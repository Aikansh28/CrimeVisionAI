@echo off
title CrimeVision AI - Launcher
echo Starting CrimeVision AI Full-Stack App...
start "CrimeVision Backend" "%~dp0start_backend.bat"
timeout /t 2 /nobreak >nul
start "CrimeVision Frontend" "%~dp0start_frontend.bat"
echo.
echo Both servers are starting up:
echo   - Backend:  http://127.0.0.1:8000
echo   - Frontend: http://localhost:5173
echo.
echo Opening browser in 3 seconds...
timeout /t 3 /nobreak >nul
start http://localhost:5173
