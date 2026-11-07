@echo off
cd /d "%~dp0"
if not exist "runtime\Scripts\python.exe" (
  echo First run: installing the Python environment...
  call setup.bat
  if errorlevel 1 exit /b 1
)
echo Stopping the local-only server if it is running...
"runtime\Scripts\python.exe" "tools\shutdown.py" >nul 2>nul
timeout /t 3 /nobreak >nul
echo Starting LAN mode. Open the printed address on your tablet.
start "" "%~dp0runtime\Scripts\pythonw.exe" "%~dp0server.py" --lan
exit /b 0
