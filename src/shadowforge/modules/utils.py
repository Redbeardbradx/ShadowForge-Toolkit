#!/usr/bin/env python3
import subprocess
import json
import argparse

def enrich_services(scan_output):
    services = [line for line in scan_output.split('\n') if '/tcp open' in line]
    return [{'service': line.split('open ')[1].split(' ')[0], 'version': line.split('open ')[1].split(' ')[1]} for line in services]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='ShadowForge Recon')
    parser.add_argument('--target', required=True)
    args = parser.parse_args()
    
    result = run_nmap_scan(args.target)
    print(json.dumps(result, indent=2))