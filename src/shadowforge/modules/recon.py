from typing import Optional, Dict, Any
import subprocess
import json
import re
import requests
from typing import Dict, Any
from .utils import enrich_services  # Shared utils for loop break

def run_nmap_scan(target: str, session: Optional[requests.Session] = None) -> Dict[str, Any]:
    """
    Summon nmap -sV on target. Parse ports/services. Ethical: Owned nets only.
    Returns JSON-ready dict: ports, services, vulns tease.
    """
    try:
        # Nmap call: -sV version detect, -oX XML stub (parse later? Keep text for now)
        result = subprocess.run(
            ['nmap', '-sV', '--open', target],  # All ports, open only
            capture_output=True,
            text=True,
            timeout=120  # 2min cap for slow targets
        )
        if result.returncode != 0:
            return {'target': target, 'timestamp': '2025-11-30', 'output': result.stdout, 'enriched': enriched, 'errors':        result.stderr}

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

        # Enrich with CVEs
        services = enrich_services(ports)

        data = {
            "target": target,
            "scan_time": subprocess.run(['date', '+%Y-%m-%d %H:%M:%S'], capture_output=True, text=True).stdout.strip(),
            "ports_open": len(services),
            "services": services,
            "vulns": []  # Tease: Later, match versions to CVE JSON
        }

        # Geocode chain: Free ipinfo.io (no key for basics)
        try:
            if session:
                geo_resp = session.get(f"http://ipinfo.io/{target}/json", timeout=10)
            else:
                geo_resp = requests.get(f"http://ipinfo.io/{target}/json", timeout=10)
            if geo_resp.status_code == 200:
                geo = geo_resp.json()
                data["geo"] = {
                    "ip": geo.get("ip", "Unknown"),
                    "city": geo.get("city", "Unknown"),
                    "loc": geo.get("loc", "No coords"),
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