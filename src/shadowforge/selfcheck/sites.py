"""Public profile URLs for a username the operator owns.

Detection is best-effort. A "found" row means the site returned a success
response for that profile URL, not proof of who created the account.
"""

from __future__ import annotations

from urllib.parse import quote

SITES: list[dict] = [
    {"name": "About.me", "url": "https://about.me/{username}", "trust_200": True},
    {"name": "Bitbucket", "url": "https://bitbucket.org/{username}", "trust_200": True},
    {"name": "Codeberg", "url": "https://codeberg.org/{username}", "trust_200": True},
    {"name": "CodePen", "url": "https://codepen.io/{username}", "trust_200": True},
    {"name": "Dev.to", "url": "https://dev.to/{username}", "trust_200": True},
    {"name": "Docker Hub", "url": "https://hub.docker.com/u/{username}", "trust_200": True},
    {"name": "Flickr", "url": "https://www.flickr.com/people/{username}", "trust_200": True},
    {"name": "GitHub", "url": "https://github.com/{username}", "trust_200": True},
    {"name": "GitLab", "url": "https://gitlab.com/{username}", "trust_200": True},
    {
        "name": "Hacker News",
        "url": "https://news.ycombinator.com/user?id={username}",
        "trust_200": False,
        "missing_markers": ["No such user."],
        "found_markers": ["created:"],
    },
    {"name": "Hugging Face", "url": "https://huggingface.co/{username}", "trust_200": True},
    {"name": "Keybase", "url": "https://keybase.io/{username}", "trust_200": True},
    {"name": "Launchpad", "url": "https://launchpad.net/~{username}", "trust_200": True},
    {"name": "Mastodon", "url": "https://mastodon.social/@{username}", "trust_200": True},
    {"name": "Medium", "url": "https://medium.com/@{username}", "trust_200": True},
    {"name": "npm", "url": "https://www.npmjs.com/~{username}", "trust_200": True},
    {"name": "Pastebin", "url": "https://pastebin.com/u/{username}", "trust_200": True},
    {"name": "PyPI", "url": "https://pypi.org/user/{username}", "trust_200": True},
    {
        "name": "Reddit",
        "url": "https://old.reddit.com/user/{username}",
        "trust_200": True,
        "missing_markers": ["nobody on Reddit goes by that name"],
    },
    {"name": "Replit", "url": "https://replit.com/@{username}", "trust_200": True},
    {"name": "SoundCloud", "url": "https://soundcloud.com/{username}", "trust_200": True},
    {"name": "SourceForge", "url": "https://sourceforge.net/u/{username}", "trust_200": True},
    {"name": "Twitch", "url": "https://www.twitch.tv/{username}", "trust_200": True},
    {"name": "Vimeo", "url": "https://vimeo.com/{username}", "trust_200": True},
    {
        "name": "Wikipedia",
        "url": "https://en.wikipedia.org/wiki/User:{username}",
        "trust_200": True,
    },
]


def profile_url(site: dict, username: str) -> str:
    safe = quote(username, safe="._-")
    return site["url"].format(username=safe)


def select_sites(requested: list[str] | None, catalog: list[dict] | None = None) -> list[dict]:
    source = SITES if catalog is None else catalog
    if not requested:
        return list(source)
    by_name = {site["name"].casefold(): site for site in source}
    chosen: list[dict] = []
    missing: list[str] = []
    for name in requested:
        site = by_name.get(name.strip().casefold())
        if site is None:
            missing.append(name.strip())
        else:
            chosen.append(site)
    if missing:
        known = ", ".join(site["name"] for site in source)
        raise ValueError(f"Unknown site(s): {', '.join(missing)}. Known sites: {known}")
    return chosen
