# pyproject.toml (preferred 2026)
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "shadowforge-toolkit"
version = "0.1.0"
dependencies = [  # from requirements.txt
    "termcolor",
    "requests",
    "shodan",
    "python-nmap",
    "scapy",
]

[project.scripts]
shadowforge = "shadowforge:main"  # entry point