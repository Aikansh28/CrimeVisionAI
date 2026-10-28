@echo off
title CrimeVision AI - Streamlit Dashboard
cd /d "%~dp0"
echo Starting CrimeVision AI on Streamlit ...
python -m streamlit run streamlit_app.py
pause
