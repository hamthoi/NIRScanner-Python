#!/usr/bin/env bash
set -euo pipefail

# build_native_pi.sh
# Build the Python extension _NIRScanner in one script (SWIG + compile + link)
# Usage: ./build_native_pi.sh [python-executable]
# Example: ./build_native_pi.sh /usr/bin/python3.11

PYTHON_BIN=${1:-python3}

echo "Using Python executable: ${PYTHON_BIN}"
PY_VERSION=$(${PYTHON_BIN} -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
PY_SHORT=$(${PYTHON_BIN} -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "Python version: ${PY_VERSION} (short: ${PY_SHORT})"

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
SRC_DIR="$ROOT_DIR/src"
BUILD_DIR="$SRC_DIR/build_native"

mkdir -p "$BUILD_DIR"
cd "$SRC_DIR"

# Generate SWIG wrapper if swig is available and the interface file exists
if command -v swig >/dev/null 2>&1 && [ -f "$SRC_DIR/NIRScanner.i" ]; then
    echo "Running swig to generate wrapper..."
    swig -c++ -python NIRScanner.i || true
else
    echo "swig not found or NIRScanner.i missing; skipping swig (will use existing wrapper if present)."
fi

# Determine python include dir
PY_INCDIR=$(${PYTHON_BIN} -c "import sysconfig; print(sysconfig.get_paths()['include'])")
echo "Python include dir: ${PY_INCDIR}"

# Enable nullglob so globs that don't match expand to empty
shopt -s nullglob

echo "Collecting sources in $SRC_DIR"
C_SOURCES=("$SRC_DIR"/*.c)
CPP_SOURCES=("$SRC_DIR"/*.cpp)
CXX_SOURCES=("$SRC_DIR"/*.cxx)

if [ ${#C_SOURCES[@]} -eq 0 ] && [ ${#CPP_SOURCES[@]} -eq 0 ] && [ ${#CXX_SOURCES[@]} -eq 0 ]; then
    echo "No C/C++ sources found in $SRC_DIR; aborting." >&2
    exit 1
fi

echo "Compiling sources into $BUILD_DIR"
for src in "${C_SOURCES[@]}"; do
    obj="$BUILD_DIR/$(basename "$src").o"
    echo "  gcc -fPIC -I${PY_INCDIR} -c $src -o $obj"
    gcc -fPIC -I"${PY_INCDIR}" -c "$src" -o "$obj"
done
for src in "${CPP_SOURCES[@]}"; do
    obj="$BUILD_DIR/$(basename "$src").o"
    echo "  g++ -fPIC -I${PY_INCDIR} -c $src -o $obj"
    g++ -fPIC -I"${PY_INCDIR}" -c "$src" -o "$obj"
done
for src in "${CXX_SOURCES[@]}"; do
    obj="$BUILD_DIR/$(basename "$src").o"
    echo "  g++ -fPIC -I${PY_INCDIR} -c $src -o $obj"
    g++ -fPIC -I"${PY_INCDIR}" -c "$src" -o "$obj"
done

echo "Objects in $BUILD_DIR:"
ls -1 "$BUILD_DIR"/*.o || true

# Link shared object
cd "$BUILD_DIR"
echo "Linking _NIRScanner.so"
g++ -shared *.o -ludev -o _NIRScanner.so

echo "Copying _NIRScanner.so to lib/ and project root..."
mkdir -p "$ROOT_DIR/lib"
cp -v _NIRScanner.so "$ROOT_DIR/lib/_NIRScanner.so.${PY_SHORT}" || true
cp -v _NIRScanner.so "$ROOT_DIR/_NIRScanner.so" || true

echo "Build finished. Result:"
ls -lh _NIRScanner.so || true
echo "If import issues occur, ensure you ran this script with the same Python executable used to run your scripts (provide full path to python when invoking)."
#!/usr/bin/env bash
set -euo pipefail

# build_native_pi.sh
# Build the Python extension _NIRScanner in one script (SWIG + compile + link)
# Usage: ./build_native_pi.sh [python-executable]
# Example: ./build_native_pi.sh /usr/bin/python3.11

PYTHON_BIN=${1:-python3}

echo "Using Python executable: ${PYTHON_BIN}"
PY_VERSION=$(${PYTHON_BIN} -c "import sys; print('.'.join(map(str, sys.version_info[:3])))")
PY_SHORT=$(${PYTHON_BIN} -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "Python version: ${PY_VERSION} (short: ${PY_SHORT})"

ROOT_DIR=$(cd "$(dirname "$0")" && pwd)
SRC_DIR="$ROOT_DIR/src"
BUILD_DIR="$SRC_DIR/build_native"

mkdir -p "$BUILD_DIR"
cd "$SRC_DIR"

# Generate SWIG wrapper if swig is available and the interface file exists
if command -v swig >/dev/null 2>&1 && [ -f "$SRC_DIR/NIRScanner.i" ]; then
    echo "Running swig to generate wrapper..."
    swig -c++ -python NIRScanner.i || true
else
    echo "swig not found or NIRScanner.i missing; skipping swig (will use existing wrapper if present)."
fi

# Determine python include dir
PY_INCDIR=$(${PYTHON_BIN} -c "import sysconfig; print(sysconfig.get_paths()['include'])")
echo "Python include dir: ${PY_INCDIR}"

echo "Compiling C sources..."
gcc -fPIC -I"${PY_INCDIR}" -c ./*.c || true
echo "Compiling C++ sources..."
g++ -fPIC -I"${PY_INCDIR}" -c ./*.cpp || true
echo "Compiling CXX sources (wrapper)..."
g++ -fPIC -I"${PY_INCDIR}" -c ./*.cxx 2>/dev/null || true

mv ./*.o "$BUILD_DIR/" || true

# Try to detect python library name (attempt common variants)
LINK_PYLIB="python${PY_SHORT}m"
if ! ldconfig -p 2>/dev/null | grep -q "lib${LINK_PYLIB}"; then
    LINK_PYLIB="python${PY_SHORT}"
    if ! ldconfig -p 2>/dev/null | grep -q "lib${LINK_PYLIB}"; then
        # fallback: don't explicitly link libpython (may still work)
        echo "Could not detect libpython for ${PY_SHORT}, will link without -lpython..."
        LINK_PYLIB=""
    else
        echo "Using python lib: ${LINK_PYLIB}"
    fi
else
    echo "Using python lib: ${LINK_PYLIB}"
fi

cd "$BUILD_DIR"
echo "Linking shared object..."
if [ -n "${LINK_PYLIB}" ]; then
    g++ -shared *.o -ludev -l${LINK_PYLIB} -o _NIRScanner.so
else
    g++ -shared *.o -ludev -o _NIRScanner.so
fi

echo "Copying _NIRScanner.so to lib/ and project root..."
mkdir -p "$ROOT_DIR/lib"
cp -v _NIRScanner.so "$ROOT_DIR/lib/_NIRScanner.so.${PY_SHORT}" || true
cp -v _NIRScanner.so "$ROOT_DIR/_NIRScanner.so" || true

echo "Build finished. Result:"
ls -lh _NIRScanner.so || true
echo "If import issues occur, ensure you ran this script with the same Python executable used to run your scripts (provide full path to python when invoking)."
