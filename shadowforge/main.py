#!/usr/bin/env python3  # Shebang flex – Unix roar; Windows ignores
import argparse
from engine import ping_sweep  # Your old hack core
import json
import os

parser = argparse.ArgumentParser(description="ShadowForge: Stealth CLI – Week 1 capstone.")
subparsers = parser.add_subparsers(dest='command')

# Scan sub – stealth vein
scan_parser = subparsers.add_parser('scan', help='Stealth vein chain')
scan_parser.add_argument('--target', type=str, required=True)
scan_parser.add_argument('--output', type=str, default='console', choices=['console', 'json'])

# Recon sub – Nmap beast chain (Week 2 tease)
recon_parser = subparsers.add_parser('recon', help='Nmap beast chain')
recon_parser.add_argument('--target', type=str, required=True, help='Target IP/range')

args = parser.parse_args()  # Parse yoke – after subs, before if chain

if args.command == 'scan':
    try:
        print(f"[*] Stealth veining {args.target}...")
        report = ping_sweep(args.target)
        if report:
            print(f"[+] Vuln seeds flagged: {report.get('vuln_seeds', [])}")  # Day 3 tease
            if args.output == 'json':
                os.makedirs('../reports', exist_ok=True)
                dump_file = f"../reports/stealth_{args.target.replace('.', '_')}.json"
                with open(dump_file, 'w') as f:
                    json.dump(report, f, indent=2)
                print(f"\033[92m[+] Stealth dump: {dump_file}\033[0m")
    except Exception as e:
        print(f"\033[91m[-] Chain shield: {e}\033[0m")

if args.command == 'recon':
    from modules.recon import run_nmap  # Evo import – your Nmap wrapper
    print(f"[+] Forging recon on {args.target}...")
    output = run_nmap(args.target)
    if "Recon fail" not in output:
        print(f"\033[92m[+] Recon vein (top 500 chars):\033[0m\n{output[:500]}...")
        # Week 2: JSON parse here (ports dict from regex, vuln_seeds flag)
    else:
        print(f"\033[91m[-] Recon snag: {output}\033[0m")  # Trap clean – newline locked