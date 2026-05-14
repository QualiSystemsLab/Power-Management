#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo
echo "Cleaning distribution folder"
rm -rf dist

echo
echo "Updating dependencies"
python3 -m pip install --upgrade setuptools wheel twine

echo
echo "Building package"
python3 setup.py sdist bdist_wheel

echo
echo "Uploading to PyPI"
python3 -m twine upload dist/*

echo
echo "Complete!"
