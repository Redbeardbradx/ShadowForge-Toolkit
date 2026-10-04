# ShadowForge self-exposure check

**This command is for checking YOUR OWN accounts and public exposure.**
Only use email addresses, usernames, and names that belong to you.

`shadowforge selfcheck` looks at public sources and writes a JSON record plus a table:

- `email` checks syntax, MX records, and Have I Been Pwned breach exposure for your own email.
- `username` checks whether public profile pages exist for your own username.
- `name` collects the first page of public search results for your own name, and always prints links you can open yourself.

The check stops when a site or API rate-limits it. It does not log into accounts, and it does not use a built-in API key.

Vendored Windows scanner binaries and committed scan output are not part of this tree. External tools, if used at all, should come from the system PATH. Generated reports belong in `reports/` or `output/`, both gitignored.

## Exact commands

Install once from this repository:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

Email (breach check runs only when `HIBP_API_KEY` is set):

```bash
export HIBP_API_KEY="your-hibp-key"
shadowforge selfcheck email --email you@example.com --i-own-this
```

Username:

```bash
shadowforge selfcheck username --username YOUR_USERNAME --i-own-this
```

Username with a shorter timeout and the default concurrency cap (maximum 10):

```bash
shadowforge selfcheck username --username YOUR_USERNAME --i-own-this --timeout 8 --concurrency 5
```

Name:

```bash
shadowforge selfcheck name --name "Your Name" --i-own-this
```

Name plus a city, writing the JSON file into `./output`:

```bash
shadowforge selfcheck name --name "Your Name" --location "Your City" --i-own-this --output-dir ./output
```

Help:

```bash
shadowforge --help
shadowforge selfcheck --help
shadowforge selfcheck username --help
```

## Output and keys

| Item | Value |
| --- | --- |
| Default output directory | `~/.local/share/shadowforge/output` |
| Override | `--output-dir` or `SHADOWFORGE_OUTPUT_DIR` |
| Formats | `--format both` (table on screen, JSON file), `--format table`, `--format json` |
| HIBP key | `HIBP_API_KEY`. If it is unset, email syntax and MX still run and the breach check explains that the key is missing. |

Get an HIBP key from <https://haveibeenpwned.com/API/Key>. Do not put the key in the repository.

Username results are best-effort. `found` means that site's public profile URL responded like an existing account. Open the URL and confirm it is yours. Pass `--show-all` to include not-found rows in the table. The JSON file always contains every row.

Name search sends one request for the first public results page. If that request is blocked or rate-limited, the command still prints DuckDuckGo and Bing links for the same query.

## Tests

```bash
pytest
```

The tests cover validation and parsing. They do not call the network and they do not need an API key.

## Package layout

The installed command is `shadowforge selfcheck`, defined in `pyproject.toml` as `shadowforge.selfcheck.cli:main`. Implementation lives in `src/shadowforge/selfcheck/`. Shared pieces are the HTTP session (`http_client.py`), output writer (`output.py`), and environment/path loader (`config.py`).
