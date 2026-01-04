@echo off
echo ======================================
echo Git Auto-Push Script
echo ======================================
echo.

REM Check if there are changes
git status

echo.
echo ======================================
set /p commit_msg="Enter commit message: "

if "%commit_msg%"=="" (
    echo Error: Commit message cannot be empty!
    pause
    exit
)

echo.
echo Adding changes...
git add .

echo.
echo Committing...
git commit -m "%commit_msg%"

echo.
echo Pushing to GitHub...
git push

echo.
echo ======================================
echo Done! Changes pushed to GitHub.
echo ======================================
pause