#!/usr/bin/env python3
"""
ShadowForge-Toolkit v6.0  Clean Lab Edition
Ethical recon toolkit  lab-only  built by Redbeardbradx
"""

import argparse
import sys
from termcolor import colored
import logging
import os

# Create logs folder if missing
os.makedirs("logs", exist_ok=True)

# Simple colored logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/shadowforge.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

def banner():
    print(colored(r"""
   _____ _           _____                    
  / ____| |         / ____|                   
 | (___ | |__   ___ | |  __  ___  _ __   ___  
  \___ \| '_ \ / _ \| | |_ |/ _ \| '_ \ / _ \ 
  ____) | | | | (_) | |__| | (_) | | | |  __/ 
 |_____/|_| |_|\___/ \_____|\___/|_| |_|\___| 
                                               
v6.0 Lab Edition  Utah Viking Forge
    """, "red", attrs=["bold"]))

def ping_sweep(target):
    try:
        import nmap
        nm = nmap.PortScanner()
        print(colored(f"[+] Sweeping {target} for live hosts...", "yellow"))
        nm.scan(hosts=target, arguments="-sn -PE")
        for host in nm.all_hosts():
            if nm[host].state() == "up":
                print(colored(f"    LIVE  {host}", "green"))
            else:
                print(colored(f"    down  {host}", "red"))
    except Exception as e:
        print(colored(f"[!] Nmap error: {e}", "red"))

def main():
    banner()
    parser = argparse.ArgumentParser(description="ShadowForge 6.0  Lab Recon Tool")
    sub = parser.add_subparsers(dest="command")

    # recon sweep
    sweep = sub.add_parser("recon", help="Network reconnaissance")
    sweep.add_argument("action", choices=["sweep"], help="Ping sweep")
    sweep.add_argument("--target", required=True, help="Target range, e.g. 192.168.56.0/24")

    args = parser.parse_args()

    if args.command == "recon" and args.action == "sweep":
        ping_sweep(args.target)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
