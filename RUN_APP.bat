@echo off
REM SnapScribe - Launch Application
REM This script starts the Streamlit app for SnapScribe

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║                     SnapScribe OCR App                         ║
echo ║                   Launching Streamlit App                      ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\python.exe" (
    echo ❌ Error: Virtual environment not found!
    echo.
    echo Please make sure you are in the SnapScribe project directory:
    echo    E:\PROJECTS\SnapScribe
    echo.
    pause
    exit /b 1
)

echo ✅ Virtual environment found
echo ✅ Starting Streamlit application...
echo.
echo The app will open at: http://localhost:8501
echo.
echo To stop the app, press Ctrl+C
echo.

REM Launch the app
venv\Scripts\python -m streamlit run app.py

pause
