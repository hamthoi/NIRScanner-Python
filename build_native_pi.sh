#!/usr/bin/env bash
set -euo pipefail

# build_native_pi.sh
# Helper to build the native _NIRScanner shared object on Raspberry Pi / Linux
# Usage: ./build_native_pi.sh [python-executable]
# Example: ./build_native_pi.sh /usr/bin/python3.11

PYTHON_BIN=${1:-python3}

echo "Using Python executable: ${PYTHON_BIN}"
PY_VERSION=$(${PYTHON_BIN} -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
echo "Python version: ${PY_VERSION}"

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
SRC_DIR="$ROOT_DIR/src"
BUILD_DIR="$SRC_DIR/build_native"

mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

echo "Running CMake..."
cmake -DPYTHON_EXECUTABLE=$(which $PYTHON_BIN) ..

echo "Building..."
make -j$(nproc || echo 1)

# Find generated shared object(s) and copy to project root as _NIRScanner.so
echo "Searching for built _NIRScanner shared object files..."
LIB_PATH=$(find . -type f -name "*_NIRScanner.so*" -print -quit || true)
if [ -z "$LIB_PATH" ]; then
    # try different pattern
    LIB_PATH=$(find . -type f -name "_NIRScanner.so*" -print -quit || true)
fi

if [ -z "$LIB_PATH" ]; then
    echo "Build completed but could not find _NIRScanner shared object. Listing build dir:" >&2
    ls -la
    exit 1
fi

echo "Found built library: $LIB_PATH"
cp -v "$LIB_PATH" "$ROOT_DIR/_NIRScanner.so"

echo "Copied to $ROOT_DIR/_NIRScanner.so"
echo "Build complete. Be sure to activate your virtualenv using the same Python interpreter before running scripts."
