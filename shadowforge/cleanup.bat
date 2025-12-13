@echo off
echo [ShadowForge] Executing post-session purge...

:: Kill Brave/Tor processes cleanly
taskkill /F /IM brave.exe /T >nul 2>&1

:: Clear Brave cache, history, cookies (all profiles)
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cache"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Code Cache"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\GPUCache"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Cookies*"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\History*"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Web Data*"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Session Storage"
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Local Storage"

:: Clear Tor-specific artifacts (Brave Tor tabs use isolated profile)
rmdir /s /q "%LOCALAPPDATA%\BraveSoftware\Brave-Browser\User Data\Default\Tor"

:: System temp files
del /q/f/s %TEMP%\*
del /q/f/s C:\Windows\Temp\* 

:: Flush DNS (removes any recon residue)
ipconfig /flushdns >nul

:: Optional: Clear recent files/jumplists
del /q/f "%APPDATA%\Microsoft\Windows\Recent\*"
reg delete "HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\RunMRU" /va /f >nul 2>&1

echo [ShadowForge] Purge complete. Rig is clean. Enjoy your evening.
timeout /t 3 >nul