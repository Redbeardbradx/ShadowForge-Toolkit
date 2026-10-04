"""Turn a self-check payload into table rows."""

from __future__ import annotations


def hibp_summary(hibp: dict) -> str:
    if not hibp.get("checked"):
        return hibp.get("reason") or "Breach check was not run."
    if not hibp.get("breached"):
        return "No breaches found for this email."
    count = len(hibp.get("breaches") or [])
    suffix = "breach" if count == 1 else "breaches"
    return f"{count} {suffix} found."


def presentation(payload: dict, *, show_all: bool = False) -> list[dict]:
    """Return one or more tables: title, columns, rows, note."""
    kind = payload.get("kind")
    if kind == "email":
        return [_email_table(payload)]
    if kind == "username":
        return [_username_table(payload, show_all=show_all)]
    if kind == "name":
        return _name_tables(payload)
    return [
        {
            "title": "Self-check",
            "columns": ["Detail"],
            "rows": [[payload.get("error") or "No result"]],
            "note": payload.get("notice") or "",
        }
    ]


def _email_table(payload: dict) -> dict:
    syntax = payload.get("syntax") or {}
    mx = payload.get("mx") or {}
    hibp = payload.get("hibp") or {}
    if syntax.get("valid"):
        syntax_cell = syntax.get("normalized") or "valid"
    else:
        syntax_cell = syntax.get("error") or "invalid"
    if mx.get("ok"):
        mx_cell = ", ".join(mx.get("hosts") or [])
    else:
        mx_cell = mx.get("error") or mx.get("reason") or "not checked"
    rows = [
        ["Syntax", syntax_cell],
        ["MX", mx_cell],
        ["HIBP", hibp_summary(hibp)],
    ]
    for breach in hibp.get("breaches") or []:
        classes = ", ".join(breach.get("data_classes") or [])
        when = breach.get("breach_date") or ""
        detail = " ".join(part for part in (when, classes) if part)
        rows.append([breach.get("title") or breach.get("name") or "Breach", detail])
    return {
        "title": "Your email exposure",
        "columns": ["Check", "Result"],
        "rows": rows,
        "note": "",
    }


def _username_table(payload: dict, *, show_all: bool) -> dict:
    if not payload.get("valid"):
        return {
            "title": "Your username exposure",
            "columns": ["Detail"],
            "rows": [[payload.get("error") or "Invalid username"]],
            "note": "",
        }
    results = payload.get("results") or []
    visible = results if show_all else [row for row in results if row.get("status") != "not_found"]
    rows = [
        [row.get("site"), row.get("status"), row.get("url"), row.get("detail") or ""]
        for row in visible
    ]
    counts = payload.get("counts") or {}
    hidden = "" if show_all else f" Not-found rows are hidden ({counts.get('not_found', 0)})."
    note = (
        f"Found {counts.get('found', 0)}, unknown {counts.get('unknown', 0)}, "
        f"errors {counts.get('error', 0)}.{hidden} "
        "A found row means the public profile URL responded like an existing account. "
        "Open the URL to confirm it is yours."
    )
    if not rows:
        rows = [["No found, unknown, or error rows.", "", "", ""]]
    return {
        "title": "Your username exposure",
        "columns": ["Site", "Status", "URL", "Detail"],
        "rows": rows,
        "note": note,
    }


def _name_tables(payload: dict) -> list[dict]:
    if not payload.get("valid"):
        return [
            {
                "title": "Your name exposure",
                "columns": ["Detail"],
                "rows": [[payload.get("error") or "Invalid name"]],
                "note": "",
            }
        ]
    result_rows = [[item.get("title"), item.get("url")] for item in payload.get("results") or []]
    if not result_rows:
        result_rows = [["No parsed results", payload.get("search_error") or ""]]
    link_rows = [[item.get("source"), item.get("url")] for item in payload.get("search_links") or []]
    note = payload.get("search_error") or ""
    return [
        {
            "title": "Public results for your name",
            "columns": ["Title", "URL"],
            "rows": result_rows,
            "note": note,
        },
        {
            "title": "Open these searches yourself",
            "columns": ["Source", "URL"],
            "rows": link_rows or [["None", ""]],
            "note": "Automated collection is limited to the first public results page.",
        },
    ]
