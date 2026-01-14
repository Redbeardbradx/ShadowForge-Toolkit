import argparse
import importlib
import os
import sys
from termcolor import colored

# Resolve project root and add to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Discover modules dynamically (scan modules/ dir)
def discover_modules():
    modules_dir = os.path.join(PROJECT_ROOT, "modules")
    modules = []
    if os.path.isdir(modules_dir):
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py") and filename != "__init__.py":
                modules.append(filename[:-3])
    return modules

AVAILABLE_MODULES = discover_modules()

def load_module(mod_name):
    try:
        return importlib.import_module(f"modules.{mod_name}")
    except Exception as e:
        print(colored(f"[-] Failed to load module '{mod_name}': {e}", "red"))
        return None

def print_banner():
    banner = """
    ███████╗██╗ ██╗ █████╗ ██████╗ ██████╗ ██╗ ██╗███████╗ ██████╗ ██████╗ ██████╗ ███████╗
    ██╔════╝██║ ██║██╔══██╗██╔══██╗██╔════╝ ██║ ██║██╔════╝██╔═══██╗██╔══██╗██╔════╝ ██╔════╝
    ███████╗███████║███████║██║ ██║██║ ███╗██║ █╗ ██║█████╗ ██║ ██║██████╔╝██║ ███╗█████╗
    ╚════██║██╔══██║██╔══██║██║ ██║██║ ██║██║███╗██║██╔══╝ ██║ ██║██╔══██╗██║ ██║██╔══╝
    ███████║██║ ██║██║ ██║██████╔╝╚██████╔╝╚███╔███╔╝██║ ╚██████╔╝██║ ██║╚██████╔╝██║
    ╚══════╝╚═╝ ╚═╝╚═╝ ╚═╝╚═════╝ ╚═════╝ ╚══╝╚══╝ ╚═╝ ╚═════╝ ╚═╝ ╚═╝ ╚═════╝ ╚═╝
    """
    print(colored(banner, "red"))
    print(colored("ShadowForge Toolkit — Lean. Fast. Ethical.", "yellow"))
    print(colored("Use only on systems you own or have explicit permission to test.", "yellow"))

def main():
    parser = argparse.ArgumentParser(); subparsers = parser.add_subparsers.add_parser('recon', help='Reconnaissance       tools'); recon_parser.add_argument('--scan', help='Target IP')
        description="ShadowForge Toolkit CLI",
        epilog="Legal reminder: Restricted to lab environments only."
    )
    subparsers = parser.add_subparsers(dest="command", required=True, help="Available modules/commands")

    # Global flags (before subcommands)
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    # Dynamically add subparsers for each discovered module
    for mod_name in AVAILABLE_MODULES:
        mod_parser = subparsers.add_parser(mod_name, help=f"Run {mod_name} module")
        # Common args for all modules
        mod_parser.add_argument("--target", "-t", help="Target IP, domain, or network (e.g., 192.168.1.0/24)")
        mod_parser.add_argument("--aggressive", "-a", action="store_true", help="Enable aggressive mode (faster, noisier)")
        mod_parser.add_argument("--full", "-f", action="store_true", help="Run full chain (implies aggressive)")
        # Module-specific args (extend per module; e.g., for recon)
        if mod_name == "recon":
            mod_parser.add_argument("--type", choices=["ping-sweep", "port-scan"], default="ping-sweep", help="Recon type")
            mod_parser.add_argument("--ports", default="1-1024", help="Port range for scans (e.g., 1-65535)")

        # More modules can add custom args here via if-blocks

    args = parser.parse_args()

    if args.full and not args.target:
        parser.error("--full requires --target")

    if args.full:
        args.aggressive = True

    print_banner()
    print(colored(f"[+] Executing command: {args.command}", "green"))

    module = load_module(args.command)
    if module and hasattr(module, "run"):
        module.run(args)
    else:
        print(colored(f"[!] Module '{args.command}' lacks a 'run' function or failed to load.", "red"))

if __name__ == "__main__":
    main()