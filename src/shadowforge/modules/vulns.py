# src/shadowforge/modules/vulns.py
import requests
from typing import List

def match_cves(version: str) -> List[str]:
    """
    Raid NVD for CVEs on service version. Ethical: OSINT only—suggest, don't exploit.
    Returns top 3 CVE IDs (e.g., ["CVE-2024-6387"] for OpenSSH 8.2).
    """
    if not version:
        return []
    try:
        url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?keywordSearch={version.replace(' ', '%20')}"
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            cves = [vuln['cve']['id'] for vuln in data['vulnerabilities'][:3]]
            return cves
        return []
    except requests.RequestException:
        return ["Error: NVD fetch failed—check net or rate limit."]

def enrich_services(services: List[dict]) -> List[dict]:
    """Chain: Add vulns to each service."""
    for svc in services:
        svc["potential_cves"] = match_cves(svc.get("version", ""))
    return services