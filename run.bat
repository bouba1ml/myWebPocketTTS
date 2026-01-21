@echo off
echo ==========================================
echo Starting WebPocketTTS...
echo ==========================================

:: Open browser immediately (it might fail if server isn't ready instantly, but refresh works)
start http://localhost:8000

echo Starting Backend Server...
python app.py

pause
