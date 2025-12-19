#!/usr/bin/env python3
"""
ShadowForge-Toolkit – main.py
CLI entry point + module router
"""
import argparse
import sys
import subprocess
import webbrowser
import time
import re
from termcolor import colored
from recon import ping_sweep, version_scan

VERSION = "0.1.0"

def banner():
    print(colored(r"""
   _____ _ _ _____ _
  / ____| | | | | __ \ | |
 | (___ | |__ __ _| | ___ | | | | ___ ___| |__ ___ ___
  \___ \| '_ \ / _` | |/ _ \| | | |/ _ \/ __| '_ \ / _ \/ __|
  ____) | | | | (_| | | (_) | | | | __/\__ \ | | | __/\__ \
 |_____/|_| |_|\__,_|_|\___/|_| |_| \___||___/_| |_|\___||___/
    """, "red"))
    print(colored(f"ShadowForge-Toolkit v{VERSION} – Isolated lab environment only\n", "cyan"))

def main():
    banner()
    parser = argparse.ArgumentParser(description="ShadowForge Toolkit – Lab Only")
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # Recon command
    recon = sub.add_parser("recon", help="Network reconnaissance")
    recon.add_argument("action", choices=["sweep", "version"], help="Action: sweep (host discovery) or version (service/OS scan)")
    recon.add_argument("--target", required=True, help="Target range (sweep) or IP(s) (version)")

    # Phone OSINT command
    phone = sub.add_parser("phone", help="Reverse phone number OSINT")
    phone.add_argument("-n", "--number", required=True, help="Phone in E.164 format e.g. +15551234567")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "recon":
        if args.action == "sweep":
            ping_sweep(args.target)
        elif args.action == "version":
            hosts = args.target.split()
            version_scan(hosts)

    elif args.command == "phone":
        print(colored("[+] Running PhoneInfoga reverse lookup...", "yellow"))
        cmd = ["docker", "run", "--rm", "sundowndev/phoneinfoga", "scan", "-n", args.number]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(result.stdout)

            safe_num = args.number[1:]
            with open(f"logs/phone_{safe_num}.txt", "w") as f:
                f.write(result.stdout)

            dork_pattern = re.compile(r'URL: (https://www\.google\.com/search\?q=[^ \n]+)')
            dorks = dork_pattern.findall(result.stdout)
            if dorks:
                print(colored(f"[+] Opening {len(dorks)} Google dork tabs...", "yellow"))
                for dork in dorks:
                    webbrowser.open_new_tab(dork)
                    time.sleep(1.5)
            else:
                print(colored("[*] No dorks found", "cyan"))

        except subprocess.CalledProcessError as e:
            print(colored(f"[!] PhoneInfoga error: {e.stderr}", "red"))
        except FileNotFoundError:
            print(colored("[!] Docker not running or image missing", "red"))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()