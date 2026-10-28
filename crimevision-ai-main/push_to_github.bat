@echo off
title CrimeVision AI - GitHub Push
cd /d "%~dp0"
echo Pushing CrimeVision AI to https://github.com/Aditya2709-mishra/crimevision-ai.git ...
echo.
git push -u origin main
echo.
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Push failed. 
    echo Make sure you have created the repository at: https://github.com/new
    echo with the name "crimevision-ai" before running this script.
) else (
    echo [SUCCESS] Successfully deployed to https://github.com/Aditya2709-mishra/crimevision-ai !
)
echo.
pause
