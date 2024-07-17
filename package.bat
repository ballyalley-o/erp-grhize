@echo off
cd %~dp0

pyinstaller --onefile --windowed erp-vis.py

copy dist\erp-vis.exe %USERPROFILE%\Desktop\erp-vis.exe

echo Packaging complete! The .exe is on your desktop.
pause