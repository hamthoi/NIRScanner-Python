#!/usr/bin/env bash
# prune_unused.sh
# Remove demo/test files that are not needed for minimal scanning on Raspberry Pi.
# Run this on the Pi from the project root if you want to permanently remove demo files.

set -euo pipefail

SRCDIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SRCDIR"

declare -a REMOVE=(
  "testAll.py"
  "testLCD.py"
  "testNewLcd.py"
  "test.py"
  "testNIR.py"
  "testplot.py"
  "test.ipynb"
  "client.py"
  "pls_model.pkl"
)

echo "This will permanently delete the following files from $SRCDIR:" 
for f in "${REMOVE[@]}"; do
  echo "  - $f"
done

read -p "Proceed? [y/N] " yn
case "$yn" in
  [Yy]*)
    for f in "${REMOVE[@]}"; do
      if [ -e "$f" ]; then
        rm -v "$f"
      fi
    done
    echo "Prune complete." ;;
  *)
    echo "Aborted." ;;
esac
