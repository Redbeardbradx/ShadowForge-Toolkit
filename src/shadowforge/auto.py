#!/usr/bin/env python3
# ShadowForge Auto: Recon → Shield chain. Set-it-forget-it glory.
import argparse
from main import recon_scan, shield_scan  # Import core funcs

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto Chain: Raid then seal.")
    parser.add_argument('--target', required=True, help='IP for full sweep')
    args = parser.parse_args()
    
    print("\033[95m[AUTO BEAST]\033[0m Unleashing chain on {args.target}...")
    recon_scan(args.target)
    shield_args = argparse.Namespace(target=args.target)
    shield_scan(shield_args)
    print("\033[92m[AUTO SEALED]\033[0m Chain complete—CSV log next sprint.")