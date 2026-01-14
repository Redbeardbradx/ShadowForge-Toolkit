# modules/cleanse.py
import os
import subprocess
import shutil
from datetime import datetime

def clear_temp():
    paths = [
        os.getenv('TEMP'),
        os.getenv('TMP'),
        r'C:\Windows\Temp',
        r'C:\Windows\Prefetch',
        r'C:\$Recycle.Bin'
    ]
    for path in paths:
        if path and os.path.exists(path):
            try:
                for root, dirs, files in os.walk(path):
                    for f in files:
                        os.unlink(os.path.join(root, f))
                    for d in dirs:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                print(f"[+] Cleared: {path}")
            except Exception as e:
                print(f"[-] Failed {path}: {e}")

def flush_dns():
    try:
        subprocess.run(['ipconfig', '/flushdns'], check=True, capture_output=True)
        print("[+] DNS cache flushed")
    except:
        print("[-] DNS flush failed")

def clear_event_logs():
    try:
        subprocess.run(['wevtutil', 'cl', 'Application'], check=True, capture_output=True)
        subprocess.run(['wevtutil', 'cl', 'System'], check=True, capture_output=True)
        subprocess.run(['wevtutil', 'cl', 'Security'], check=True, capture_output=True)
        print("[+] Event logs cleared (App/System/Security)")
    except:
        print("[-] Event log clear failed - needs admin")

def run(args):
    print(f"[*] ShadowForge Cleanse started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    clear_temp()
    flush_dns()
    if args.full:
        clear_event_logs()
    print("[+] Cleanse complete. Host tracks minimized.\n")