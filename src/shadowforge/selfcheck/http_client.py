"""One shared HTTP session for the self-check commands.

Retries cover brief server failures. A 429 from a site or API is reported
to the caller and is not retried in a loop.
"""

from __future__ import annotations

import threading

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from shadowforge.selfcheck.config import MAX_CONCURRENCY

USER_AGENT = (
    "ShadowForge-SelfCheck/0.2 "
    "(personal exposure self-assessment; checks identifiers the operator owns)"
)

_THREAD_LOCAL = threading.local()


def build_session() -> requests.Session:
    retry_kwargs = dict(
        total=1,
        connect=1,
        read=1,
        backoff_factor=0.5,
        status_forcelist=(502, 503, 504),
        respect_retry_after_header=True,
    )
    try:
        retry = Retry(allowed_methods=frozenset(["GET", "HEAD", "POST"]), **retry_kwargs)
    except TypeError:  # urllib3 < 1.26
        retry = Retry(method_whitelist=frozenset(["GET", "HEAD", "POST"]), **retry_kwargs)
    adapter = HTTPAdapter(max_retries=retry, pool_maxsize=MAX_CONCURRENCY)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/json;q=0.9,*/*;q=0.8",
        }
    )
    return session


def thread_session() -> requests.Session:
    """Return a session private to this thread.

    requests.Session is not safe to share across concurrent workers.
    """
    session = getattr(_THREAD_LOCAL, "session", None)
    if session is None:
        session = build_session()
        _THREAD_LOCAL.session = session
    return session


def fetch_url(url: str, timeout: float) -> dict:
    """GET a public URL. Errors become a result dict instead of a crash."""
    try:
        response = thread_session().get(url, timeout=timeout, allow_redirects=True)
    except requests.Timeout:
        return {"status_code": None, "text": "", "error": "timed out", "final_url": url}
    except requests.RequestException as exc:
        return {
            "status_code": None,
            "text": "",
            "error": f"network error: {exc.__class__.__name__}",
            "final_url": url,
        }
    return {
        "status_code": response.status_code,
        "text": response.text[:200_000],
        "error": None,
        "final_url": str(response.url),
    }
