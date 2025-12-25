#!/usr/bin/env python3
# ShadowForge Toolkit — Modular Ethical Hacking Suite. Utah Viking edition.
import argparse
import importlib
import os
import sys
from termcolor import colored

# Proper package path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def load_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    loaded = []
    for filename in os.listdir(modules_dir):
        if filename.endswith(".py") and filename not in ["__init__.py"]:
            mod_name = filename[:-3]
            try:
                importlib.import_module(f"shadowforge.modules.{mod_name}")
                print(colored(f"[+] Forged {mod_name} into arsenal", "green"))
                loaded.append(mod_name)
            except Exception as e:
                print(colored(f"[-] {mod_name} forge failed: {e}", "red"))
    return loaded

def main():
    parser = argparse.ArgumentParser(
        description="ShadowForge: Recon raids, shield seals, auto chains—dominate your lab.",
        epilog="Use only on systems you own or have explicit permission to test."
    parser.add_argument('module', choices=['recon', 'osint', 'shield', 'ai_suggest', 'cleanse', 'bedtime', 'scan'],
        help='Module to execute')
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Recon subcommand
    recon_parser = subparsers.add_parser("recon", help="Port/OSINT raid")
    recon_parser.add_argument("--target", required=True, help="IP/domain to hammer")
    recon_parser.add_argument("--aggressive", action="store_true", help="Full port + vuln scripts")

    # Shield subcommand
    shield_parser = subparsers.add_parser("shield", help="Proc/port seal + evasion")
    shield_parser.add_argument("--target", default="127.0.0.1", help="Target for shield ops")

    # Auto chain
    auto_parser = subparsers.add_parser("auto", help="Full chain: recon → shield")
    auto_parser.add_argument("--target", required=True, help="Target for full auto raid")

    args = parser.parse_args()
    load_modules()

    if args.command == "recon":
        from shadowforge.modules.recon import run_recon
        run_recon(args.target, aggressive=args.aggressive)
    if args.module in ['recon', 'scan']:
        from shadowforge.modules.recon import run_recon
        run_recon(args)
    elif args.command == "shield":
        from shadowforge.modules.shield import run_shield
        run_shield(args.target)
    elif args.command == "auto":
        from shadowforge.modules.recon import run_recon
        from shadowforge.modules.shield import run_shield
        print(colored("[AUTO CHAIN] Raid → Seal sequence initiated", "magenta"))
        run_recon(args.target, aggressive=True)
        run_shield(args.target)
    else:
        parser.print_help()
        sys.exit(1)

    print(colored("[FORGE WIN] Cycle crushed—log the loot, brother.", "green"))

if __name__ == "__main__":
    print(colored("""
    ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗███████╗ ██████╗ ██████╗  ██████╗ ███████╗
    ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔════╝ ██║    ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
    ███████╗███████║███████║██║  ██║██║  ███╗██║ █╗ ██║█████╗  ██║   ██║██████╔╝██║  ███╗█████╗  
    ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║██╔══╝  ██║   ██║██╔══██╗██║   ██║██╔══╝  
    ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝██║     ╚██████╔╝██║  ██║╚██████╔╝██║     
    ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝ ╚═╝      ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚═╝    
    """, "red"))
    main()