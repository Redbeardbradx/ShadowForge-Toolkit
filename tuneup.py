# tuneup.py — Instant drop-in ShadowForge module (no external repo needed)
# Save this exact file to E:\ShadowForge-Toolkit\tuneup.py and run.

import os, subprocess, sys, ctypes, time
from pathlib import Path

def is_admin(): return ctypes.windll.shell32.IsUserAnAdmin()

def run(cmd): subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

if not is_admin():
    print("[!] Re-launching as Administrator...")
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{__file__}"', None, 1)
    sys.exit(0)

print("""
╔══════════════════════════════════════════╗
║   ShadowForge — PornReady TuneUp v1.0    ║
║       Making your rig scream in 4K       ║
╚══════════════════════════════════════════╝
""")

# Temp folders
for folder in ["%TEMP%", "C:\\Windows\\Temp", "C:\\Windows\\Prefetch"]:
    run(f'rd /s /q "{os.path.expandvars(folder)}" 2>nul || del /f /s /q "{os.path.expandvars(folder)}\\*.*" 2>nul')

# Bloat apps
bloat = ["xbox","bingweather","zunemusic","solitaire","candycrush","twitter","spotify","disney"]
for app in bloat:
    run(f'powershell -c "Get-AppxPackage *{app}* | Remove-AppxPackage" 2>nul')

# Network reset
for cmd in ["ipconfig /flushdns", "ipconfig /release", "ipconfig /renew", "netsh winsock reset"]:
    run(cmd)

# Ultimate Performance
run('powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 2>nul')
run('powercfg -setactive e9a42b02-d5df-448d-aa00-03f14749eb61')

# Browser caches (Chrome/Edge/Brave/Firefox)
caches = [
    os.path.expandvars(r"%LocalAppData%\Google\Chrome\User Data\Default\Cache"),
    os.path.expandvars(r"%LocalAppData%\Microsoft\Edge\User Data\Default\Cache"),
    os.path.expandvars(r"%LocalAppData%\BraveSoftware\Brave-Browser\User Data\Default\Cache"),
    os.path.expandvars(r"%AppData%\Mozilla\Firefox\Profiles")
]
for path in caches:
    if Path(path).exists():
        run(f'rd /s /q "{path}" 2>nul')

print("[+] Cleanup complete. Rebooting in 10 seconds (Ctrl+C to cancel)...")
time.sleep(10)
run("shutdown /r /t 0")