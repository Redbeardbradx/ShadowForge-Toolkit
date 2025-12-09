import psutil
import os
import subprocess
from datetime import datetime

# OneDrive path hunt—adjust if your sync dir's custom (e.g., C:\Users\[YourName]\OneDrive\Documents)
onedrive_root = os.path.expanduser(r"~\C:\Users\bradm\OneDrive\MJ Goat Sales")  # Stock OneDrive root
py_scripts = []

def hunt_running_py():
    running = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower() or 'py' in ' '.join(proc.info['cmdline'] or []):
                cmd = ' '.join(proc.info['cmdline'] or ['unknown'])
                running.append({'pid': proc.info['pid'], 'cmd': cmd, 'status': proc.status()})
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return running

def scan_onedrive_py(root):
    for dirpath, dirs, files in os.walk(root):
        for file in files:
            if file.endswith('.py'):
                py_scripts.append(os.path.join(dirpath, file))
    return py_scripts

if __name__ == '__main__':
    print("💀 OneDrive Python Recon: Hunting running blades & idle scripts...")
    
    # Hunt running
    running_py = hunt_running_py()
    print(f"Running Python processes: {len(running_py)}")
    for p in running_py:
        print(f"PID {p['pid']}: {p['cmd']} (Status: {p['status']})")
    
    # Scan OneDrive .py ghosts
    scripts = scan_onedrive_py(onedrive_root)
    print(f"\nIdle .py scripts in OneDrive: {len(scripts)}")
    for script in scripts:
        print(f"  - {script}")
    
    # Log scars
    with open('onedrive_recon_log.txt', 'a', encoding='utf-8') as l:
        l.write(f"{datetime.now()}: Recon complete—{len(running_py)} running, {len(scripts)} idle scripts.\n")
    
    print("\n💀 Scars logged to onedrive_recon_log.txt—clean sweep? Gold.")
    input("Hit Enter to close...")  # Pause for your eyes