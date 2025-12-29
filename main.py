import argparse
from termcolor import colored  # Install: pip install termcolor
import sys

def main():
    parser = argparse.ArgumentParser(description="ShadowForge-Toolkit: Ethical Hacking Suite")
    subparsers = parser.add_subparsers(dest="command", help="Modules")

    # Recon subcommand
    recon_parser = subparsers.add_parser("recon", help="Recon tools")
    recon_parser.add_argument("--scan", required=True, help="Target IP (e.g., 127.0.0.1)")

    args = parser.parse_args()
    if args.command == "recon":
        from modules.scan import threaded_scan  # We'll create this next
        print(colored(f"Scanning {args.scan}...", "yellow"))
        threaded_scan(args.scan, range(1, 1025))  # Ports 1-1024
    else:
        parser.print_help()
        sys.exit(1)

if __name__ == "__main__":
    main()