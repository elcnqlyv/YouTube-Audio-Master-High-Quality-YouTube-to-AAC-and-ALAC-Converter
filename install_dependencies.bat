@echo off
REM YouTube Audio Master - Automated Installation Script for Windows
REM This script installs Python, FFmpeg, and required Python dependencies

setlocal enabledelayedexpansion

echo.
echo ========================================
echo YouTube Audio Master - Setup Wizard
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing Python...
    REM Download and install Python (using chocolatey or scoop if available)
    choco install python -y >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        scoop install python -y >nul 2>&1
    )
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Could not install Python. Please install Python manually from https://www.python.org
        pause
        exit /b 1
    )
) else (
    echo Python is already installed
)

REM Check if FFmpeg is installed
ffmpeg -version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Installing FFmpeg...
    REM Download and install FFmpeg using chocolatey
    choco install ffmpeg -y >nul 2>&1
    if %ERRORLEVEL% NEQ 0 (
        REM Try scoop as alternative
        scoop install ffmpeg -y >nul 2>&1
    )
    if %ERRORLEVEL% NEQ 0 (
        echo Error: Could not install FFmpeg. Please install FFmpeg manually from https://ffmpeg.org/download.html
        pause
        exit /b 1
    )
) else (
    echo FFmpeg is already installed
)

REM Install Python dependencies
echo.
echo Installing Python dependencies...
pip install -r requirements_desktop.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install Python dependencies
    pause
    exit /b 1
)
echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo You can now run the application:
echo python desktop_app.py
echo.
pause