"""Aggregate the first page of public search results for your own name."""

from __future__ import annotations

from html.parser import HTMLParser
from urllib.parse import parse_qs, quote_plus, unquote, urlparse

import requests

from shadowforge.selfcheck import NOTICE
from shadowforge.selfcheck.http_client import build_session

_DDG_HTML = "https://html.duckduckgo.com/html/"
_MAX_RESULTS = 25
_MARKS = set(" .'’-")


def _clean_text(value: str) -> str:
    return " ".join(str(value).replace("\u200b", "").split())


def _valid_label(value: str, *, minimum: int, maximum: int) -> bool:
    if not minimum <= len(value) <= maximum:
        return False
    if not value[0].isalpha():
        return False
    return all(char.isalpha() or char in _MARKS for char in value)


def validate_name(value: str) -> dict:
    name = _clean_text(value)
    if not _valid_label(name, minimum=2, maximum=120):
        return {
            "valid": False,
            "normalized": None,
            "error": (
                "Name must be 2-120 characters and may contain letters, spaces, "
                "apostrophes, periods, and hyphens only."
            ),
        }
    return {"valid": True, "normalized": name, "error": None}


def validate_location(value: str) -> dict:
    location = _clean_text(value)
    if not location:
        return {"valid": True, "normalized": None, "error": None}
    if not _valid_label(location, minimum=2, maximum=80):
        return {
            "valid": False,
            "normalized": None,
            "error": (
                "Location must be 2-80 characters and may contain letters, spaces, "
                "apostrophes, periods, and hyphens only."
            ),
        }
    return {"valid": True, "normalized": location, "error": None}


def build_name_query(name: str, location: str | None = None) -> str:
    query = f'"{name}"'
    if location:
        query = f"{query} {location}"
    return query


def manual_search_links(query: str) -> list[dict]:
    encoded = quote_plus(query)
    return [
        {"source": "DuckDuckGo", "url": f"https://duckduckgo.com/?q={encoded}"},
        {"source": "Bing", "url": f"https://www.bing.com/search?q={encoded}"},
    ]


def canonical_url(url: str) -> str:
    parsed = urlparse(url)
    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]
    path = parsed.path.rstrip("/") or "/"
    return f"{parsed.scheme.lower()}://{host}{path}"


def decode_result_href(href: str) -> str | None:
    if not href:
        return None
    if href.startswith("//"):
        href = "https:" + href
    parsed = urlparse(href)
    host = parsed.netloc.lower()
    if host.endswith("duckduckgo.com") and parsed.path.startswith("/l/"):
        target = (parse_qs(parsed.query).get("uddg") or [None])[0]
        if not target:
            return None
        parsed = urlparse(unquote(target))
    if parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc.lower().endswith("duckduckgo.com"):
        return None
    return parsed._replace(fragment="").geturl()


class _ResultParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._capture = False
        self._href = ""
        self._parts: list[str] = []
        self.results: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() != "a":
            return
        attr = {key.lower(): value or "" for key, value in attrs}
        classes = attr.get("class", "").split()
        if "result__a" not in classes:
            return
        self._capture = True
        self._href = attr.get("href", "")
        self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._capture:
            return
        title = " ".join("".join(self._parts).split())
        url = decode_result_href(self._href)
        if title and url:
            self.results.append({"title": title, "url": url, "source": "DuckDuckGo"})
        self._capture = False
        self._href = ""
        self._parts = []


def parse_duckduckgo_html(html: str) -> list[dict]:
    parser = _ResultParser()
    parser.feed(html or "")
    parser.close()
    return parser.results


def dedupe_results(items: list[dict]) -> list[dict]:
    seen: set[str] = set()
    unique: list[dict] = []
    for item in items:
        key = canonical_url(item["url"])
        if key in seen:
            continue
        seen.add(key)
        unique.append(item)
    return unique


def _default_fetch_html(query: str, timeout: float):
    try:
        response = build_session().get(
            _DDG_HTML,
            params={"q": query},
            timeout=timeout,
            headers={"Accept": "text/html"},
        )
    except requests.Timeout:
        return None, "", "Search request timed out."
    except requests.RequestException as exc:
        return None, "", f"Search network error: {exc.__class__.__name__}."
    if response.status_code == 429:
        return 429, "", "Search engine rate limit reached (HTTP 429). Open the search links instead."
    if response.status_code != 200:
        return (
            response.status_code,
            "",
            f"Search engine returned HTTP {response.status_code}. Open the search links instead.",
        )
    return response.status_code, response.text, None


def assess_name(
    name: str,
    location: str | None = None,
    *,
    timeout: float = 8.0,
    fetch_html=None,
) -> dict:
    parsed_name = validate_name(name)
    if not parsed_name["valid"]:
        return _invalid_name(parsed_name["error"])
    parsed_location = validate_location(location or "")
    if not parsed_location["valid"]:
        return _invalid_name(parsed_location["error"])
    query = build_name_query(parsed_name["normalized"], parsed_location["normalized"])
    links = manual_search_links(query)
    payload = {
        "kind": "name",
        "notice": NOTICE,
        "valid": True,
        "name": parsed_name["normalized"],
        "location": parsed_location["normalized"],
        "query": query,
        "search_links": links,
        "results": [],
        "search_error": None,
    }
    fetcher = fetch_html or _default_fetch_html
    try:
        status, html, error = fetcher(query, timeout)
    except Exception as exc:
        status, html, error = None, "", f"Search request failed: {exc.__class__.__name__}."
    if error or status != 200:
        payload["search_error"] = error or (
            f"Search engine returned HTTP {status}. Open the search links instead."
        )
        return payload
    results = dedupe_results(parse_duckduckgo_html(html))[:_MAX_RESULTS]
    payload["results"] = results
    if not results:
        payload["search_error"] = (
            "No public results were parsed. The search engine may have blocked "
            "the automated request. Open the search links to review them yourself."
        )
    return payload


def _invalid_name(error: str) -> dict:
    return {
        "kind": "name",
        "notice": NOTICE,
        "valid": False,
        "name": None,
        "location": None,
        "query": None,
        "search_links": [],
        "results": [],
        "search_error": error,
        "error": error,
    }
