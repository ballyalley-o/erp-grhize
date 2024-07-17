#!/bin/bash

cd "$(dirname "$0")"

pyinstaller --onefile --windowed erp-vis.py

cp dist/erp-vis.exe ~/Desktop/erp-vis.exe

echo "Packaging complete! The .exe is on your desktop."