@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo        DIGI AI - WINDOWS INSTALLER
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python 3.11+ was not found. Install Python from https://www.python.org/downloads/windows/
  echo Make sure "Add Python to PATH" is selected.
  pause
  exit /b 1
)
py -3 -m venv .venv
if errorlevel 1 goto failed
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Digi AI dependencies installed.
echo Double-click DigiAI.bat to start the software.
pause
exit /b 0
:failed
echo Installation failed. Check the error above and try again.
pause
exit /b 1
