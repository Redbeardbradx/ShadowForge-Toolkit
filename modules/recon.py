#!/usr/bin/env python3
# recon.py – ShadowForge Recon v2
# RustScan (blazing fast) → Nmap deep scan → clean JSON report
# Built by Utah Viking – Lab only. Stay legal.

import subprocess
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BARN_ROOT = Path(__file__).parent.parent
REPORT_DIR = BARN_ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def run_rustscan(target):
    """Ultra-fast port discovery with RustScan"""
    cmd = ["rustscan", "-a", target, "--ulimit", "5000", "--", "-sS", "-sV", "--top-ports", "1000"]
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=180
        )
        if result.returncode not in [0, 1]:
            print("[!] RustScan failed. Falling back to Nmap...")
            return None
        return result.stdout
    except FileNotFoundError:
        print("[!] rustscan not found. Install: https://github.com/RustScan/RustScan")
        print("    Falling back to pure Nmap...")
        return None
    except Exception as e:
        print(f"[!] RustScan error: {e}")
        return None

def extract_open_ports(rustscan_output):
    """Parse RustScan output → list of open ports"""
    ports = []
    for line in rustscan_output.splitlines():
        if "Open" in line and "->" in line:
            port = line.split("->")[1].strip().split()[0]
            if "/" in port:
                ports.append(port.split("/")[0])
    return ports

def run_nmap_deep(target, ports):
    """Deep service/version/OS detection on discovered ports"""
    port_string = ",".join(ports[:20])  # limit to top 20 to stay fast
    cmd = [
        "nmap",
        "-sV", "-sC", "-O", "--version-intensity", "7",
        "-p", port_string,
        "-oN", "-",  # stdout
        target
    ]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        return result.stdout
    except Exception as e:
        return f"Nmap deep scan failed: {e}"

def generate_report(target, rustscan_out, nmap_out, open_ports):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report = {
        "tool": "ShadowForge Recon v2",
        "timestamp": datetime.now().isoformat(),
        "target": target,
        "phase1": "RustScan (fast discovery)",
        "open_ports_found": len(open_ports),
        "ports": open_ports,
        "phase2": "Nmap deep scan (-sV -sC -O)",
        "rustscan_raw": rustscan_out,
        "nmap_raw": nmap_out,
        "report_file": f"recon_{target}_{timestamp}.json"
    }
    
    report_path = REPORT_DIR / f"recon_{target}_{timestamp}.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    
    return report_path

def main(target=None):
    if not target:
        print("[!] No target provided. Usage: python main.py recon 192.168.1.1")
        return
    
    print(f"[ShadowForge] Launching recon against {target}...")
    
    # Phase 1: RustScan
    print("[1] RustScan – speed run...")
    rust_out = run_rustscan(target)
    if not rust_out:
        print("[!] RustScan failed. Running pure Nmap top 1000...")
        nmap_full = subprocess.run(
            ["nmap", "-sV", "--top-ports", "1000", "-oG", "-", target],
            capture_output=True, text=True, shell=True
        ).stdout
        open_ports = [line.split()[1] for line in nmap_full.splitlines() if "Open" in line]
    else:
        open_ports = extract_open_ports(rust_out)
        print(f"[+] RustScan found {len(open_ports)} open ports: {', '.join(open_ports[:10])}{'...' if len(open_ports)>10 else ''}")
    
    if not open_ports:
        print("[!] No open ports found. Target may be down or filtered.")
        return
    
    # Phase 2: Nmap deep
    print("[2] Nmap deep dive – services, scripts, OS...")
    nmap_deep = run_nmap_deep(target, open_ports)
    
    # Generate final report
    report_file = generate_report(target, rust_out or "RustScan failed", nmap_deep, open_ports)
    print(f"[+] Recon complete. Report saved: {report_file}")

# Remove the old if __name__ block completely
# Keep only the def main(target=None): version above