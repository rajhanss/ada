@echo off
title ADA Cloud Backend
echo ===================================================
echo Starting ADA Cloud Backend on http://localhost:8000
echo ===================================================
cd /d C:\Projects\ADA\backend
C:\Projects\Arcane\.venv\Scripts\python.exe -m uvicorn ada.main:app --host 0.0.0.0 --port 8000 --reload
pause
