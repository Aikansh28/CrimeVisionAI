@echo off
title CrimeVision AI - Backend Server
cd /d "%~dp0backend"
echo Starting CrimeVision AI Backend on http://127.0.0.1:8000 ...
python run.py
pause
