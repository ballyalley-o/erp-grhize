#!/bin/bash

echo "deleting existing build...."

rm -rf dist
rm -rf build

echo "Activating virtual environment...."

source erpvenv/bin/activate

echo "packaging binary / executable file...."
pyinstaller erp-vis.spec

echo "deactivating virtual environment...."
deactivate