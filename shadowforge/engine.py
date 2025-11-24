import json
import sys
import re
from datetime import datetime
from scapy.all import IP, ICMP, sr1  # Stealth layers

def ping_sweep(target):
    """Stealth vein: Scapy craft → Nmap parse, trap shadows."""  # Doc: Your hack ID
    try:
        print(f"[+] Stealth crafting to {target}...")
        pkt = IP(dst=target)/ICMP()  # Forge packet: IP + ICMP echo
        reply = sr1(pkt, timeout=2, verbose=0)  # Send/sniff 1 – silent
        if reply is None:
            print("\033[91m[-] No shadow reply – ghost.\033[0m")
            return None
        if ICMP in reply and reply[ICMP].type == 0:
            print("\033[92m[+] Stealth echo hit – Nmap chain...\033[0m")
        else:
            print("\033[91m[-] Filtered – force vein.\033[0m")  # Proceed ethical

        import subprocess  # Nmap bolt (scapy ports Week 2)
        nmap_cmd = ['nmap', '-sV', '--top-ports', '100', target]
        scan_result = subprocess.run(nmap_cmd, capture_output=True, text=True, timeout=45)

        if scan_result.returncode != 0:
            raise ValueError(f"Nmap dodge: {scan_result.stderr}")

        output = scan_result.stdout
        open_ports_raw = []
        ports_data = {}
        for line in output.split('\n'):
            if '/tcp' in line and 'open' in line.lower():
                open_ports_raw.append(line.strip())
                match = re.search(r'(\d+)/tcp\s+open\s+(\S+)(?:\s+(.+))?$', line)
                if match:
                    port, service, version = match.groups()
                    ports_data[port] = {
                        'service': service,
                        'version': version.strip() if version else 'unknown'
                    }

        vuln_seeds = [p for p in ports_data if ports_data[p]['service'].lower() in ['http', 'ftp', 'ssh', 'telnet']]

        report = {
            'timestamp': datetime.now().isoformat(),
            'target': target,
            'status': 'stealth_vein_complete',
            'stealth_ping': 'hit' if reply else 'miss',
            'open_ports': open_ports_raw,
            'parsed_ports': ports_data,
            'vuln_seeds': vuln_seeds,
            'full_output': output
        }
        print("\033[92m[+] Stealth JSON Gold:\033[0m")
        print(json.dumps(report, indent=2))
        with open('recon_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        return report
    except subprocess.TimeoutExpired:
        print("\033[93m[!] Nmap shadow dodge.\033[0m")
        return None
    except (FileNotFoundError, ValueError, Exception) as e:
        print(f"\033[91m[-] Stealth trap: {e} – os_log.txt log.\033[0m")
        return None

if __name__ == "__main__":
    ping_sweep('127.0.0.1')