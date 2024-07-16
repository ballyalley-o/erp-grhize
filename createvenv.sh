#!/bin/bash

echo "deleting existing virtual environment...."
rm -rf erpvenv
rm -rf dist
rm -rf build
rm -rf __pycache__

echo "creating virtual environment, please wait..."
python3 -m venv erpvenv

echo "activating virtual environment...."
source erpvenv/bin/activate

echo "upgrading pip and installing dependencies...."
pip install --upgrade pip
pip install pyinstaller matplotlib

pip install --no-binary :all: matplotlib kiwisolver
echo "installing dependencies, please wait..."

file erpvenv/lib/python3.12/site-packages/kiwisolver/_cext.cpython-312-darwin.so

echo "packaging binary / executable file...."
pyinstaller --onefile --windowed --noupx --clean --log-level=WARN  erp-vis.py


echo "deactivating virtual environment...."
deactivate