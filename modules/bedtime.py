#!/usr/bin/env python3
import os
import shutil
import subprocess
from pathlib import Path
from colorama import init, Fore, Style

init(convert=True)

def clear_brave_artifacts():
    base = Path(os.getenv("LOCALAPPDATA")) / "BraveSoftware" / "Brave-Browser" / "User Data"
    targets = [
        "Default/Cache", "Default/Code Cache", "Default/GPUCache",
        "Default/Cookies*", "Default/History*", "Default/Web Data*",
        "Default/Session Storage", "Default/Local Storage",
        "Default/Tor", "Tor Profile"
    ]
    for path in base.rglob("*"):
        for t in targets:
            if t.replace("*", "") in str(path):
                if path.is_dir():
                    shutil.rmtree(path, ignore_errors=True)
                else:
                    path.unlink(missing_ok=True)

def clear_system():
    shutil.rmtree(Path(os.getenv("TEMP")), ignore_errors=True)
    subprocess.run(["ipconfig", "/flushdns"], capture_output=True, shell=True)
    downloads = Path(os.getenv("USERPROFILE")) / "Downloads"
    for pattern in ["*.crdownload", "*.part"]:
        for f in downloads.glob(pattern):
            f.unlink(missing_ok=True)

def main(mode="bedtime"):
    print("[ShadowForge] Initiating purge...")
    clear_brave_artifacts()
    clear_system()
    print(Fore.GREEN + "[+] Artifacts nuked. Rig clean." + Style.RESET_ALL)

    if mode == "hacking":
        print(Fore.CYAN + "[+] Post-hack purge complete. Ready for personal use." + Style.RESET_ALL)
    else:
        print(Fore.CYAN + "[+] Bedtime purge complete." + Style.RESET_ALL)
        choice = input("[?] Shutdown after purge? (y/N): ").strip().lower()
        if choice == "y":
            subprocess.run(["shutdown", "/s", "/t", "10"], shell=True)
            print("[+] Shutting down in 10 seconds...")

if __name__ == "__main__":
    import sys
    m = sys.argv[1] if len(sys.argv) > 1 else "bedtime"
    main(mode=m)