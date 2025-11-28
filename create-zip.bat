@echo off
REM Batch script to create project zip
REM This will run the PowerShell script

echo Creating Matrimony HR AI project zip file...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0create-zip.ps1"

echo.
echo Done! Press any key to exit...
pause >nul
