@echo off
REM ins Projektverzeichnis wechseln
cd /d "%~dp0"
REM Server starten
py -m uvicorn backend.verify_api:app --reload --host 127.0.0.1 --port 8000
