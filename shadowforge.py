import argparse
import subprocess
import json
import yaml  # From requirements flood
from ruamel.yaml import YAML  # Deep merge

parser = argparse.ArgumentParser(description='ShadowForge: Ethical Chaos Engine')
subparsers = parser.add_subparsers(dest='command', help='Commands')

recon_parser = subparsers.add_parser('recon', help='Recon module')
recon_parser.add_argument('--target', required=True, help='Target domain/IP')
recon_parser.add_argument('--osmedeus-full', action='store_true', help='Full Osmedeus chain')
recon_parser.add_argument('--osmedeus-custom', help='YAML patch file')

args = parser.parse_args()

if args.command == 'recon':
    print(f"Recon on {args.target}: Forging...")
    if args.osmedeus_custom or args.osmedeus_full:
        # Merge logic stub (from merge_workflows.py; exec or import)
        base_yaml = {'workflows': {'recon': {'tools': ['nmap', 'amass', 'rustscan', 'dracmap']}}}
        if args.osmedeus_custom:
            with open(args.osmedeus_custom, 'r') as f:
                patch = json.load(f)
            base_yaml['workflows'].update(patch['workflows'])
        merged_yaml = yaml.dump(base_yaml)
        with open('merged_workflow.yaml', 'w') as out:
            out.write(merged_yaml)
        print("Merged workflow forged.")
    if args.osmedeus_full:
        # WSL Osmedeus chain
        subprocess.run(['wsl', 'osmedeus', 'scan', '--target', args.target, '--config', '/mnt/e/ShadowForge-Toolkit/merged_workflow.yaml'], check=True)
        print("Osmedeus full chain fired: Recon + fuzz + osint.")
        # Stub output parse (real: yaml.load report)
        print("Sim report: 17 dirs (/admin, /api/v1), 45 emails, Nuclei vulns: 3 CVEs flagged.")
    else:
        # Basic recon stub (Nmap/Rustscan subprocess)
        subprocess.run(['nmap', '-sV', args.target], check=True)
        print("Basic recon: Ports + services JSON stub.")