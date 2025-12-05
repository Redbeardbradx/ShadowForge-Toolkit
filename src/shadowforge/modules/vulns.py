#!/usr/bin/env python3
import json
import argparse
import requests
from .utils import run_nmap  # Shared utils for loop break
def parse_vulns(target, api_key=None):
    scan = run_nmap(target)
    open_ports = [line for line in scan['output'].split('\n') if '/tcp open' in line]
    vulns = []
    for port_line in open_ports:
        port = port_line.split('/')[0]
        # NIST CVE tease (free API—no key needed for basic)
        r = requests.get(f'https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={port}')
        if r.status_code == 200:
            data = r.json()
            cves = [cve['cve']['id'] for cve in data['vulnerabilities'][:3]]
            vulns.append({'port': port, 'cves': cves})
    return {'target': target, 'vulns': vulns, 'scan': scan}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ShadowForge Vulns Parse')
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    
    result = parse_vulns(args.target)
    print(json.dumps(result, indent=2))