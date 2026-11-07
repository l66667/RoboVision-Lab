# -*- coding: utf-8 -*-
"""Write ASCII + CRLF launchers so cmd.exe never mis-parses Chinese bytes."""

import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

START = r"""@echo off
cd /d "%~dp0"
if not exist "runtime\Scripts\python.exe" (
  echo First run: installing the Python environment...
  call setup.bat
  if errorlevel 1 exit /b 1
)
start "" "%~dp0runtime\Scripts\pythonw.exe" "%~dp0server.py"
exit /b 0
"""

SETUP = r"""@echo off
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
"""

STOP = r"""@echo off
cd /d "%~dp0"
if exist "runtime\Scripts\python.exe" (
  "runtime\Scripts\python.exe" "tools\shutdown.py"
) else (
  echo Runtime not found; the server may already be stopped.
)
"""

START_TABLET = r"""@echo off
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
"""

ALLOW_FIREWALL = r"""@echo off
cd /d "%~dp0"
net session >nul 2>&1
if not %errorlevel%==0 (
  powershell -NoProfile -Command "Start-Process -Verb RunAs -FilePath '%~f0'"
  exit /b
)
echo Adding a firewall rule for ports 8770-8789, limited to the local subnet...
echo WARNING: this also allows the ports on public networks. Only use on trusted Wi-Fi.
netsh advfirewall firewall delete rule name="RoboVision Lab" >nul 2>nul
netsh advfirewall firewall add rule name="RoboVision Lab" dir=in action=allow protocol=TCP localport=8770-8789 remoteip=LocalSubnet profile=any
echo.
echo Done. Restart start_tablet.bat, then open the address shown in the app.
pause
"""

for name, text in (
    ("start.bat", START),
    ("start_tablet.bat", START_TABLET),
    ("allow_tablet_firewall.bat", ALLOW_FIREWALL),
    ("setup.bat", SETUP),
    ("stop.bat", STOP),
):
    path = os.path.join(ROOT, name)
    with open(path, "w", encoding="ascii", newline="\r\n") as handle:
        handle.write(text)
    print("wrote", path)

for name in ("启动学习软件.bat", "停止学习软件.bat"):
    path = os.path.join(ROOT, name)
    if os.path.isfile(path):
        os.remove(path)
        print("removed", path)
