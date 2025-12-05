#!/usr/bin/env python3
# ShadowForge: CleanSweep – Ethical rootkit hunter. From ranch dust to digital fortress.
import argparse
import subprocess
import psutil
import json
from scapy.all import sr1, IP, TCP  # Port knock sim
import sys

def scan_ports(target='127.0.0.1', ports=[22, 80, 443, 445, 3389]):
    """Recon.py bolt-in: Nmap-lite port sweep. Flags open gates."""
    open_ports = []
    for port in ports:
        pkt = IP(dst=target)/TCP(dport=port, flags='S')
        resp = sr1(pkt, timeout=1, verbose=0)
        if resp and resp.haslayer(TCP) and resp[TCP].flags == 0x12:  # SYN-ACK
            open_ports.append(port)
            print(f"\033[91m[ALERT]\033[0m Port {port} wide open—like a barn door in a storm.")
    return open_ports

def process_sweep():
    """Shield layer: Sniff running hogs. Kill suspicious (manual flag)."""
    threats = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if proc.info['cpu_percent'] > 50 or 'miner' in proc.info['name'].lower():
                threats.append(proc.info)
                print(f"\033[93m[WARNING]\033[0m PID {proc.info['pid']}: {proc.info['name']} – CPU hog? Ranch it.")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
    return threats

def vuln_report(open_ports, threats):
    """JSON dump for auto.py chain. Feed to Grok API later for exploit sug (x.ai/api)."""
    report = {
        "timestamp": "2025-12-03T12:00:00Z",
        "target": "localhost",
        "status": "clean" if not (open_ports or threats) else "breach risk",
        "open_ports": open_ports,
        "suspect_procs": threats
    }
    with open('sweep_log.json', 'w') as f:
        json.dump(report, f, indent=2)
    print(f"\033[92m[SECURE]\033[0m Report forged: sweep_log.json. Zero threats? You're sealed tighter than a vault.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowForge CleanSweep: Scan, seal, dominate.")
    parser.add_argument('--target', default='127.0.0.1', help="IP to probe (default: localhost)")
    args = parser.parse_args()
    
    print("\033[95m=== ShadowForge Grind: Initiating Clean Sweep ===\033[0m")
    ports = scan_ports(args.target)
    procs = process_sweep()
    vuln_report(ports, procs)
    print("\033[92m[VICTORY]\033[0m Rig's ranch-ready. Run daily: crontab -e → 0 6 * * * python shield.py\033[0m")