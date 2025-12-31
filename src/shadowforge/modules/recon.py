# src/shadowforge/modules/recon.py
# Pure local Nmap recon — fast, reliable, no dependencies beyond Nmap

import subprocess
import os
from termcolor import colored

def run_recon(args):
    target = args.target.strip()
    aggressive = args.aggressive or args.full

    print(colored(f"[RECON RAID] Hammering lab target: {target}", "red"))
    if aggressive:
        print(colored("[!] AGGRESSIVE MODE — scanning all 65535 ports + scripts", "yellow"))

    os.makedirs("reports", exist_ok=True)

    # Base Nmap flags
    nmap_cmd = [
        "nmap",
        "-T4",                     # timing template 4 (aggressive but stable)
        "-Pn",                     # skip host discovery
        "-sV",                     # version detection
        "-sC",                     # default script scan
        "-O",                      # OS fingerprint
        "--stats-every", "10s",    # progress feedback every 10s
        "-oA", f"reports/recon_{target.replace('/', '_')}"  # all formats to host reports/
    ]

    if aggressive:
        nmap_cmd.append("-p-")     # full port range

    nmap_cmd.append(target)

    print(colored(f"[NMAP PHASE] Executing: {' '.join(nmap_cmd)}", "cyan"))

    try:
        # Live output + progress
        subprocess.run(nmap_cmd, check=False)
    except FileNotFoundError:
        print(colored("[X] Nmap not found in PATH — install it first", "red"))
        return

    # Quick live summary from .nmap file
    nmap_file = f"reports/recon_{target.replace('/', '_')}.nmap"
    if os.path.exists(nmap_file):
        print(colored("\n[+] LIVE FINDINGS SUMMARY", "green"))
        with open(nmap_file, "r") as f:
            for line in f:
                if any(keyword in line.lower() for keyword in ["open", "os:", "service"]):
                    print(colored(f"    {line.strip()}", "yellow"))

    print(colored("[RECON COMPLETE] Results in reports/ (recon_<target>.*) — move on with your Christmas.", "green"))