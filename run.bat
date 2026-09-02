@echo off
echo ========================================
echo         vault-connect-bot launcher
echo ========================================
echo.

python --version >nul 2>&1
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python not found. Run install.bat first.
    pause
    exit /b 1
)

echo Starting bot... Press Ctrl+C to stop.
echo.
python bot.py

pause
