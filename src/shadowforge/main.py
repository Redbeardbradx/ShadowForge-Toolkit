# In main.py subparsers (add to recon_parser):
recon_parser.add_argument('--proxy', choices=['tor'], help='Veil thru TOR')

# In if __name__ for recon:
if args.command == 'recon':
    from .modules.recon import run_nmap_scan
    from .modules.shield.proxy import tor_session  # Only if tor
    session = tor_session() if args.proxy == 'tor' else None
    scan_data = run_nmap_scan(args.target, session=session)  # Pass session to recon

# Update recon.py run_nmap_scan (add param):
def run_nmap_scan(target: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    # ... existing ...
    # In geocode: if session: geo_resp = session.get(f"http://ipinfo.io/{target}/json", timeout=10)
    # else: geo_resp = requests.get(...)
    # ... rest unchanged

# At file bottom, before if __name__:
def cli_entry(): full argparse + handlers (subparsers for recon/auto, if command == 'auto': from .modules.auto import chain_assault; for slice in chain_assault(target, dry_run=True, proxy=args.proxy): print(json.dumps(slice)); return 0  # Similar for recon/payload; import json, argparse

if __name__ == "__main__":
    cli_entry()