@echo off
REM Vibecraft Global Launcher
REM 
REM This script runs vibecraft without requiring PATH modification.
REM It uses the Python launcher (py) to execute vibecraft as a module.
REM
REM Requirements:
REM   - Python 3.10+ installed with py launcher
REM   - vibecraft package installed (pip install vibecraft)
REM
REM Usage:
REM   vibecraft.bat [command] [options]
REM
REM Examples:
REM   vibecraft.bat --help
REM   vibecraft.bat doctor
REM   vibecraft.bat init -r research.md -s stack.md
REM

REM Find Python using py launcher (works with all Python installations)
py -c "import vibecraft" >nul 2>&1
if %errorlevel% neq 0 (
    echo Vibecraft is not installed.
    echo.
    echo Install with one of these options:
    echo   Option 1: Global install (requires admin)
    echo     cd vibecraft-framework
    echo     python install.py
    echo.
    echo   Option 2: Local install (no admin required)
    echo     cd your-project
    echo     python vibecraft-framework\install-to-project.py
    echo.
    echo   Option 3: Manual install
    echo     pip install vibecraft
    echo.
    exit /b 1
)

REM Run vibecraft as a module
py -m vibecraft %*
