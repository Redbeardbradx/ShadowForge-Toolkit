"""See which public sites have a profile for a username you own."""

from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, as_completed

from shadowforge.selfcheck import NOTICE
from shadowforge.selfcheck.config import MAX_CONCURRENCY
from shadowforge.selfcheck.sites import SITES, profile_url, select_sites

_USERNAME_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]{0,63})$")


def validate_username(value: str) -> dict:
    username = str(value).strip()
    if not username:
        return {"valid": False, "normalized": None, "error": "Username is empty."}
    if any(char.isspace() for char in username):
        return {"valid": False, "normalized": None, "error": "Username cannot contain spaces."}
    if not _USERNAME_RE.fullmatch(username):
        return {
            "valid": False,
            "normalized": None,
            "error": (
                "Username must be 1-64 characters and use only letters, digits, "
                "periods, underscores, and hyphens. It must start with a letter or digit."
            ),
        }
    return {"valid": True, "normalized": username, "error": None}


def classify(status_code: int | None, body: str, site: dict, error: str | None = None) -> str:
    """Map an HTTP result to found, not_found, unknown, or error."""
    if error or status_code is None:
        return "error"
    if status_code in (404, 410):
        return "not_found"
    if status_code in (401, 403, 429):
        return "unknown"
    if status_code >= 500:
        return "error"
    if status_code != 200:
        return "unknown"
    folded = (body or "").casefold()
    for marker in site.get("missing_markers") or []:
        if str(marker).casefold() in folded:
            return "not_found"
    if site.get("trust_200"):
        return "found"
    for marker in site.get("found_markers") or []:
        if str(marker).casefold() in folded:
            return "found"
    return "unknown"


def detail_for(status_code: int | None, error: str | None) -> str:
    if error:
        return error
    if status_code == 429:
        return "rate limited"
    if status_code in (401, 403):
        return "site blocked the check"
    return ""


def interpret_site(site: dict, username: str, fetched: dict) -> dict:
    return {
        "site": site["name"],
        "url": profile_url(site, username),
        "final_url": fetched.get("final_url") or profile_url(site, username),
        "status": classify(
            fetched.get("status_code"),
            fetched.get("text") or "",
            site,
            error=fetched.get("error"),
        ),
        "http_status": fetched.get("status_code"),
        "detail": detail_for(fetched.get("status_code"), fetched.get("error")),
    }


def summarize(results: list[dict]) -> dict:
    counts = {"found": 0, "not_found": 0, "unknown": 0, "error": 0}
    for row in results:
        key = row.get("status")
        if key in counts:
            counts[key] += 1
    return counts


def assess_username(
    username: str,
    *,
    fetch,
    sites: list[dict] | None = None,
    site_names: list[str] | None = None,
    workers: int = 5,
) -> dict:
    parsed = validate_username(username)
    if not parsed["valid"]:
        return {
            "kind": "username",
            "notice": NOTICE,
            "valid": False,
            "username": None,
            "error": parsed["error"],
            "counts": summarize([]),
            "results": [],
        }
    try:
        chosen = select_sites(site_names, sites if sites is not None else SITES)
    except ValueError as exc:
        return {
            "kind": "username",
            "notice": NOTICE,
            "valid": False,
            "username": parsed["normalized"],
            "error": str(exc),
            "counts": summarize([]),
            "results": [],
        }
    worker_count = max(1, min(workers, len(chosen), MAX_CONCURRENCY))
    results: list[dict] = []
    with ThreadPoolExecutor(max_workers=worker_count) as pool:
        futures = [
            pool.submit(_check_one, site, parsed["normalized"], fetch) for site in chosen
        ]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda row: (row["status"] != "found", row["site"].casefold()))
    return {
        "kind": "username",
        "notice": NOTICE,
        "valid": True,
        "username": parsed["normalized"],
        "error": None,
        "counts": summarize(results),
        "results": results,
    }


def _check_one(site: dict, username: str, fetch) -> dict:
    url = profile_url(site, username)
    try:
        fetched = fetch(url)
    except Exception as exc:  # one site should not abort the others
        fetched = {
            "status_code": None,
            "text": "",
            "error": f"network error: {exc.__class__.__name__}",
            "final_url": url,
        }
    if not isinstance(fetched, dict):
        fetched = {
            "status_code": None,
            "text": "",
            "error": "fetcher returned an unexpected result",
            "final_url": url,
        }
    return interpret_site(site, username, fetched)
