# ShadowForge-Toolkit

Python project scaffold. Vendored Windows scanner binaries and committed scan output are not part of this tree. External tools, if used at all, should come from the system PATH.

## Repository notes

- Package metadata lives in `pyproject.toml`.
- Python sources are under `src/shadowforge/` and at the repository root. Several modules are duplicated and unfinished.
- Generated reports belong in `reports/` or `output/`, both gitignored.

## Installation

```bash
pip install -e .
```
