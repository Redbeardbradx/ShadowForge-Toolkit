import argparse
import subprocess
import json
import os

import ctypes
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
if os.name == 'nt' and not is_admin():
    print("Run as admin for NSE power—right-click PS > Run as admin")
    exit(1)

parser = argparse.ArgumentParser(description="ShadowForge Recon: NSE Beast Mode")
parser.add_argument('--target', required=True, help="Target IP/hostname")
parser.add_argument('--nse', default='default', help="NSE category: default|vuln|brute")
args = parser.parse_args()

def run_nse(target, category='default'):
    cmd = ['nmap', '-sV', f'--script {category}', '-oJ', '-', target]
    # Windows path hack—adjust if your nmap.exe is elsewhere
    if os.name == 'nt':
        nmap_path = r'C:\Program Files\Nmap\nmap.exe'  # Or wherever you installed
        if os.path.exists(nmap_path):
            cmd[0] = nmap_path
        else:
            return {"error": "Nmap not found—install from nmap.org"}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except (json.JSONDecodeError, subprocess.CalledProcessError, FileNotFoundError) as e:
        return {"error": f"NSE run fail: {e} – Check nmap install/path"}

if __name__ == "__main__":
    data = run_nse(args.target, args.nse)
    print(json.dumps(data, indent=2))  # JSON drop for chain