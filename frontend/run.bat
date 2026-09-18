@echo off
REM Run Frontend - Hien Huu Bus
cd /d "%~dp0"

echo Installing dependencies...
call npm install

echo.
echo Starting Frontend Server...
echo App: http://localhost:5173
echo.
npm run dev
