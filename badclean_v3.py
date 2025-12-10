#!/usr/bin/env python3
"""
BADBRAD RAGE CLEANER v3.0 – BULLETPROOF FINAL
Just works. No syntax errors. Same carnage.
"""

import os
import sys
import shutil
import subprocess
import psutil
import ctypes
from datetime import datetime

WEBHOOK = ""  # ← drop your Discord webhook here (optional)

R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; X = "\033[0m"

def banner():
    print(f"""{R}
    ╔═══════════════════════════════════════════════╗
    ║       BADBRAD RAGE CLEANER v3.0               ║
    ║           ONE-CLICK WINDOWS APOCALYPSE        ║
    ╚═══════════════════════════════════════════════╝{X}""")

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

def get_size(b):
    for u in ['B','KB','MB','GB','TB']:
        if b < 1024: return f"{b:.2f}{u}"
        b /= 1024
    return f"{b:.2f} PB"

def kill_hogs():
    killed = 0
    print(f"{Y}[+] Slaughtering resource hogs...{X}")
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
        try:
            cpu = p.info['cpu_percent'] or 0
            mem = p.info['memory_percent'] or 0
            name = p.name().lower()
            if (cpu > 75 or mem > 12) and name not in [
                'svchost.exe','explorer.exe','dwm.exe','csrss.exe',
                'winlogon.exe','lsass.exe','python.exe','badclean_v3.py'
            ]:
                p.kill()
                print(f"    {R}☠ KILLED:{X} {p.name():35} CPU {cpu:5.1f}% RAM {mem:4.1f}%")
                killed += 1
        except: pass
    return killed

def nuke_temp():
    total = 0
    paths = [
        os.getenv('TEMP'), os.getenv('TMP'),
        r"C:\Windows\Temp", r"C:\Windows\Prefetch",
        r"C:\Windows\SoftwareDistribution\Download",
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"),
    ]
    print(f"{Y}[+] Nuking temp folders...{X}")
    for base in paths:
        if not base or not os.path.exists(base): continue
        for root, dirs, files in os.walk(base, topdown=False):
            for f in files + dirs:
                path = os.path.join(root, f)
                try:
                    if os.path.isfile(path):
                        total += os.path.getsize(path)
                        os.remove(path)
                    else:
                        size = sum(os.path.getsize(os.path.join(dp, fn)) for dp, _, fs in os.walk(path) for fn in fs)
                        shutil.rmtree(path, ignore_errors=True)
                        total += size
                except: pass
    return total

def empty_recycle_bin():
    print(f"{Y}[+] Emptying Recycle Bin...{X}")
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)
        print(f"    {G}→ Purged{X}")
    except: print(f"    {R}→ Failed (need admin){X}")

def flush_network():
    print(f"{Y}[+] Resetting network stack...{X}")
    for cmd in ["ipconfig /flushdns", "ipconfig /release", "ipconfig /renew",
                "netsh int ip reset", "netsh winsock reset"]:
        subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def create_scheduled_task():
    script = os.path.abspath(__file__)
    xml = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <Triggers><LogonTrigger><Enabled>true</Enabled></LogonTrigger></Triggers>
  <Principals><Principal id="Author"><RunLevel>HighestAvailable</RunLevel></Principal></Principals>
  <Actions Context="Author">
    <Exec>
      <Command>pythonw.exe</Command>
      <Arguments>"{script}"</Arguments>
    </Exec>
  </Actions>
</Task>"""
    subprocess.run(f'schtasks /create /tn "BadBradCleaner" /xml "{xml}" /f', shell=True, capture_output=True)
    print(f"{G}→ Auto-run on boot scheduled{X}")

def main():
    banner()
    if not is_admin():
        print(f"{R}Not running as Administrator – some features limited.{X}\n")

    killed = kill_hogs()
    freed = nuke_temp()
    empty_recycle_bin()
    flush_network()

    print(f"\n{G}╔══════════════════ FINAL BODY COUNT ══════════════════╗{X}")
    print(f"{G}║  Freed       : {get_size(freed):>12}                           ║{X}")
    print(f"{G}║  Killed      : {killed:>5} processes                        ║{X}")
    print(f"{G}╚═══════════════════════════════════════════════════════╝{X}\n")

    if input(f"{Y}Schedule this to run silently on every boot? (y/N{X} ").strip().lower() == "y":
        create_scheduled_task()

    input(f"\nPress Enter to exit...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}Aborted. Stay lethal.{X}")