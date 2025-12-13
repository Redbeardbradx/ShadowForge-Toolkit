#!/usr/bin/env python3
import argparse
from banner import print_banner
from modules.bedtime import main as bedtime_main
from modules.recon import main as recon_main   # ← Fixed import

def main():
    print_banner()

    parser = argparse.ArgumentParser(prog="shadowforge", description="ShadowForge-Toolkit v2")
    subparsers = parser.add_subparsers(dest="command", title="Commands")

    # Bedtime purge
    bedtime_parser = subparsers.add_parser("bedtime", help="Post-session purge")
    bedtime_parser.add_argument("--mode", choices=["hacking", "bedtime"], default="bedtime")

    # Recon module
    recon_parser = subparsers.add_parser("recon", help="RustScan → Nmap recon")
    recon_parser.add_argument("target", help="Target IP or range")

    args = parser.parse_args()

    if args.command == "bedtime":
        bedtime_main(mode=args.mode)

    elif args.command == "recon":
        recon_main(target=args.target)

    else:
        parser.print_help()

if __name__ == "__main__":
    main()