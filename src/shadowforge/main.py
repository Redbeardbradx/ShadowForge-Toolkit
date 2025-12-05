#!/usr/bin/env python3
# ShadowForge: Core CLI – Recon raids + shield seals. Utah Viking edition. Windows PS primed.
import argparse
import subprocess
import sys
import os
import argparse  # For mock args

def recon_scan(target):
    """Recon: Nmap sweep (Drac bash pivot—direct for PS). OSINT stub inbound."""
    print(f"\033[95m[RECON RAID]\033[0m Hammering {target}—services spill like Viking loot.")
    try:
        # Nmap core—Windows fire
        nmap_cmd = ['nmap', '-sV', '--open', target]  # --open for live ports only
        nmap_result = subprocess.run(nmap_cmd, capture_output=True, text=True, timeout=45)
        if nmap_result.returncode == 0:
            print(nmap_result.stdout)
            print(f"\033[92m[INTEL DROP]\033[0m Services mapped—{len([line for line in nmap_result.stdout.splitlines() if 'open' in line.lower()])} gates open. Vulns next.")
        else:
            print(f"\033[91m[NMAP FAIL]\033[0m {nmap_result.stderr}. Strap nmap: winget install Insecure.Nmap.")
        
        # Drac Pivot: Bash stub—if Linux VM, subprocess.call(['./Dracnmap/Dracnmap.sh', target]); else, nmap echo.
        if os.name == 'nt':  # Windows detect
            print("\033[93m[DRAC PIVOT]\033[0m Bash beast sleeps on PS—raid VM (Kali VBox) or bolt Recon-NG: pip install recon-ng.")
        else:
            drac_path = os.path.join(os.getcwd(), 'Dracnmap', 'Dracnmap.sh')
            if os.path.exists(drac_path):
                subprocess.run(['bash', drac_path, target], timeout=60)
            else:
                print("\033[93m[WARNING]\033[0m Drac dir MIA—git clone https://github.com/screetsec/Dracnmap; chmod +x Dracnmap.sh.")
        
        # Recon-NG Stub (OSINT bolt—pip if not loaded)
        try:
            recon_ng_result = subprocess.run(['recon-ng', '-c', f'modules load recon/domains-hosts/shodan_hostname; options set SOURCE {target}; run'], 
                                             capture_output=True, text=True, timeout=30, shell=True)
            if recon_ng_result.returncode == 0:
                print(f"\033[93m[OSINT GLEAN]\033[0m {recon_ng_result.stdout[:300]}...")  # Snippet
        except FileNotFoundError:
            print("\033[93m[RECON-NG ARMORY]\033[0m Not strapped—pip install recon-ng; recon-ng -ir (install modules).")
            
    except FileNotFoundError:
        print("\033[93m[NMAP ARMORY]\033[0m Nmap ghosted—winget install Insecure.Nmap; PATH refresh.")
    except subprocess.TimeoutExpired:
        print("\033[93m[TIMEOUT]\033[0m Target's a wall—add -T4 for speed.")

def shield_scan(args):
    """Shield import & call."""
    try:
        import shield
        shield.main(args)  # Your shield.py main() flex
    except ImportError:
        print("\033[91m[SHIELD GHOST]\033[0m shield.py MIA or no main()—forge it from Day 4 drop.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowForge: Recon, shield, auto—dominate.")
    subparsers = parser.add_subparsers(dest='command', help='Commands: recon | shield | auto')

    recon_parser = subparsers.add_parser('recon', help='Port/OSINT raid')
    recon_parser.add_argument('--target', required=True, help='IP/hostname probe')

    shield_parser = subparsers.add_parser('shield', help='Proc/port seal')
    shield_parser.add_argument('--target', default='127.0.0.1', nargs='?', help='IP seal')

    auto_parser = subparsers.add_parser('auto', help='Chain raid → seal')
    auto_parser.add_argument('--target', required=True, help='Full auto target')

    args = parser.parse_args()

    if args.command == 'recon':
        recon_scan(args.target)
    elif args.command == 'shield':
        shield_scan(args)
    elif args.command == 'auto':
        recon_scan(args.target)
        shield_args = argparse.Namespace(target=args.target)
        shield_scan(shield_args)
    else:
        parser.print_help()
        sys.exit(1)

    print("\033[92m[FORGE WIN]\033[0m Cycle crushed—log the loot, brother.")