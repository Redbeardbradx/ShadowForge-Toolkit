#!/usr/bin/env python3
import argparse
import sys
from termcolor import colored
from banner import print_banner

from modules.bedtime import main as bedtime_main
from modules.recon import main as recon_main
from modules.osint import main as osint_main  # Adjust if signature changes
from osint import run_osint
from auto import run_auto_chain
import payloads

def main():
    print_banner()
    
    parser = argparse.ArgumentParser(prog="shadowforge", description="ShadowForge-Toolkit v2")
    parser.add_argument("--version", action="version", version="ShadowForge-Toolkit 0.2.0")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    parser.add_parser('osint', help='OSINT gathering')
    parser.add_parser('auto', help='Automated scan → payload chain')
    subparsers = parser.add_subparsers(dest="command", title="Commands")
    
    # Bedtime
    bedtime_parser = subparsers.add_parser("bedtime", help="Post-session purge")
    bedtime_parser.add_argument("--mode", choices=["hacking", "bedtime"], default="bedtime")
    
    # Recon
    recon_parser = subparsers.add_parser("recon", help="RustScan → Nmap recon")
    recon_parser.add_argument("target", help="Target IP/range")
    
    # OSINT
    osint_parser = subparsers.add_parser("osint", help="Domain OSINT collection")
    osint_parser.add_argument("query", help="Domain for passive collection")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    try:
        if args.command == "bedtime":
            bedtime_main(mode=args.mode)
        elif args.command == "recon":
            recon_main(target=args.target)
        elif args.command == "osint":
            osint_main(query=args.query)  # Matches current osint.py signature
        else:
            parser.print_help()
    except Exception as e:
        print(colored(f"[-] Module execution failed: {str(e)}", "red"))
        if args.verbose:
            raise
        sys.exit(1)

if __name__ == "__main__":
    main()