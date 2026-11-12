@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title Digi AI - Python 3.15 Installer
echo ==========================================
echo       DIGI AI - SIMPLE INSTALLER
echo ==========================================
echo.
if not exist "%~dp0requirements.txt" (
  echo ERROR: requirements.txt missing. Extract the ZIP first.
  pause
  exit /b 1
)
where py >nul 2>nul
if errorlevel 1 (
  echo ERROR: Python Launcher not found.
  echo Please repair your existing Python 3.15 installation.
  pause
  exit /b 1
)
py -3.15 --version
if errorlevel 1 (
  echo ERROR: Python 3.15 was not found by the Windows Python Launcher.
  echo Open CMD and run: py --list
  pause
  exit /b 1
)
echo.
echo [1/3] Preparing Python 3.15 environment...
if exist "%~dp0.venv" rmdir /s /q "%~dp0.venv"
py -3.15 -m venv "%~dp0.venv"
if errorlevel 1 goto failed
echo.
echo [2/3] Updating pip...
"%~dp0.venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto failed
echo.
echo [3/3] Installing Digi AI packages...
"%~dp0.venv\Scripts\python.exe" -m pip install -r "%~dp0requirements.txt"
if errorlevel 1 goto failed
echo.
echo ==========================================
echo       DIGI AI INSTALLATION COMPLETE
echo       Now open DigiAI.bat
echo ==========================================
pause
exit /b 0
:failed
echo.
echo INSTALLATION FAILED.
echo Please send a screenshot of the FIRST red error line above.
pause
exit /b 1
