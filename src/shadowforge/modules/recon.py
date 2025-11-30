# src/shadowforge/modules/recon.py
import subprocess
import json
import re
import requests
from typing import Dict, Any

def run_nmap_scan(target: str) -> Dict[str, Any]:
    """
    Summon nmap -sV on target. Parse ports/services. Ethical: Owned nets only.
    Returns JSON-ready dict: ports, services, vulns tease.
    """
    try:
        # Nmap call: -sV version detect, -oX XML stub (parse later? Keep text for now)
        result = subprocess.run(
            ['nmap', '-sV', '--open', '-p-', target],  # All ports, open only
            capture_output=True,
            text=True,
            timeout=60  # 1min cap—don't hang the raid
        )
        if result.returncode != 0:
            return {"error": f"Nmap failed: {result.stderr}"}

        # Parse stdout: Regex for ports/services (e.g., 80/tcp open http Apache 2.4.41)
        output = result.stdout
        ports = []
        port_pattern = r'(\d+)/tcp\s+open\s+(\S+)\s+(.*)'
        for match in re.finditer(port_pattern, output):
            ports.append({
                "port": match.group(1),
                "protocol": "tcp",
                "service": match.group(2),
                "version": match.group(3).strip()
            })

        data = {
            "target": target,
            "scan_time": subprocess.run(['date', '+%Y-%m-%d %H:%M:%S'], capture_output=True, text=True).stdout.strip(),
            "ports_open": len(ports),
            "services": ports,
            "vulns": []  # Tease: Later, match versions to CVE JSON (e.g., from utils/cve.py)
        }

        # Geocode chain: Free ipinfo.io (no key for basics; upgrade for token)
        try:
            geo_resp = requests.get(f"http://ipinfo.io/{target}/json", timeout=10)
            if geo_resp.status_code == 200:
                geo = geo_resp.json()
                data["geo"] = {
                    "ip": geo.get("ip", "Unknown"),
                    "city": geo.get("city", "Unknown"),
                    "loc": geo.get("loc", "No coords"),  # "40.7608,-111.8910"
                    "org": geo.get("org", "Unknown ISP")
                }
        except requests.RequestException:
            data["geo"] = {"error": "Geocode fetch failed—check net."}

        return data

    except FileNotFoundError:
        return {"error": "Nmap not in PATH—install: apt/yum install nmap or brew install nmap."}
    except Exception as e:
        return {"error": f"Recon raid failed: {str(e)}"}

def output_json(data: Dict[str, Any], filepath: str = None) -> str:
    """Dump to JSON string or file. Colored tease via rich (import in main)."""
    json_str = json.dumps(data, indent=2)
    if filepath:
        with open(filepath, 'w') as f:
            f.write(json_str)
    return json_str

# In main.py subparsers (add to recon_parser):
recon_parser.add_argument('--proxy', choices=['tor'], help='Veil thru TOR')

# In if __name__ for recon:
if args.command == 'recon':
    from .modules.recon import run_nmap_scan
    from .modules.shield.proxy import tor_session  # Only if tor
    session = tor_session() if args.proxy == 'tor' else None
    scan_data = run_nmap_scan(args.target, session=session)  # Pass session to recon

# Update recon.py run_nmap_scan (add param):
def run_nmap_scan(target: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    # ... existing ...
    # In geocode: if session: geo_resp = session.get(f"http://ipinfo.io/{target}/json", timeout=10)
    # else: geo_resp = requests.get(...)
    # ... rest unchanged