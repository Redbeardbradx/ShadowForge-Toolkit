import argparse
import importlib
import os
import sys
from termcolor import colored

# Resolve project root and add to path once
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

# Pre-discover available modules (fast, one-time dir scan)
def discover_modules():
    modules_dir = os.path.join(os.path.dirname(__file__), "modules")
    modules = []
    if os.path.isdir(modules_dir):
        for filename in os.listdir(modules_dir):
            if filename.endswith(".py") and filename not in {"__init__.py"}:
                mod_name = filename[:-3]
                modules.append(mod_name)
    return modules

AVAILABLE_MODULES = discover_modules()

def load_module(mod_name):
    try:
        return importlib.import_module(f"shadowforge.modules.{mod_name}")
    except Exception as e:
        print(colored(f"[-] Failed to load {mod_name}: {e}", "red"))
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

def main():
    parser = argparse.ArgumentParser(
        description="ShadowForge Toolkit — Lean. Fast. Ethical.",
        epilog="Use only on systems you own or have explicit permission to test."
    )
    parser.add_argument("module", nargs="?", choices=AVAILABLE_MODULES,
                        help="Module to execute")
    parser.add_argument("--target", "-t", help="Target IP or domain")
    parser.add_argument("--aggressive", "-a", action="store_true",
                        help="Enable aggressive scanning/options")
    parser.add_argument("--full", "-f", action="store_true",
                        help="Full comprehensive chain (implies aggressive)")

    args = parser.parse_args()

    if not args.module:
        print_banner()
        parser.print_help()
        return

    # Handle --full flag globally
    if args.full:
        if not args.target:
            parser.error("--full requires --target/-t")
        args.aggressive = True  # --full always forces aggressive

    print(colored(f"[+] Executing module: {args.module}", "green"))

    module = load_module(args.module)
    if module and hasattr(module, "run"):
        module.run(args)
    else:
        print(colored(f"[!] Module {args.module} has no 'run' entry point", "yellow"))

if __name__ == "__main__":
    main()