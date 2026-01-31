@echo off
:: =====================================================
:: Multi-instance Launcher Script
:: Function: Launch 12 instances of Chess98
:: Author: User Custom
:: Version: 1.0
:: =====================================================

:: Display usage instructions
:show_help
echo.
echo =====================================================
echo         Chess98 Multi-instance Launcher
echo =====================================================
echo This script will launch many instances of Chess98.
echo.
echo Usage:
echo   1. Double-click to run this batch file
echo   2. Or right-click and select "Run as administrator"
echo.
echo Notes:
echo   - Ensure the Chess98.exe path is correct
echo   - Running multiple instances consumes significant system resources
echo   - 1-second interval between launches to prevent system lag
echo   - Script automatically switches to its own directory
echo.
echo Configuration:
echo   Program Path: E:\Projects_chess\Chess98\x64\Release\Chess98.exe
echo.
echo Press any key to start... (Press Ctrl+C to cancel)
echo =====================================================
echo.
pause >nul

:: Change to the batch file's directory
cd /d %~dp0

echo.
echo Launching Chess98 instances...

:: Launch many program instances
for /L %%i in (1,1,12) do (
    echo Launching instance %%i...
    start "" "E:\Projects_chess\Chess98\x64\Release\Chess98.exe"
    timeout /t 1 >nul
)

echo.
echo All instances have been launched!
echo.
pause