@echo off
title Cosmic Engine Launcher
color 0A
echo =========================================
echo    🚀 COSMIC ENGINE LAUNCHER 🌌
echo    Choose Your 3D Engine
echo =========================================
echo.
echo Available Engines:
echo   • Ursina Simple - Fast & Easy
echo   • Ursina Enhanced - Better Graphics  
echo   • Panda3D Advanced - Photorealistic
echo   • Three.js Web - Browser-Based
echo.

cd /d "%~dp0"

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH!
    echo Please install Python 3.8+ from python.org
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo ✓ Activating virtual environment...
    call venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ⚠ Virtual environment not found. Using system Python.
    echo   Consider creating a venv: python -m venv venv
)

echo.
echo ✓ Launching engine selection interface...
python desktop_app\cosmic_engine_launcher.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ ERROR: Failed to launch engine launcher!
    echo.
    echo Troubleshooting steps:
    echo 1. Make sure Python 3.8+ is installed
    echo 2. Install required packages: pip install tkinter
    echo 3. Check that desktop_app\cosmic_engine_launcher.py exists
    echo.
    echo Press any key to exit...
    pause >nul
) else (
    echo.
    echo ✓ Engine launcher closed successfully
)
