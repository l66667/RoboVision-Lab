@echo off
cd /d "%~dp0"
echo.
echo  RoboVision Lab - environment setup
echo  =================================
echo.

where py >nul 2>nul
if %errorlevel%==0 (
  set "PY=py -3"
) else (
  set "PY=python"
)

%PY% --version
if errorlevel 1 (
  echo.
  echo Python was not found. Install Python 3.10+ and enable "Add to PATH".
  pause
  exit /b 1
)

if not exist "runtime\Scripts\python.exe" (
  echo Creating the isolated runtime...
  %PY% -m venv runtime
  if errorlevel 1 (
    echo Failed to create the virtual environment.
    pause
    exit /b 1
  )
)

echo Installing OpenCV and NumPy...
"runtime\Scripts\python.exe" -m pip install --upgrade pip
"runtime\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
  echo.
  echo Installation failed. Check the network and try Python 3.10-3.13.
  pause
  exit /b 1
)

"runtime\Scripts\python.exe" -c "import cv2, numpy, sys; print('OK - Python', sys.version.split()[0], '| OpenCV', cv2.__version__, '| NumPy', numpy.__version__)"
echo.
echo Done. Double-click start.bat (or the desktop shortcut) to start.
pause
