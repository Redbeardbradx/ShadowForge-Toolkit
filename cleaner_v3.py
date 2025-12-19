import os
import subprocess
import shutil  # <-- Added this line
from termcolor import colored

def run_disk_cleanup():
    subprocess.run(["cleanmgr", "/sagerun:1"], shell=True)
    print(colored("[+] Disk Cleanup executed", "green"))

def clear_prefetch():
    path = r"C:\Windows\Prefetch"
    if os.path.exists(path):
        shutil.rmtree(path, ignore_errors=True)
        os.makedirs(path)  # Recreate empty for Windows
        print(colored("[+] Prefetch cleared and recreated", "green"))

def clear_thumbnails():
    path = os.path.expanduser(r"~\AppData\Local\Microsoft\Windows\Explorer")
    if os.path.exists(path):
        for file in os.listdir(path):
            if file.startswith("thumbcache"):
                try:
                    os.unlink(os.path.join(path, file))
                except:
                    pass
        print(colored("[+] Thumbnail cache cleared", "green"))

def clear_event_logs():
    try:
        logs = ["Application", "System", "Security"]
        for log in logs:
            subprocess.run(["wevtutil", "cl", log], check=True, stdout=subprocess.DEVNULL)
        print(colored("[+] Event logs cleared (requires admin)", "green"))
    except:
        print(colored("[!] Event log clear failed (run as admin)", "yellow"))

if __name__ == "__main__":
    print(colored("[*] Starting weekly deep clean (v3)...", "yellow"))
    run_disk_cleanup()
    clear_prefetch()
    clear_thumbnails()
    clear_event_logs()
    print(colored("[+] Weekly clean complete. System optimized.", "green"))