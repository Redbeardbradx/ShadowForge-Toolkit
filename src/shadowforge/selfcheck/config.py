"""Paths, environment variables, and numeric limits."""

from __future__ import annotations

import os
import re
from pathlib import Path

HIBP_API_KEY_ENV = "HIBP_API_KEY"
OUTPUT_DIR_ENV = "SHADOWFORGE_OUTPUT_DIR"

DEFAULT_TIMEOUT = 8.0
MIN_TIMEOUT = 1.0
MAX_TIMEOUT = 30.0

DEFAULT_CONCURRENCY = 5
MIN_CONCURRENCY = 1
MAX_CONCURRENCY = 10

_SLUG_RE = re.compile(r"[^A-Za-z0-9._-]+")


def hibp_api_key(environ: dict | None = None) -> str | None:
    """Return the HIBP key, or None when it is unset. Never invent a key."""
    env = os.environ if environ is None else environ
    value = str(env.get(HIBP_API_KEY_ENV, "")).strip()
    return value or None


def resolve_output_dir(
    explicit: str | None = None,
    *,
    environ: dict | None = None,
    home: Path | None = None,
) -> Path:
    """Choose an output directory and create it.

    Precedence is the CLI flag, then SHADOWFORGE_OUTPUT_DIR, then
    ~/.local/share/shadowforge/output.
    """
    env = os.environ if environ is None else environ
    if explicit:
        path = Path(explicit).expanduser()
    elif str(env.get(OUTPUT_DIR_ENV, "")).strip():
        path = Path(str(env[OUTPUT_DIR_ENV])).expanduser()
    else:
        base = home if home is not None else Path.home()
        path = base / ".local" / "share" / "shadowforge" / "output"
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_slug(value: str) -> str:
    """Make a filename fragment that cannot be a parent directory."""
    slug = _SLUG_RE.sub("_", value).strip("._")
    if not slug or slug in {".", ".."}:
        return "result"
    return slug[:60]


def parse_timeout(value: str) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("timeout must be a number of seconds") from exc
    if number < MIN_TIMEOUT or number > MAX_TIMEOUT:
        raise ValueError(
            f"timeout must be between {MIN_TIMEOUT:g} and {MAX_TIMEOUT:g} seconds"
        )
    return number


def parse_concurrency(value: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("concurrency must be an integer") from exc
    if number < MIN_CONCURRENCY or number > MAX_CONCURRENCY:
        raise ValueError(
            f"concurrency must be between {MIN_CONCURRENCY} and {MAX_CONCURRENCY}"
        )
    return number
