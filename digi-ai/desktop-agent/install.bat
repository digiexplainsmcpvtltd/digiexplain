@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Digi AI - Safe Windows Installer
echo ==========================================
echo        DIGI AI - SAFE INSTALLER
echo ==========================================
echo.
echo Installer folder: %CD%
if not exist "%~dp0requirements.txt" (
  echo ERROR: requirements.txt is missing from this folder.
  echo Extract the NEW Digi AI ZIP using Extract All, then run install.bat inside:
  echo digi-ai\desktop-agent
  pause
  exit /b 1
)
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher is missing.
  echo Install Python 3.12 x64 first:
  echo https://www.python.org/downloads/release/python-31210/
  pause
  exit /b 1
)
py -3.12 --version
if errorlevel 1 (
  echo ERROR: Python 3.12 x64 is not installed.
  echo Do not use Python 3.15 for this build.
  echo Install Python 3.12 x64 from:
  echo https://www.python.org/downloads/release/python-31210/
  pause
  exit /b 1
)
echo.
echo [1/4] Removing old virtual environment...
if exist "%~dp0.venv" rmdir /s /q "%~dp0.venv"
if exist "%~dp0.venv" (
  echo ERROR: Could not remove old .venv. Close Digi AI and retry.
  pause
  exit /b 1
)
echo.
echo [2/4] Creating Python 3.12 environment...
py -3.12 -m venv "%~dp0.venv"
if errorlevel 1 goto failed
echo.
echo [3/4] Updating pip...
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
echo.
echo [4/4] Installing prebuilt packages only (no C++ compilation)...
"%~dp0.venv\Scripts\python.exe" -m pip install --only-binary=:all: -r "%~dp0requirements.txt"
if errorlevel 1 goto failed
echo.
echo ==========================================
echo DIGI AI INSTALLED SUCCESSFULLY
echo Now double-click DigiAI.bat
echo ==========================================
pause
exit /b 0
:failed
echo.
echo INSTALLATION FAILED.
echo A full log was not generated. Take a screenshot of the error above.
echo Confirm Python 3.12 x64 is installed and internet is available.
pause
exit /b 1
