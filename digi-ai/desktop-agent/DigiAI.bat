@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\pythonw.exe" (
  echo Please run install.bat first.
  pause
  exit /b 1
)
".venv\Scripts\pythonw.exe" desktop_app.py
if errorlevel 1 (
  ".venv\Scripts\python.exe" desktop_app.py
)
