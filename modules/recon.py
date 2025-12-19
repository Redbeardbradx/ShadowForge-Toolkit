#!/usr/bin/env python3
"""
ShadowForge-Toolkit – modules/recon.py
Fast recon chain: RustScan (rapid port discovery) → targeted Nmap (deep analysis)
Lab-only. Requires Docker + rustscan/rustscan:latest pulled.
"""

import argparse
import subprocess
import sys
import re
from termcolor import colored

def run_recon_chain(target: str, rustscan_opts: str = "-b 5000 -t 2000", nmap_opts: str = "-sV -sC -O -T4"):
    print(colored(f"[+] Launching recon chain on lab target: {target}", "yellow"))
    
    # Phase 1: RustScan via Docker – ultra-fast full-port scan
    rustscan_cmd = [
    "docker", "run", "--rm", "-it",
    "--ulimit", "nofile=1048576:1048576",
    "rustscan/rustscan:2.1.1",  # Stable, smaller
    "-a", target,
    *rustscan_opts.split(),
    "--", *nmap_opts.split()
]
    
    print(colored(f"[*] RustScan phase: {rustscan_cmd}", "cyan"))
    
    try:
        result = subprocess.run(rustscan_cmd, capture_output=True, text=True, check=False)
        
        if result.returncode != 0 and "No ports found" not in result.stdout:
            print(colored(f"[-] RustScan failed: {result.stderr.strip()}", "red"))
            sys.exit(1)
            
        print(colored(result.stdout.strip(), "green"))
        if result.stderr:
            print(colored(result.stderr.strip(), "magenta"))

        # Extract open ports from RustScan output
        ports = re.findall(r"Open\s+[\d.]+\:(\d+)", result.stdout)
        if not ports:
            print(colored("[-] No open ports detected – ending chain", "yellow"))
            return
            
        ports_str = ",".join(ports)
        print(colored(f"[+] {len(ports)} open ports found: {ports_str}", "green"))
        
        # Phase 2: Targeted deep Nmap (native, no Docker needed)
        print(colored("[*] Deep Nmap phase – version detection, scripts, OS fingerprint", "cyan"))
        nmap_cmd = ["nmap", "-p", ports_str, *nmap_opts.split(), target]
        nmap_result = subprocess.run(nmap_cmd, capture_output=True, text=True)
        
        print(colored(nmap_result.stdout.strip(), "green"))
        if nmap_result.stderr:
            print(colored(nmap_result.stderr.strip(), "magenta"))
            
    except FileNotFoundError:
        print(colored("[-] Docker not found. Install Docker Desktop and pull image: docker pull rustscan/rustscan:latest", "red"))
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="ShadowForge Fast Recon – RustScan + Nmap chain (lab only)")
    parser.add_argument("target", help="Lab target IP or range (e.g., 192.168.10.10 or 192.168.10.0/24)")
    parser.add_argument("--rustscan-opts", default="-b 5000 -t 2000", help="RustScan options (default: batch 5000, timeout 2000ms)")
    parser.add_argument("--nmap-opts", default="-sV -sC -O -T4", help="Nmap options (default: version, default scripts, OS, aggressive timing)")
    args = parser.parse_args()
    
    run_recon_chain(args.target, args.rustscan_opts, args.nmap_opts)

if __name__ == "__main__":
    main()