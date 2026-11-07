@echo off
cd /d "%~dp0"
if exist "runtime\Scripts\python.exe" (
  "runtime\Scripts\python.exe" "tools\shutdown.py"
) else (
  echo Runtime not found; the server may already be stopped.
)
