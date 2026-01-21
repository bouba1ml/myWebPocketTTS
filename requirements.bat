@echo off
echo ==========================================
echo Installing WebPocketTTS Dependencies...
echo ==========================================

pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Failed to install dependencies. Please check your Python/Pip installation.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo [SUCCESS] All dependencies installed successfully!
echo You can now run the app using run.bat
echo.
pause
