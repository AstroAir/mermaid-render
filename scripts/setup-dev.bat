@echo off
REM Development environment setup script for Windows
REM This is a Windows batch file equivalent of setup-dev.py

setlocal enabledelayedexpansion

echo.
echo ========================================
echo Mermaid Render Development Setup
echo ========================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://python.org
    pause
    exit /b 1
)

echo [INFO] Python found
python --version

REM Check Python version
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python version: %PYTHON_VERSION%

REM Change to project root
cd /d "%~dp0\.."

REM Run the Python setup script
echo [INFO] Running Python setup script...
python scripts/setup-dev.py %*

if errorlevel 1 (
    echo [ERROR] Setup failed
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Setup completed successfully!
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate
echo.
echo Then you can use:
echo   python scripts/dev.py --help
echo   make help
echo.

pause
