@echo off
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
