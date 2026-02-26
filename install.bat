@echo off
REM Vibecraft Installer for Windows
REM 
REM This script installs vibecraft and configures PATH automatically.
REM
REM Usage: Double-click this file or run: install.bat

echo ============================================================
echo   Vibecraft Installer (Windows)
echo ============================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

echo Installing vibecraft...
echo.

REM Run the Python installer
python "%~dp0install.py"

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed
    pause
    exit /b 1
)

echo.
echo ============================================================
echo   Installation Complete!
echo ============================================================
echo.
echo IMPORTANT: Please RESTART your terminal for changes to take effect.
echo After restarting, you can run 'vibecraft' from anywhere!
echo.
pause
