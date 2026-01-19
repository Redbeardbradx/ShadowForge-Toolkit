# src/shadowforge/main.py
import argparse
from termcolor import colored
import sys
import traceback

# Graceful imports - CLI works even if modules missing
run_recon = None
run_osint = None
generate_payload = None

try:
    from shadowforge.recon import run_recon
except ImportError as e:
    print(colored(f"[!] Recon missing: {e}", "red"), file=sys.stderr)

try:
    from shadowforge.osint import run_osint
except ImportError as e:
    print(colored(f"[!] OSINT missing: {e}", "red"), file=sys.stderr)

try:
    from shadowforge.payloads import generate_payload
except ImportError as e:
    print(colored(f"[!] Payloads missing: {e}", "red"), file=sys.stderr)

def main():
    parser = argparse.ArgumentParser(
        prog="shadowforge",
        description="ShadowForge Toolkit - Ethical pentest lab suite",
        epilog="Lab VMs only. 18 U.S.C. §1030 violation otherwise."
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # recon
    recon_p = subparsers.add_parser("recon", help="Nmap wrapper scan")
    recon_p.add_argument("--target", required=True, help="Lab IP/range")
    recon_p.add_argument("--scan", default="ping", choices=["ping", "tcp", "version", "os"])
    recon_p.add_argument("--ports", default="1-1000")

    # osint stub
    osint_p = subparsers.add_parser("osint", help="OSINT gathering")
    osint_p.add_argument("--domain", required=True, help="Target domain")

    # payloads (booty!)
    payload_p = subparsers.add_parser("payloads", help="Generate reverse shell")
    payload_p.add_argument("--type", required=True, choices=["reverse"])
    payload_p.add_argument("--ip", required=True, help="Listener IP")
    payload_p.add_argument("--port", type=int, required=True, help="Listener port")

    args = parser.parse_args()

    try:
        if args.command == "recon":
            if run_recon is None:
                print(colored("[!] Create src/shadowforge/recon.py", "red"))
            else:
                run_recon(args.target, args.scan, args.ports)
        elif args.command == "osint":
            if run_osint is None:
                print(colored("[!] Create src/shadowforge/osint.py", "red"))
            else:
                run_osint(args.domain)
        elif args.command == "payloads":
            if generate_payload is None:
                print(colored("[!] Create src/shadowforge/payloads.py", "red"))
            else:
                generate_payload(args.type, args.ip, args.port)
        else:
            parser.print_help()
    except Exception as e:
        print(colored(f"[!] Error: {e}", "red"))
        traceback.print_exc(file=sys.stderr)

if __name__ == "__main__":
    main()