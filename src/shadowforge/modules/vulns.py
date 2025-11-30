import nvdlib
from typing import List, Dict

def match_cves(version: str) -> List[Dict]:
    """
    Raid NVD for CVEs on service version. Ethical: OSINT only—suggest, don't exploit.
    Returns list of dicts: {'id': 'CVE-2024-6387', 'severity': 'HIGH', 'description': 'snippet'}.
    """
    if not version:
        return []
    try:
        results = nvdlib.searchCVE(
            keywordSearch=str(version),
            cvssV3Severity=['HIGH', 'CRITICAL'],
            limit=5
        )
        cves = []
        for cve in results:
            cves.append({
                'id': cve.id,
                'severity': cve.score[2] if cve.score else 'UNKNOWN',
                'description': cve.descriptions[0].value[:100] + '...' if cve.descriptions else 'No desc'
            })
        return cves
    except Exception as e:
        print(f"[red]NVD hunt failed: {e}—check net or rate limit.[/red]")
        return []

def enrich_services(services: List[Dict]) -> List[Dict]:
    """Chain: Add CVEs to each service."""
    for svc in services:
        svc["potential_cves"] = match_cves(svc.get("version", ""))
    return services