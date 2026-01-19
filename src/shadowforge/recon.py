from termcolor import colored
import nmap

def run_recon(target, scan_type="ping", ports="1-1000"):
    print(colored(f"[*] Recon stub: {scan_type} on {target}", "yellow"))
    print(colored("  - Future: Nmap/RustScan call here", "cyan"))
    print(colored("[+] Done (stub)", "green"))
    scanner = nmap.PortScanner()
    arg_map = {
        "ping": "-sn",
        "tcp": f"-sT -p {ports}",
        "version": f"-sV -p {ports}",
        "os": f"-O -p {ports}",
    }
    args = arg_map.get(scan_type, "-sT")
    try:
        scanner.scan(target, arguments=args)
        for host in scanner.all_hosts():
            state = scanner[host].state()
            print(colored(f"{host}: {state.upper()}", "green" if state == "up" else "red"))
    except Exception as e:
        print(colored(f"[!] {e}", "red"))