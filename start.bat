@echo off
cd /d "%~dp0"
if not exist "runtime\Scripts\python.exe" (
  echo First run: installing the Python environment...
  call setup.bat
  if errorlevel 1 exit /b 1
)
start "" "%~dp0runtime\Scripts\pythonw.exe" "%~dp0server.py"
exit /b 0
