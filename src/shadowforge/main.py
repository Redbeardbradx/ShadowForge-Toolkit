import argparse
import json
from typing import Optional
from .modules.recon import run_nmap_scan
from .modules.payloads import gen_reverse_shell, gen_for_port
from .modules.auto import chain_assault
from .modules.shield.proxy import tor_session

def cli_entry():
    parser = argparse.ArgumentParser(description='ShadowForge: Ethical pentest forge.')
    subparsers = parser.add_subparsers(dest='command')
    # Recon sub
    recon_parser = subparsers.add_parser('recon', help='Nmap + CVE recon')
    recon_parser.add_argument('--target', required=True)
    recon_parser.add_argument('--proxy', choices=['tor'], default=None)
    # Auto sub
    auto_parser = subparsers.add_parser('auto', help='Chain recon → payloads')
    auto_parser.add_argument('--target', required=True)
    auto_parser.add_argument('--dry-run', action='store_true', default=True)
    auto_parser.add_argument('--proxy', choices=['tor'], default=None)
    # Payload sub
    payload_parser = subparsers.add_parser('payload', help='Gen shell')
    payload_parser.add_argument('--target', required=True)
    payload_parser.add_argument('--port', type=int, default=4444)
    payload_parser.add_argument('--type', choices=['bash', 'python'], default='bash')
    # Audit sub
    audit_parser = subparsers.add_parser('audit', help='Rig lockdown sweep')
    audit_parser.add_argument('--level', choices=['quick', 'full'], default='quick')
    args = parser.parse_args()
    if args.command == 'recon':
        session = tor_session() if args.proxy == 'tor' else None
        data = run_nmap_scan(args.target, session)
        print(json.dumps(data, indent=2))
    elif args.command == 'auto':
        session = tor_session() if args.proxy == 'tor' else None
        for slice in chain_assault(args.target, args.dry_run, args.proxy):
            print(json.dumps(slice, indent=2))
    elif args.command == 'payload':
        shell_data = gen_reverse_shell(args.target, args.port, args.type)
        print(json.dumps(shell_data, indent=2))
    elif args.command == 'audit':
        from .modules.security_audit import run_audit, log_audit
        results = run_audit(args.level)
        print(json.dumps(results, indent=2))
        print(log_audit(results))
    return 0

# Save. Verify: Get-Content src\shadowforge\main.py | Select -LineNumber -Line 25-35  # Echo indented block—no orphan if