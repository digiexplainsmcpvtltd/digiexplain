@echo off
setlocal
cd /d "%~dp0"
echo ==========================================
echo        DIGI AI - WINDOWS INSTALLER
echo ==========================================
where py >nul 2>nul
if errorlevel 1 (
  echo Python Launcher was not found.
  echo Install Python 3.12 x64 from https://www.python.org/downloads/release/python-31210/
  echo Then run this installer again.
  pause
  exit /b 1
)
py -3.12 --version >nul 2>nul
if errorlevel 1 (
  echo Python 3.12 was not found.
  echo Please install Python 3.12 x64 from:
  echo https://www.python.org/downloads/release/python-31210/
  echo During setup, enable the Python Launcher option.
  pause
  exit /b 1
)
if exist ".venv" (
  echo Removing the previous virtual environment...
  rmdir /s /q ".venv"
)
py -3.12 -m venv .venv
if errorlevel 1 goto failed
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip
if errorlevel 1 goto failed
python -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo.
echo Digi AI dependencies installed successfully.
echo Double-click DigiAI.bat to start the software.
pause
exit /b 0
:failed
echo.
echo Installation failed. Check the error above and try again.
pause
exit /b 1
