#!/usr/bin/env python3
import subprocess
import re
from termcolor import colored

def run_recon(target: str, aggressive: bool = False):
    print(colored(f"[RECON RAID] Hammering lab target: {target}", "red"))

    # Attacker-tuned options
    rustscan_opts = "-b 1000 -t 1500"  # Lower batch for reliability on quiet hosts
    nmap_chain_opts = "-Pn -sV -sC -O -T4"  # Force no ping, version, scripts, OS

    if aggressive:
        rustscan_opts = "-b 2000 -t 1200 --accessible"
        nmap_chain_opts = "-Pn -sV -sC -O -p- --script vuln,exploit,brute -T5 --version-intensity 9"

    rustscan_cmd = [
        "docker", "run", "--rm", "-it",
        "--ulimit", "nofile=1048576:1048576",
        "rustscan/rustscan:2.1.1",
        "-a", target,
        *rustscan_opts.split(),
        "--", *nmap_chain_opts.split()
    ]

    print(colored(f"[RUSTSCAN PHASE] {rustscan_cmd}", "cyan"))

    try:
        result = subprocess.run(
            rustscan_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=600
        )

        print(colored(result.stdout or "[NO STDOUT]", "green"))
        if result.stderr:
            print(colored(result.stderr.strip(), "magenta"))

        # Force deep native Nmap even if RustScan reports nothing (defender ICMP block common)
        print(colored("[FORCE DEEP NMAP] Bypassing potential RustScan miss", "yellow"))
        native_opts = nmap_chain_opts if not aggressive else nmap_chain_opts.replace("-p-", "")
        native_cmd = ["nmap", *native_opts.split(), target]

        native_result = subprocess.run(
            native_cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        print(colored(native_result.stdout or "[NO OUTPUT]", "green"))
        if native_result.stderr:
            print(colored(native_result.stderr.strip(), "magenta"))

    except FileNotFoundError:
        print(colored("[-] Docker daemon down → pure native Nmap fallback", "red"))
        fallback_nmap(target, aggressive)
    except subprocess.TimeoutExpired:
        print(colored("[-] RustScan timeout → native fallback", "yellow"))
        fallback_nmap(target, aggressive)

def fallback_nmap(target, aggressive):
    opts = "-Pn -sV -sC -O -T4"
    if aggressive:
        opts = "-Pn -sV -sC -O -p- --script vuln,exploit,brute -T5"
    cmd = ["nmap", *opts.split(), target]
    res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    print(colored(res.stdout or "[NO OUTPUT]", "green"))

print(colored("[RECON COMPLETE] Full chain executed – review output for live services.", "green"))