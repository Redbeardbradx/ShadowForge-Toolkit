import argparse
from engine import ping_sweep
import json
import os

parser = argparse.ArgumentParser(description="ShadowForge: Stealth CLI – Week 1 capstone.")
subparsers = parser.add_subparsers(dest='command')

scan_parser = subparsers.add_parser('scan', help='Stealth vein chain')
scan_parser.add_argument('--target', type=str, required=True)
scan_parser.add_argument('--output', type=str, default='console', choices=['console', 'json'])

args = parser.parse_args()
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