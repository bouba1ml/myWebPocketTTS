@echo off
set /p repo_url="Enter your GitHub Repository URL (e.g., https://github.com/username/repo.git): "

if "%repo_url%"=="" (
    echo Error: Repository URL cannot be empty.
    pause
    exit /b
)

echo.
echo Configuring remote 'origin'...
git remote remove origin 2>nul
git remote add origin %repo_url%

echo.
echo Renaming branch to 'main'...
git branch -M main

echo.
echo Pushing code to GitHub...
git push -u origin main

echo.
if %ERRORLEVEL% EQU 0 (
    echo [SUCCESS] Code pushed successfully!
) else (
    echo [ERROR] Failed to push. Check your URL and credentials.
)
pause
