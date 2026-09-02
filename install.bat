@echo off
echo ========================================
echo        vault-connect-bot installer
echo ========================================
echo.

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found.
    echo Please install Python 3.11 from https://www.python.org/downloads/release/python-3119/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

echo [INFO] Checking Python version...
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYVER=%%i
echo [INFO] Found Python %PYVER%

echo.
echo [1/2] Installing dependencies...
pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install dependencies.
    echo Make sure you have Python 3.11 installed: https://www.python.org/downloads/release/python-3119/
    pause
    exit /b 1
)

echo.
echo [2/2] Done! Fill in config\settings.py then run run.bat
echo.
pause
