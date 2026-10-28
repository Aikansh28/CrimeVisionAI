@echo off
title CrimeVision AI - Frontend Server
set "PATH=C:\Program Files\nodejs;%PATH%"
cd /d "%~dp0frontend"
echo Starting CrimeVision AI Frontend on http://localhost:5173 ...
call npm run dev
pause
