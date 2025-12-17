#!/usr/bin/env python3
import sys
import argparse
from banner import print_banner
from modules.bedtime import main as bedtime_main
from modules.recon import main as recon_main
from modules.osint import main as osint_main

def main():
    print_banner()

    parser = argparse.ArgumentParser(prog="shadowforge", description="ShadowForge-Toolkit v2")
    parser.add_argument("--version", action="version", version="ShadowForge-Toolkit 0.2.0")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable verbose output")
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # Bedtime
    bedtime_parser = subparsers.add_parser("bedtime", help="Post-session purge")
    bedtime_parser.add_argument("--mode", choices=["hacking", "bedtime"], default="bedtime")

    # Recon
    recon_parser = subparsers.add_parser("recon", help="RustScan → Nmap recon")
    recon_parser.add_argument("target", help="Target IP/range")

    # OSINT
    osint_parser = subparsers.add_parser("osint", help="Name/Phone OSINT")
    osint_parser.add_argument("query", help="Name or phone number (quote names with spaces)")
    osint_parser.add_argument("--type", choices=["name", "phone"], default="name", help="Query type")

    args = parser.parse_args()

    if args.command == "bedtime":
    try:
        bedtime_main(mode=args.mode)
    except Exception as e:
        print(f"[-] Bedtime module error: {e}", file=sys.stderr)
        sys.exit(1)
# Repeat pattern for recon/osint

    elif args.command == "recon":
        recon_main(target=args.target)
    elif args.command == "osint":
        # Pass query/type to osint_main
        osint_main(query=args.query, type=args.type)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()