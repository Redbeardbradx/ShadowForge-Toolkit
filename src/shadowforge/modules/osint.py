#!/usr/bin/env python3
"""
ShadowForge-Toolkit – modules/osint.py
Passive OSINT collection: TheHarvester (emails, subdomains, hosts) + optional Shodan
Lab-only. Save output for recon chain import.
"""
import argparse
import subprocess
import json
import os
from termcolor import colored

def harvester_collect(domain: str, sources: str = "all", limit: int = 500):
    print(colored(f"[+] TheHarvester passive collection on {domain}", "yellow"))
    output_file = f"results/{domain}_harvester.json"
    os.makedirs("results", exist_ok=True)
    
    cmd = [
        "theharvester",
        "-d", domain,
        "-l", str(limit),
        "-b", sources,
        "-f", output_file
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(colored(result.stdout.strip(), "green"))
        
        with open(output_file, "r") as f:
            data = json.load(f)
        
        emails = data.get("emails", [])
        hosts = data.get("hosts", [])
        subdomains = list(data.get("subdomains", []))
        
        print(colored(f"[+] Collected: {len(emails)} emails | {len(hosts)} hosts | {len(subdomains)} subdomains", "green"))
        return {"emails": emails, "hosts": hosts, "subdomains": subdomains}
        
    except subprocess.CalledProcessError as e:
        print(colored(f"[-] TheHarvester failed: {e.stderr.strip()}", "red"))
        return {}

def main(query: str, type: str = "name"):
    if type == "domain":  # Align with main.py routing if needed
        harvester_collect(query)
    else:
        print(colored("[-] Only domain OSINT implemented in v0.1 – extend for name/phone", "yellow"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowForge OSINT Collector")
    parser.add_argument("query", help="Domain for passive collection")
    args = parser.parse_args()
    harvester_collect(args.query)