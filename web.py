import subprocess
import sys

def run_nuclei(target, severity="high", templates_path="~/nuclei-templates"):
    cmd = ["nuclei", "-u", target, "-severity", severity, "-t", templates_path, "-json"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Nuclei error: {e.stderr}")
        return None

def run_feroxbuster(target, wordlist=r"E:\wordlists\raft-medium-directories.txt", extensions=["php","js","html","txt"]):
    cmd = ["feroxbuster", "-u", target, "-w", wordlist, "--auto-tune", "-t", "150"]
    if extensions:
        cmd += ["-x", ",".join(extensions)]
    cmd += ["--status-codes", "200,301,403"]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except FileNotFoundError:
        print("feroxbuster not found or wordlist missing.")

# Example usage
# run_feroxbuster("http://lab-target.local")