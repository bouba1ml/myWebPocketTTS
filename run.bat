@echo off
echo ==========================================
echo Starting WebPocketTTS...
echo ==========================================

echo Checking for existing server on port 8543...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8543" ^| find "LISTENING"') do (
    echo Found process %%a using port 8543. Killing it...
    taskkill /f /pid %%a >nul 2>&1
)

echo.
echo Starting Backend Server...
:: Open browser immediately (it might fail if server isn't ready instantly, but refresh works)
start "" "http://localhost:8543"
python app.py

pause
