"""Validation and parsing tests. These do not use the network or an API key."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from shadowforge.selfcheck import NOTICE
from shadowforge.selfcheck.cli import build_parser, main
from shadowforge.selfcheck.config import (
    parse_concurrency,
    parse_timeout,
    resolve_output_dir,
    safe_slug,
)
from shadowforge.selfcheck.email_check import (
    assess_email,
    lookup_mx,
    parse_hibp_response,
    validate_email,
)
from shadowforge.selfcheck.name_check import (
    assess_name,
    build_name_query,
    canonical_url,
    dedupe_results,
    manual_search_links,
    parse_duckduckgo_html,
    validate_location,
    validate_name,
)
from shadowforge.selfcheck.output import write_json
from shadowforge.selfcheck.present import hibp_summary, presentation
from shadowforge.selfcheck.sites import profile_url, select_sites
from shadowforge.selfcheck.username_check import (
    assess_username,
    classify,
    validate_username,
)

ROOT = Path(__file__).resolve().parents[3]

DDG_HTML = """
<html><body>
<a class="result__a" href="//duckduckgo.com/l/?uddg=https%3A%2F%2Fexample.com%2Fabout&amp;rut=1">Ada Lovelace</a>
<a class="result__a" href="https://duckduckgo.com/l/?uddg=https%3A%2F%2Fwww.example.com%2Fabout&amp;rut=2">Duplicate</a>
<a class="result__a" href="https://other.example/page">Other Page</a>
<a class="result__a" href="https://duckduckgo.com/y.js?ad=1">Skip ad</a>
<a class="other" href="https://ignored.example/">Ignored</a>
</body></html>
"""


def test_email_validation_normalizes_and_rejects_bad_syntax():
    valid = validate_email("  You@Example.com ")
    assert valid["valid"] is True
    assert valid["normalized"] == "you@example.com"
    assert valid["domain"] == "example.com"
    assert validate_email("you@example.com")["valid"] is True
    assert validate_email("not an email")["valid"] is False
    assert validate_email("a@localhost")["valid"] is False
    assert validate_email("a..b@example.com")["valid"] is False
    assert validate_email("")["valid"] is False
    assert validate_email("user@sub.example.co.uk")["valid"] is True


def test_hibp_response_parsing():
    missing = parse_hibp_response(404, "")
    assert missing == {"checked": True, "breached": False, "breaches": [], "reason": None}

    parsed = parse_hibp_response(
        200,
        json.dumps(
            [
                {
                    "Name": "Example",
                    "Title": "Example Breach",
                    "BreachDate": "2020-01-01",
                    "DataClasses": ["Email addresses"],
                }
            ]
        ),
    )
    assert parsed["breached"] is True
    assert parsed["breaches"][0]["name"] == "Example"
    assert parsed["breaches"][0]["data_classes"] == ["Email addresses"]

    names = parse_hibp_response(200, json.dumps(["Adobe"]))
    assert names["breaches"][0]["name"] == "Adobe"

    assert parse_hibp_response(401, "")["checked"] is False
    assert "401" in parse_hibp_response(401, "")["reason"]
    assert "429" in parse_hibp_response(429, "")["reason"]
    assert parse_hibp_response(200, "{")["checked"] is False

    many = parse_hibp_response(200, json.dumps(["Breach"] * 51))
    assert len(many["breaches"]) == 50
    assert many["truncated"] is True


def test_email_assessment_skips_breach_check_without_key_and_hides_key():
    class Record:
        exchange = "mx.example.com."

    def resolver(domain, kind):
        assert domain == "example.com"
        assert kind == "MX"
        return [Record()]

    skipped = assess_email("you@example.com", api_key=None, resolver=resolver)
    assert skipped["hibp"]["checked"] is False
    assert "HIBP_API_KEY" in skipped["hibp"]["reason"]
    assert skipped["mx"]["hosts"] == ["mx.example.com"]

    def fetch(email, api_key, timeout):
        assert api_key == "super-secret-value"
        assert "super-secret-value" not in email
        return (
            200,
            json.dumps(
                [{"Name": "Example", "Title": "Example", "BreachDate": "2020-01-01", "DataClasses": []}]
            ),
            None,
        )

    found = assess_email(
        "You@Example.com",
        api_key="super-secret-value",
        fetch=fetch,
        resolver=resolver,
    )
    assert "super-secret-value" not in json.dumps(found)
    assert found["email"] == "you@example.com"
    assert found["hibp"]["breached"] is True
    assert hibp_summary(found["hibp"]) == "1 breach found."


def test_null_mx_is_not_a_mail_host():
    class NullRecord:
        exchange = "."

    result = lookup_mx("example.com", resolver=lambda domain, kind: [NullRecord()])
    assert result["checked"] is True
    assert result["ok"] is False
    assert result["hosts"] == []


def test_invalid_email_does_not_query_dns_or_hibp():
    def fetch(*_args):
        raise AssertionError("HIBP should not be called")

    def resolver(*_args):
        raise AssertionError("DNS should not be called")

    payload = assess_email("nope", api_key="secret", fetch=fetch, resolver=resolver)
    assert payload["valid"] is False
    assert "secret" not in json.dumps(payload)


def test_username_validation_and_classification():
    assert validate_username("good.name_1")["valid"] is True
    assert validate_username("a")["valid"] is True
    assert validate_username("bad name")["valid"] is False
    assert validate_username("../etc")["valid"] is False
    assert validate_username("-lead")["valid"] is False
    assert validate_username("a" * 65)["valid"] is False

    site = {"trust_200": True, "missing_markers": ["nobody on Reddit goes by that name"]}
    assert classify(404, "", site) == "not_found"
    assert classify(200, "profile", site) == "found"
    assert classify(200, "Nobody on Reddit goes by that name", site) == "not_found"
    assert classify(429, "", site) == "unknown"
    assert classify(503, "", site) == "error"
    assert classify(None, "", site, error="timed out") == "error"

    hn = {"trust_200": False, "missing_markers": ["No such user."], "found_markers": ["created:"]}
    assert classify(200, "user created: 2020", hn) == "found"
    assert classify(200, "No such user.", hn) == "not_found"
    assert classify(200, "login wall", hn) == "unknown"


def test_username_check_uses_profile_urls_and_isolates_site_errors():
    catalog = [
        {"name": "GitHub", "url": "https://github.com/{username}", "trust_200": True},
        {"name": "GitLab", "url": "https://gitlab.com/{username}", "trust_200": True},
        {"name": "PyPI", "url": "https://pypi.org/user/{username}", "trust_200": True},
    ]

    def fetch(url):
        if "github.com" in url:
            return {"status_code": 200, "text": "ok", "error": None, "final_url": url}
        if "gitlab.com" in url:
            return {"status_code": 429, "text": "", "error": None, "final_url": url}
        raise RuntimeError("down")

    payload = assess_username("octocat", fetch=fetch, sites=catalog, workers=2)
    by_site = {row["site"]: row for row in payload["results"]}
    assert payload["valid"] is True
    assert by_site["GitHub"]["status"] == "found"
    assert by_site["GitHub"]["url"] == "https://github.com/octocat"
    assert by_site["GitLab"]["status"] == "unknown"
    assert by_site["GitLab"]["detail"] == "rate limited"
    assert by_site["PyPI"]["status"] == "error"
    assert payload["counts"]["found"] == 1

    hidden = presentation(payload, show_all=False)[0]
    assert all(row[1] != "not_found" for row in hidden["rows"])

    refused = assess_username("bad name", fetch=fetch, sites=catalog)
    assert refused["valid"] is False
    assert refused["results"] == []


def test_site_selection_and_profile_url():
    chosen = select_sites(["github", "PyPI"])
    assert [site["name"] for site in chosen] == ["GitHub", "PyPI"]
    with pytest.raises(ValueError):
        select_sites(["not-a-site"])
    assert profile_url(
        {"url": "https://github.com/{username}"},
        "octocat",
    ) == "https://github.com/octocat"
    assert len(select_sites(None)) >= 20


def test_name_validation_query_and_result_parsing():
    assert validate_name("  Ada   Lovelace ")["normalized"] == "Ada Lovelace"
    assert validate_name("José María")["valid"] is True
    assert validate_name("O'Brien-Smith")["valid"] is True
    assert validate_name("A")["valid"] is False
    assert validate_name("site:example.com")["valid"] is False
    assert validate_name('Ada "quoted"')["valid"] is False
    assert validate_location("São Paulo")["valid"] is True
    assert validate_location("x")["valid"] is False

    assert build_name_query("Ada Lovelace", "London") == '"Ada Lovelace" London'
    links = manual_search_links('"Ada Lovelace" London')
    assert "duckduckgo.com" in links[0]["url"]
    assert "%22Ada+Lovelace%22+London" in links[0]["url"]
    assert "bing.com" in links[1]["url"]

    parsed = dedupe_results(parse_duckduckgo_html(DDG_HTML))
    assert [(item["title"], canonical_url(item["url"])) for item in parsed] == [
        ("Ada Lovelace", "https://example.com/about"),
        ("Other Page", "https://other.example/page"),
    ]

    def fetch_html(query, timeout):
        assert query == '"Ada Lovelace" London'
        assert timeout == 8
        return 200, DDG_HTML, None

    payload = assess_name("Ada Lovelace", location="London", fetch_html=fetch_html)
    assert payload["valid"] is True
    assert len(payload["results"]) == 2
    assert payload["search_links"]

    blocked = assess_name(
        "Ada Lovelace",
        fetch_html=lambda query, timeout: (429, "", "rate limited"),
    )
    assert blocked["results"] == []
    assert blocked["search_error"] == "rate limited"
    assert blocked["search_links"]

    rejected = assess_name("site:example.com")
    assert rejected["valid"] is False
    assert rejected["search_links"] == []


def test_output_writer_and_directory_precedence(tmp_path):
    moment = datetime(2026, 10, 4, 19, 0, tzinfo=timezone.utc)
    path = write_json(
        tmp_path,
        "email",
        "you@example.com",
        {"email": "you@example.com", "notice": NOTICE},
        now=moment,
    )
    assert path.name == "selfcheck-email-you_example.com-20261004T190000Z.json"
    assert json.loads(path.read_text(encoding="utf-8"))["notice"] == NOTICE
    assert safe_slug("..") == "result"
    assert safe_slug("../etc") == "etc"

    cli_dir = tmp_path / "cli"
    env_dir = tmp_path / "env"
    assert resolve_output_dir(
        str(cli_dir),
        environ={"SHADOWFORGE_OUTPUT_DIR": str(env_dir)},
        home=tmp_path,
    ) == cli_dir
    assert resolve_output_dir(
        None,
        environ={"SHADOWFORGE_OUTPUT_DIR": str(env_dir)},
        home=tmp_path,
    ) == env_dir
    assert resolve_output_dir(None, environ={}, home=tmp_path) == (
        tmp_path / ".local" / "share" / "shadowforge" / "output"
    )


def test_limits_and_help_text():
    assert parse_concurrency("5") == 5
    with pytest.raises(ValueError):
        parse_concurrency("11")
    with pytest.raises(ValueError):
        parse_timeout("0")
    help_text = build_parser().format_help()
    assert "YOUR OWN" in help_text
    assert "shadowforge selfcheck email --email you@example.com --i-own-this" in help_text
    assert "shadowforge selfcheck username --username YOUR_USERNAME --i-own-this" in help_text
    assert 'shadowforge selfcheck name --name "Your Name" --i-own-this' in help_text


def test_username_help_exits_cleanly():
    with pytest.raises(SystemExit) as caught:
        build_parser().parse_args(["selfcheck", "username", "--help"])
    assert caught.value.code == 0


def test_cli_refuses_to_run_without_ownership_flag():
    with pytest.raises(SystemExit) as caught:
        main(["selfcheck", "username", "--username", "someone"])
    assert caught.value.code == 2


def test_cli_writes_result_without_network(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(
        "shadowforge.selfcheck.cli.run_check",
        lambda args: {
            "kind": "name",
            "valid": True,
            "name": "Ada Lovelace",
            "notice": NOTICE,
            "results": [{"title": "Bio", "url": "https://example.com/ada"}],
            "search_links": [{"source": "DuckDuckGo", "url": "https://duckduckgo.com/?q=test"}],
            "search_error": None,
        },
    )
    code = main(
        [
            "selfcheck",
            "name",
            "--name",
            "Ada Lovelace",
            "--i-own-this",
            "--output-dir",
            str(tmp_path),
            "--format",
            "json",
        ]
    )
    assert code == 0
    saved = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert saved["confirmed_own_identifier"] is True
    assert "Ada Lovelace" in capsys.readouterr().out


def test_invalid_email_exits_without_network(tmp_path):
    code = main(
        [
            "selfcheck",
            "email",
            "--email",
            "nope",
            "--i-own-this",
            "--output-dir",
            str(tmp_path),
            "--format",
            "json",
        ]
    )
    assert code == 2
    saved = json.loads(next(tmp_path.glob("*.json")).read_text(encoding="utf-8"))
    assert saved["valid"] is False


def test_selfcheck_does_not_import_attack_modules():
    import sys

    forbidden = [
        "shadowforge.payloads",
        "shadowforge.modules.payloads",
        "shadowforge.modules.auto",
        "shadowforge.modules.modules.cleanse",
    ]
    for name in forbidden:
        assert name not in sys.modules


def test_packaging_entry_point_is_selfcheck_only():
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'shadowforge = "shadowforge.selfcheck.cli:main"' in text
    assert "shadowforge.main:main" not in text
    assert "shadowforge.main:cli_entry" not in text
    assert not (ROOT / "setup.py").exists()
