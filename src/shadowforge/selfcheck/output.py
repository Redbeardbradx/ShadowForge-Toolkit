"""Write a JSON record of a self-check."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from shadowforge.selfcheck.config import safe_slug


def stamp_payload(payload: dict, *, now: datetime | None = None) -> dict:
    moment = now or datetime.now(timezone.utc)
    stamped = dict(payload)
    stamped["checked_at"] = moment.strftime("%Y-%m-%dT%H:%M:%SZ")
    return stamped


def write_json(
    directory: Path,
    kind: str,
    subject: str,
    payload: dict,
    *,
    now: datetime | None = None,
) -> Path:
    moment = now or datetime.now(timezone.utc)
    filename = (
        f"selfcheck-{kind}-{safe_slug(subject)}-"
        f"{moment.strftime('%Y%m%dT%H%M%SZ')}.json"
    )
    path = directory / filename
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return path
