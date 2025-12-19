import subprocess
from termcolor import colored

def ping_sweep(target):
    """Active host discovery with nmap -sn -PE (ICMP + TCP echo for Windows)"""
    try:
        print(colored(f"[+] Sweeping {target} for live hosts...", "yellow"))
        cmd = ["nmap", "-sn", "-PE", "-oG", "-", target]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)

        live_hosts = []
        for line in result.stdout.splitlines():
            if line.startswith("Host: ") and "Status: Up" in line:
                host = line.split("Host: ")[1].split(" (")[0].strip()
                live_hosts.append(host)
                print(colored(f" LIVE {host}", "green"))

        if not live_hosts:
            print(colored("[*] No live hosts found", "cyan"))

        return live_hosts

    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Nmap failed: {e.stderr}", "red"))
    except FileNotFoundError:
        print(colored("[!] nmap.exe not found in PATH", "red"))

def version_scan(hosts):
    """Service version + OS fingerprint — skips host discovery (-Pn)"""
    if not hosts:
        print(colored("[*] No hosts provided for version scan", "cyan"))
        return
    try:
        print(colored(f"[+] Version scanning {len(hosts)} host(s) with -Pn (skip ping)...", "yellow"))
        cmd = ["nmap", "-sV", "-O", "-p-", "-T4", "-Pn"] + hosts
        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
    except subprocess.CalledProcessError as e:
        print(colored(f"[!] Nmap version scan failed: {e.stderr}", "red"))