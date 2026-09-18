@echo off
REM Run Backend - Hien Huu Bus
cd /d "%~dp0"

REM Activate venv
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo ERROR: Virtual environment not found!
    echo Run: python -m venv venv
    pause
    exit /b 1
)

REM Run seed data (first time only - comment out after)
python seed_data.py

echo.
echo Starting Backend Server...
echo API: http://localhost:8000
echo Docs: http://localhost:8000/docs
echo.
uvicorn main:app --reload --port 8000 --host 0.0.0.0
