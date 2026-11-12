@echo off
setlocal
cd /d "%~dp0"
if not exist "%~dp0.venv\Scripts\pythonw.exe" (
  echo Digi AI is not installed. Run install.bat first.
  pause
  exit /b 1
)
"%~dp0.venv\Scripts\pythonw.exe" "%~dp0desktop_app.py"
if errorlevel 1 (
  "%~dp0.venv\Scripts\python.exe" "%~dp0desktop_app.py"
)
