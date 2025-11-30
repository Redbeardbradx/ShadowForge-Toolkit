import argparse
import json
from .modules.recon import run_nmap_scan
from .modules.payloads import gen_for_port
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
        from .modules.payloads import gen_reverse_shell
        shell_data = gen_reverse_shell(args.target, args.port, args.type)
        print(json.dumps(shell_data, indent=2))
    return 0

# Save. Test fallback: python -m shadowforge auto --target 192.168.1.1 --dry-run  # Full: {"phase":"recon_complete","data":{"ports_open":4}} → laced yields (CVE-2024-6387 SSH) → payloads (bash encoded)