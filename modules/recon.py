# recon.py – ShadowForge Network Recon Beast (Nmap wrapper + JSON vuln spit)
# Barn bolt: E:\ShadowForge\shadowforge\modules\recon.py
import subprocess, json, sys, argparse, os
from datetime import datetime

# Barn root for chains (e.g., auto.py imports)
BARN_ROOT = os.path.dirname(os.path.dirname(__file__))

def run_nmap(target, args=' -sV -O --top-ports 1000 '):
    cmd = f'nmap{args}{target}'
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=300)
        return result.stdout + result.stderr
    except Exception as e: return f"Recon fail: {e}"

def parse_to_json(nmap_out):
    lines = nmap_out.split('\n')
    ports = [line for line in lines if '/tcp' in line or '/udp' in line]
    vulns = [p for p in ports if 'open' in p.lower()]
    report = {
        "timestamp": datetime.now().isoformat(),
        "target": sys.argv[2] if len(sys.argv)>2 else "localhost",
        "open_ports": vulns[:10],
        "full_output": nmap_out[-500:]
    }
    return json.dumps(report, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ShadowForge Recon: Scan like a Viking raid.")
    parser.add_argument("target", help="IP/hostname to sweep (e.g., 192.168.1.1)")
    args = parser.parse_args()
    
    print("Forging recon in modules barn...")
    output = run_nmap(args.target)
    json_report = parse_to_json(output)
    
    report_path = os.path.join(BARN_ROOT, "recon_report.json")
    with open(report_path, "w") as f: f.write(json_report)
    print(f"Recon dropped: {len(json_report)} bytes. Check {report_path}")