"""Command line for checking your own public exposure."""

from __future__ import annotations

import argparse
import json
import sys

from rich.console import Console
from rich.table import Table

from shadowforge.selfcheck import NOTICE
from shadowforge.selfcheck.config import (
    DEFAULT_CONCURRENCY,
    DEFAULT_TIMEOUT,
    parse_concurrency,
    parse_timeout,
    resolve_output_dir,
    hibp_api_key,
)
from shadowforge.selfcheck.email_check import assess_email
from shadowforge.selfcheck.http_client import fetch_url
from shadowforge.selfcheck.name_check import assess_name
from shadowforge.selfcheck.output import stamp_payload, write_json
from shadowforge.selfcheck.present import presentation
from shadowforge.selfcheck.username_check import assess_username

EXAMPLES = """
examples:
  shadowforge selfcheck email --email you@example.com --i-own-this
  shadowforge selfcheck username --username YOUR_USERNAME --i-own-this
  shadowforge selfcheck username --username YOUR_USERNAME --i-own-this --timeout 8 --concurrency 5
  shadowforge selfcheck name --name "Your Name" --i-own-this
  shadowforge selfcheck name --name "Your Name" --location "Your City" --i-own-this --output-dir ./output

Set HIBP_API_KEY to include a Have I Been Pwned breach check for your own email.
Set SHADOWFORGE_OUTPUT_DIR to change the default output directory.
This command is for identifiers that belong to you.
"""


def _timeout_arg(value: str) -> float:
    try:
        return parse_timeout(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _concurrency_arg(value: str) -> int:
    try:
        return parse_concurrency(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def _common() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument(
        "--output-dir",
        default=None,
        help=(
            "Directory for the JSON result. Defaults to SHADOWFORGE_OUTPUT_DIR "
            "or ~/.local/share/shadowforge/output."
        ),
    )
    parser.add_argument(
        "--format",
        choices=("table", "json", "both"),
        default="both",
        help=(
            "both (default) prints a table and writes JSON. "
            "json prints JSON to stdout and writes the same file. "
            "table prints a table and writes JSON."
        ),
    )
    parser.add_argument(
        "--timeout",
        type=_timeout_arg,
        default=DEFAULT_TIMEOUT,
        help=f"Per-request timeout in seconds ({DEFAULT_TIMEOUT:g} default, 30 max).",
    )
    parser.add_argument(
        "--i-own-this",
        action="store_true",
        help="Required. Confirm the identifier belongs to you.",
    )
    return parser


def build_parser() -> argparse.ArgumentParser:
    common = _common()
    parser = argparse.ArgumentParser(
        prog="shadowforge",
        description=NOTICE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    commands = parser.add_subparsers(dest="command", required=True)
    selfcheck = commands.add_parser(
        "selfcheck",
        help="Check your own public exposure",
        description=NOTICE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    checks = selfcheck.add_subparsers(dest="check", required=True)

    email = checks.add_parser(
        "email",
        parents=[common],
        help="Syntax, MX, and HIBP breach check for your own email",
        description=NOTICE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    email.add_argument("--email", required=True, help="Your own email address.")

    username = checks.add_parser(
        "username",
        parents=[common],
        help="Public profile presence for your own username",
        description=NOTICE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    username.add_argument("--username", required=True, help="Your own username.")
    username.add_argument(
        "--concurrency",
        type=_concurrency_arg,
        default=DEFAULT_CONCURRENCY,
        help=f"Parallel site checks ({DEFAULT_CONCURRENCY} default, 10 max).",
    )
    username.add_argument(
        "--sites",
        default=None,
        help="Comma-separated site names to check. Defaults to the built-in list.",
    )
    username.add_argument(
        "--show-all",
        action="store_true",
        help="Include not-found rows in the table. JSON always includes them.",
    )

    name = checks.add_parser(
        "name",
        parents=[common],
        help="Public search results for your own name",
        description=NOTICE,
        epilog=EXAMPLES,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    name.add_argument("--name", required=True, help='Your own name, for example "Ada Lovelace".')
    name.add_argument(
        "--location",
        default=None,
        help="Optional place name to add to the public search, such as a city.",
    )
    return parser


def run_check(args: argparse.Namespace) -> dict:
    if args.check == "email":
        return assess_email(
            args.email,
            api_key=hibp_api_key(),
            timeout=args.timeout,
        )
    if args.check == "username":
        site_names = None
        if args.sites:
            site_names = [part.strip() for part in args.sites.split(",") if part.strip()]
        return assess_username(
            args.username,
            fetch=lambda url: fetch_url(url, args.timeout),
            site_names=site_names,
            workers=args.concurrency,
        )
    if args.check == "name":
        return assess_name(args.name, location=args.location, timeout=args.timeout)
    raise ValueError(f"Unknown selfcheck command: {args.check}")


def _subject(payload: dict, args: argparse.Namespace) -> str:
    for key in ("email", "username", "name"):
        if payload.get(key):
            return str(payload[key])
    for key in ("email", "username", "name"):
        raw = getattr(args, key, None)
        if raw:
            return str(raw)
    return str(payload.get("kind") or "result")


def render(payload: dict, fmt: str, path, *, show_all: bool) -> None:
    console = Console()
    if fmt in {"table", "both"}:
        console.print(f"[bold]{NOTICE}[/bold]")
        for table_spec in presentation(payload, show_all=show_all):
            table = Table(title=table_spec["title"], show_lines=False)
            for column in table_spec["columns"]:
                table.add_column(column, overflow="fold")
            for row in table_spec["rows"]:
                table.add_row(*["" if cell is None else str(cell) for cell in row])
            console.print(table)
            if table_spec.get("note"):
                console.print(table_spec["note"])
        console.print(f"Wrote {path}")
    if fmt == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        print(f"Wrote {path}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "i_own_this", False):
        parser.error(
            "Refusing to run without --i-own-this. "
            "This tool is only for identifiers you own."
        )
    try:
        directory = resolve_output_dir(args.output_dir)
        payload = stamp_payload(run_check(args))
        payload["confirmed_own_identifier"] = True
        path = write_json(directory, payload["kind"], _subject(payload, args), payload)
    except OSError as exc:
        print(f"error: cannot write the result: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:
        print(f"error: {exc.__class__.__name__}: {exc}", file=sys.stderr)
        return 1
    render(payload, args.format, path, show_all=getattr(args, "show_all", False))
    if payload.get("valid") is False:
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
