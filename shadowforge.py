#!/usr/bin/env python3
"""
ShadowForge-Toolkit v6.0 Clean Lab Edition
Ethical recon toolkit lab-only built by Redbeardbradx
"""
import argparse
import sys
import os
import logging
import subprocess
from termcolor import colored
from osint.domain_enum import amass_enum

# Create logs folder if missing
os.makedirs("logs", exist_ok=True)

# Logging setup
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
   _____ _ _____
  / ____| | / ____|
 | (___ | |__ ___ | | __ ___ _ __ ___
  \___ \| '_ \ / _ \| | |_ |/ _ \| '_ \ / _ \
  ____) | | | | (_) | |__| | (_) | | | | __/
 |_____/|_| |_|\___/ \_____|\___/|_| |_|\___|
                                              
v6.0 Lab Edition
    """, "red", attrs=["bold"]))

def ping_sweep(target):
    try:
        logging.info(f"Sweeping {target} for live hosts")
        cmd = ["nmap", "-sn", "-PE", "-oG", "-", target]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)

        live_hosts = []
        for line in result.stdout.splitlines():
            if line.startswith("Host: ") and "Status: Up" in line:
                host = line.split("Host: ")[1].split(" (")[0].strip()
                live_hosts.append(host)
                print(colored(f" LIVE {host}", "green"))

        if not live_hosts:
            print(colored("[*] No live hosts found in range", "cyan"))
        else:
            print(colored(f"[+] Found {len(live_hosts)} live hosts", "green"))

        return live_hosts  # Return for chaining later

    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Nmap failed: {e.stderr}", "red"))
    except FileNotFoundError:
        print(colored("[!] nmap.exe not found in PATH", "red"))


    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Nmap failed: {e.stderr}", "red"))
    except FileNotFoundError:
        print(colored("[!] nmap.exe not found in PATH", "red"))

    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Nmap failed: {e.stderr}", "red"))
    except FileNotFoundError:
        print(colored("[!] nmap.exe not found in PATH", "red"))

def main():
    banner()
    parser = argparse.ArgumentParser(description="ShadowForge Toolkit v6.0 - Lab Only")
    sub = parser.add_subparsers(dest="command")

    # Recon sweep
    recon = sub.add_parser("recon", help="Network reconnaissance")
    recon.add_argument("action", choices=["sweep"], help="Ping sweep")
    recon.add_argument("--target", required=True, help="Target range e.g. 192.168.56.0/24")

    # Domain OSINT
    domain = sub.add_parser("domain", help="Passive domain enumeration")
    domain.add_argument("-d", "--domain", required=True, help="Target domain e.g. example.com")

    # Phone OSINT
    phone = sub.add_parser("phone", help="Phone number OSINT")
    phone.add_argument("-n", "--number", required=True, help="Phone in E.164 format e.g. +15551234567")

    args = parser.parse_args()

    if args.command == "recon" and args.action == "sweep":
        ping_sweep(args.target)

    elif args.command == "domain":
        logging.info(f"Passive Amass enumeration on {args.domain}")
        amass_enum(args.domain)

    elif args.command == "phone":
        logging.info(f"PhoneInfoga OSINT on {args.number}")
        print(colored("[+] Phone module placeholder - Docker integration next", "yellow"))

    else:
        parser.print_help()

if __name__ == "__main__":
    main()