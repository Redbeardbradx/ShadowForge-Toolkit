"""Syntax, MX, and Have I Been Pwned checks for an email you own."""

from __future__ import annotations

import json
import re
from urllib.parse import quote

import requests

from shadowforge.selfcheck import NOTICE
from shadowforge.selfcheck.http_client import USER_AGENT, build_session

_EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]{1,64}@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)

HIBP_ENDPOINT = "https://haveibeenpwned.com/api/v3/breachedaccount/"
_MISSING_KEY = (
    "HIBP_API_KEY is not set. The breach check was skipped. "
    "Syntax and MX checks still ran. Create a key at "
    "https://haveibeenpwned.com/API/Key and export HIBP_API_KEY."
)


def validate_email(value: str) -> dict:
    """Normalize an email address or explain why it is unusable."""
    raw = " ".join(str(value).split())
    if any(char.isspace() for char in str(value).strip()):
        return _invalid("Email addresses cannot contain spaces.")
    email = raw.strip().lower()
    if not email:
        return _invalid("Email address is empty.")
    if len(email) > 254:
        return _invalid("Email address is longer than 254 characters.")
    if email.count("@") != 1 or ".." in email:
        return _invalid("Email address syntax is invalid.")
    if _EMAIL_RE.fullmatch(email) is None:
        return _invalid("Email address syntax is invalid.")
    domain = email.split("@", 1)[1]
    return {"valid": True, "normalized": email, "domain": domain, "error": None}


def _invalid(message: str) -> dict:
    return {"valid": False, "normalized": None, "domain": None, "error": message}


def lookup_mx(domain: str, timeout: float = 8.0, resolver=None) -> dict:
    """Resolve MX hosts. `resolver(domain, "MX")` is injectable for tests."""
    if resolver is None:
        return _dns_lookup_mx(domain, timeout)
    try:
        answers = resolver(domain, "MX")
    except Exception as exc:
        checked = bool(getattr(exc, "checked", True))
        return {"checked": checked, "ok": False, "hosts": [], "error": str(exc)}
    hosts = _mx_hosts(answers)
    if not hosts:
        return {
            "checked": True,
            "ok": False,
            "hosts": [],
            "error": "No usable MX hosts. A null MX means the domain does not accept mail.",
        }
    return {"checked": True, "ok": True, "hosts": hosts, "error": None}


def _dns_lookup_mx(domain: str, timeout: float) -> dict:
    try:
        import dns.exception
        import dns.resolver
    except ImportError:
        return {
            "checked": False,
            "ok": False,
            "hosts": [],
            "error": "dnspython is not installed, so MX lookup was skipped.",
        }
    resolver = dns.resolver.Resolver()
    resolver.lifetime = timeout
    try:
        answers = resolver.resolve(domain, "MX")
    except dns.resolver.NXDOMAIN:
        return {
            "checked": True,
            "ok": False,
            "hosts": [],
            "error": "Domain does not exist (NXDOMAIN).",
        }
    except dns.resolver.NoAnswer:
        return {
            "checked": True,
            "ok": False,
            "hosts": [],
            "error": "No MX records. Some domains still accept mail via an A record.",
        }
    except dns.exception.DNSException as exc:
        return {
            "checked": False,
            "ok": False,
            "hosts": [],
            "error": f"DNS lookup failed: {exc.__class__.__name__}.",
        }
    hosts = _mx_hosts(answers)
    if not hosts:
        return {
            "checked": True,
            "ok": False,
            "hosts": [],
            "error": "No usable MX hosts. A null MX means the domain does not accept mail.",
        }
    return {"checked": True, "ok": True, "hosts": hosts, "error": None}


def _mx_hosts(answers) -> list[str]:
    hosts = set()
    for item in answers:
        host = str(getattr(item, "exchange", item)).rstrip(".")
        if host:
            hosts.add(host)
    return sorted(hosts)


def parse_hibp_response(status_code: int | None, body: str) -> dict:
    """Turn an HIBP breached-account response into a small result."""
    if status_code is None:
        return _hibp_skipped("HIBP request failed before a response arrived.")
    if status_code == 404:
        return {"checked": True, "breached": False, "breaches": [], "reason": None}
    if status_code == 401:
        return _hibp_skipped("HIBP rejected the API key (HTTP 401).")
    if status_code == 403:
        return _hibp_skipped("HIBP refused the request (HTTP 403).")
    if status_code == 429:
        return _hibp_skipped("HIBP rate limit reached (HTTP 429). Wait and try again later.")
    if status_code == 503:
        return _hibp_skipped("HIBP is unavailable (HTTP 503). Try again later.")
    if status_code != 200:
        return _hibp_skipped(f"HIBP returned HTTP {status_code}.")
    try:
        data = json.loads(body or "null")
    except json.JSONDecodeError:
        return _hibp_skipped("HIBP returned a response that was not valid JSON.")
    if not isinstance(data, list):
        return _hibp_skipped("HIBP returned an unexpected JSON shape.")
    breaches = []
    for item in data[:50]:
        if isinstance(item, str):
            breaches.append(
                {"name": item, "title": None, "breach_date": None, "data_classes": []}
            )
        elif isinstance(item, dict):
            classes = item.get("DataClasses") or []
            breaches.append(
                {
                    "name": item.get("Name"),
                    "title": item.get("Title"),
                    "breach_date": item.get("BreachDate"),
                    "data_classes": [str(entry) for entry in classes],
                }
            )
    return {
        "checked": True,
        "breached": bool(breaches),
        "breaches": breaches,
        "truncated": len(data) > 50,
        "reason": None,
    }


def _hibp_skipped(reason: str) -> dict:
    return {"checked": False, "breached": None, "breaches": [], "reason": reason}


def check_hibp(email: str, api_key: str | None, fetch=None, timeout: float = 8.0) -> dict:
    if not api_key:
        return _hibp_skipped(_MISSING_KEY)
    if fetch is None:
        fetch = _default_hibp_fetch
    status, body, error = fetch(email, api_key, timeout)
    if error:
        return _hibp_skipped(error)
    parsed = parse_hibp_response(status, body)
    return parsed


def _default_hibp_fetch(email: str, api_key: str, timeout: float):
    url = HIBP_ENDPOINT + quote(email, safe="")
    try:
        response = build_session().get(
            url,
            params={"truncateResponse": "false"},
            headers={
                "hibp-api-key": api_key,
                "Accept": "application/json",
                "User-Agent": USER_AGENT,
            },
            timeout=timeout,
        )
    except requests.Timeout:
        return None, "", "HIBP request timed out."
    except requests.RequestException as exc:
        return None, "", f"HIBP network error: {exc.__class__.__name__}."
    return response.status_code, response.text, None


def assess_email(
    email: str,
    *,
    api_key: str | None,
    timeout: float = 8.0,
    fetch=None,
    resolver=None,
) -> dict:
    syntax = validate_email(email)
    if not syntax["valid"]:
        return {
            "kind": "email",
            "notice": NOTICE,
            "valid": False,
            "email": None,
            "syntax": syntax,
            "mx": {
                "checked": False,
                "ok": False,
                "hosts": [],
                "error": "Skipped because the email syntax is invalid.",
            },
            "hibp": _hibp_skipped("Skipped because the email syntax is invalid."),
        }
    return {
        "kind": "email",
        "notice": NOTICE,
        "valid": True,
        "email": syntax["normalized"],
        "syntax": syntax,
        "mx": lookup_mx(syntax["domain"], timeout=timeout, resolver=resolver),
        "hibp": check_hibp(syntax["normalized"], api_key, fetch=fetch, timeout=timeout),
    }
