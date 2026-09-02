@echo off
echo ========================================
echo        vault-connect-bot installer
echo ========================================
echo.

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/2] Python found. Installing dependencies...
pip install -r requirements.txt

IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo.
echo [2/2] Done! Fill in config\settings.py then run run.bat
echo.
pause
