#!/usr/bin/env python3
# ShadowForge: Core CLI – Recon raids + shield seals. Utah Viking edition.
import argparse
import subprocess
import sys
import os

def recon_scan(target):
    """Recon: Nmap sweep + Dracnmap bolt (if cloned)."""
    print(f"\033[95m[RECON RAID]\033[0m Hammering {target}—services spill.")
    try:
        # Nmap core
        nmap_result = subprocess.run(['nmap', '-sV', target], capture_output=True, text=True, timeout=30)
        if nmap_result.returncode == 0:
            print(nmap_result.stdout)
        else:
            print(f"\033[91m[NMAP FAIL]\033[0m {nmap_result.stderr}")
        
        # Dracnmap bolt (if dir exists—Python summon)
        drac_dir = os.path.join(os.getcwd(), 'Dracnmap')
        if os.path.exists(drac_dir):
            drac_result = subprocess.run([sys.executable, os.path.join(drac_dir, 'dracnmap.py'), '-t', target], capture_output=True, text=True)
            if drac_result.returncode == 0:
                print(f"\033[93m[DRAC INTEL]\033[0m {drac_result.stdout[:500]}...")  # Snippet to avoid flood
            else:
                print(f"\033[91m[DRAC GHOST]\033[0m {drac_result.stderr}")
        else:
            print("\033[93m[WARNING]\033[0m Dracnmap dir MIA—clone it, brother.")
    except FileNotFoundError:
        print("\033[93m[NMAP ARMORY]\033[0m Nmap not loaded—winget install Insecure.Nmap.")
    except subprocess.TimeoutExpired:
        print("\033[93m[TIMEOUT]\033[0m Target's walled—shorten scan.")

# Shield stub (import from shield.py)
def shield_scan(args):
    import shield
    shield.main(args)  # Calls shield's main (add def main(args): in shield.py below)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowForge: Recon, shield, auto-dominate.")
    subparsers = parser.add_subparsers(dest='command', help='Commands: recon | shield | auto')

    recon_parser = subparsers.add_parser('recon', help='Port/service raid')
    recon_parser.add_argument('--target', required=True, help='IP to probe')

    shield_parser = subparsers.add_parser('shield', help='Clean sweep')
    shield_parser.add_argument('--target', default='127.0.0.1', nargs='?', help='IP to seal')

    auto_parser = subparsers.add_parser('auto', help='Chain: Recon → Shield')
    auto_parser.add_argument('--target', required=True, help='Target for full auto')

    args = parser.parse_args()

    if args.command == 'recon':
        recon_scan(args.target)
    elif args.command == 'shield':
        shield_scan(args)
    elif args.command == 'auto':
        recon_scan(args.target)
        shield_args = argparse.Namespace(target=args.target)  # Mock args for shield
        shield_scan(shield_args)
    else:
        parser.print_help()
        sys.exit(1)

    print("\033[92m[FORGE WIN]\033[0m Cycle crushed—log the loot.")

def main(args):
    ports = scan_ports(args.target)
    procs = process_sweep()
    vuln_report(ports, procs)