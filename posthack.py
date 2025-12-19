import os
import shutil
import subprocess
from termcolor import colored

def clear_temp():
    paths = [os.environ.get("TEMP"), os.environ.get("TMP"), r"C:\Windows\Temp"]
    for path in paths:
        if path and os.path.exists(path):
            for root, dirs, files in os.walk(path):
                for f in files:
                    try:
                        os.unlink(os.path.join(root, f))
                    except:
                        pass
                for d in dirs:
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                    except:
                        pass
    print(colored("[+] Temp directories cleared", "green"))

def clear_recycle_bin():
    try:
        subprocess.run(["powershell", "-Command", "Clear-RecycleBin -Force"], check=True, stdout=subprocess.DEVNULL)
        print(colored("[+] Recycle Bin emptied", "green"))
    except:
        print(colored("[!] Failed to clear Recycle Bin (run as admin)", "yellow"))

def clear_bash_history():
    history_files = [
        os.path.expanduser("~/.bash_history"),
        r"C:\Users\%USERNAME%\AppData\Roaming\Microsoft\Windows\PowerShell\PSReadLine\ConsoleHost_history.txt"
    ]
    for hist in history_files:
        if os.path.exists(hist):
            open(hist, "w").close()
    print(colored("[+] Bash/PowerShell history cleared", "green"))

def wipe_loot():
    loot_dirs = ["loot", "output", "screenshots", "logs"]  # Add your own
    for dir in loot_dirs:
        if os.path.exists(dir):
            shutil.rmtree(dir, ignore_errors=True)
            os.makedirs(dir)  # recreate empty
    print(colored("[+] Loot directories wiped and recreated", "green"))

if __name__ == "__main__":
    print(colored("[*] Starting post-hack cleanup...", "yellow"))
    clear_temp()
    clear_recycle_bin()
    clear_bash_history()
    wipe_loot()
    print(colored("[+] Post-hack cleanup complete. Lab baseline restored.", "green"))