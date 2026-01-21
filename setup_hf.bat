@echo off
echo ==========================================
echo Setting up Hugging Face Authentication
echo ==========================================
echo.
echo Step 1: Please ensure you have accepted the terms at:
echo https://huggingface.co/kyutai/pocket-tts
echo.
echo Step 2: Generate a User Access Token (Read) at:
echo https://huggingface.co/settings/tokens
echo.
echo Step 3: Copy your token (starts with hf_...)
echo.

set /p token="Paste your HF Token here: "

if "%token%"=="" (
    echo Error: Token cannot be empty.
    pause
    exit /b
)

echo.
echo Saving token to .env...
findstr /v "HF_TOKEN" .env > .env.tmp 2>nul
echo HF_TOKEN=%token%>> .env.tmp
move /y .env.tmp .env >nul

echo.
echo Installing huggingface_hub...
python -m pip install huggingface_hub

echo.
echo Creating login script...
(
echo from huggingface_hub import login
echo try:
echo     login(token='%token%', add_to_git_credential=True^)
echo     print("[SUCCESS] Logged in via Python API!"^)
echo except Exception as e:
echo     print(f"[ERROR] Failed to login: {e}"^)
echo     exit(1^)
) > hf_login_temp.py

echo.
echo Running login...
python hf_login_temp.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Login failed.
) else (
    echo.
    echo [SUCCESS] Authentication complete!
    echo Token saved to .env and global cache.
)

del hf_login_temp.py
echo.
echo You can now restart the WebPocketTTS app.
pause
