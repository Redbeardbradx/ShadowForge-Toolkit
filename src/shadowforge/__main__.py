from .main import cli_entry

if __name__ == "__main__":
    cli_entry()
# Save/close. Verify: Get-Content src\shadowforge\__main__.py  # Echo: from .main import cli_entry \n if __name__ == "__main__": \n     cli_entry()
# Test module: python -m shadowforge auto --target 192.168.1.1 --dry-run  # Roars: {"phase":"recon_complete","data":{"target":"192.168.1.1","ports_open":4}} → yields laced (no __main__ choke)