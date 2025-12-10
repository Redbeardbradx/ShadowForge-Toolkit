#!/usr/bin/env python3
"""
BADBRAD RAGE CLEANER v2.0
Windows nuclear option – everything dies, everything flies.
"""

import os
import sys
import shutil
import platform
import subprocess
import psutil
import ctypes
from datetime import datetime

# Colors
R = "\033[91m"; G = "\033[92m"; Y = "\033[93m"; C = "\033[96m"; M = "\033[95m"; X = "\033[0m"

def banner():
    print(f"""{R}
    ╔══════════════════════════════════════════════════╗
    ║         BADBRAD RAGE CLEANER v2.0                ║
    ║       Windows Nuclear Cleanup – No Survivors     ║
    ╚══════════════════════════════════════════════════╝{X}
    """)

def is_admin():
    return ctypes.windll.shell32.IsUserAnAdmin() != 0

def get_size(b):
    for u in ['B','KB','MB','GB','TB']: 
        if b < 1024: return f"{b:.2f}{u}"
        b /= 1024

def kill_hogs():
    print(f"{Y}[+] Executing resource criminals...{X}")
    killed = 0
    for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
        try:
            cpu = p.info['cpu_percent'] or 0
            mem = p.info['memory_percent'] or 0
            name = p.name().lower()
            if (cpu > 75 or mem > 12) and name not in [
                'svchost.exe','explorer.exe','dwm.exe','csrss.exe',
                'winlogon.exe','lsass.exe','python.exe','badclean.py'
            ]:
                p.kill()
                print(f"    {R}☠  EXECUTED:{X} {p.name():30} CPU {cpu:5.1f}% RAM {mem:4.1f}%")
                killed += 1
        except: pass
    print(f"    {G}→ {killed} bodies dropped.{X}")

def nuke_all_temp():
    print(f"{Y}[+] Annihilating every temp folder known to man...{X}")
    paths = [
        os.getenv('TEMP'), os.getenv('TMP'),
        r"C:\Windows\Temp", r"C:\Windows\Prefetch",
        r"C:\Windows\SoftwareDistribution\Download",
        os.path.expandvars(r"%LOCALAPPDATA%\Temp"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\INetCache"),
        os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Explorer\thumbcache_*.db"),
        os.path.expandvars(r"%USERPROFILE%\Recent"),
    ]
    total = 0
    for p in paths:
        if not p or not os.path.exists(p): continue
        for root, dirs, files in os.walk(p, topdown=False):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    s = os.path.getsize(fp)
                    os.remove(fp)
                    total += s
                except: pass
            for d in dirs:
                dp = os.path.join(root, d)
                try:
                    s = sum(os.path.getsize(os.path.join(dirpath, f)) 
                            for dirpath,_,fs in os.walk(dp) for f in fs)
                    shutil.rmtree(dp, ignore_errors=True)
                    total += s
                except: pass
    print(f"    {G}→ {get_size(total)} of trash incinerated.{X}")

def empty_recycle_bin():
    print(f"{Y}[+] Emptying Recycle Bin...{X}")
    try:
        ctypes.windll.shell32.SHEmptyRecycleBinW(None, None, 1)  # SHERB_NOCONFIRMATION
        print(f"    {G}→ Bin purged.{X}")
    except: print(f"    {R}→ Failed (run as Admin).{X}")

def flush_network():
    print(f"{Y}[+] Flushing DNS + resetting TCP/IP stack...{X}")
    cmds = [
        "ipconfig /flushdns",
        "ipconfig /release",
        "ipconfig /renew",
        "netsh int ip reset",
        "netsh winsock reset",
        "netsh advfirewall reset"
    ]
    for cmd in cmds:
        try:
            subprocess.run(cmd, shell=True, capture_output=True)
        except: pass
    print(f"    {G}→ Network stack reborn.{X}")

def show_top():
    print(f"{Y}[+] Current top 10 offenders:{X}")
    procs = sorted(
        [p.info for p in psutil.process_iter(['name','cpu_percent','memory_percent']) 
         if p.info['cpu_percent'] is not None],
        key=lambda x: x['cpu_percent'] or 0, reverse=True)[:10]
    for i, p in enumerate(procs, 1):
        print(f"    {i:2}. {p['name'][:35]:35} CPU {p['cpu_percent']:6.1f}% RAM {p['memory_percent']:5.1f}%")

def main():
    if not is_admin():
        print(f"{R}RUN AS ADMINISTRATOR FOR FULL POWER. Right-click → Run as administrator.{X}")
        input("Press Enter to continue with limited mode anyway...")
    
    banner()
    print(f"{C}Time  :{X} {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    kill_hogs()
    nuke_all_temp()
    empty_recycle_bin()
    flush_network()
    show_top()

    print(f"\n{G}══════════════════════════════════════════════════{X}")
    print(f"{G}          RAGE CLEAN v2.0 COMPLETE               {X}")
    print(f"{G}       Your PC just hit the gym and PR’d         {X}")
    print(f"{G}══════════════════════════════════════════════════{X}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{R}Clean aborted. Stay savage.{X}")