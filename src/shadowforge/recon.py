import argparse
import subprocess
import json
import os
import ctypes
import shutil  # PATH hunt
from datetime import datetime  # Log stamps

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if os.name == 'nt' and not is_admin():
    print("⚠️ Run as admin for NSE power—right-click PS > Run as admin")
    exit(1)

parser = argparse.ArgumentParser(description="ShadowForge Recon: NSE Beast Mode")
parser.add_argument('--target', required=True, help="Target IP/hostname")
parser.add_argument('--nse', default='default', help="NSE category: default|vuln|brute")
args = parser.parse_args()

def run_nse(target, category='default'):
    # Cross-platform cmd—PATH hunt first, fallback Windows path
    cmd = ['nmap', '-sV', f'--script {category}', '-oJ', '-', target]
    if os.name == 'nt':
        nmap_path = r'C:\Program Files\Nmap\nmap.exe'  # Adjust if custom install
        if not shutil.which('nmap') and os.path.exists(nmap_path):
            cmd[0] = nmap_path
        elif not shutil.which('nmap'):
            return {"error": "Nmap not found—install from nmap.org/download"}
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout)
        # Log win
        with open('os_log.txt', 'a', encoding='utf-8') as l:
            l.write(f"{datetime.now()}: NSE feast on {target} ({category})—{len(data.get('scan', {}))} hosts scanned.\n")
        return data
    except json.JSONDecodeError as e:
        error = f"JSON choke: {e}"
    except subprocess.CalledProcessError as e:
        error = f"NSE run fail (code {e.returncode}): {e.stderr}"
    except FileNotFoundError as e:
        error = f"Nmap ghost: {e} – Check PATH/install"
    except Exception as e:
        error = f"Recon rot: {e}"
    # Log choke
    with open('os_log.txt', 'a', encoding='utf-8') as l:
        l.write(f"{datetime.now()}: Recon choke on {target} ({category}): {error}\n")
    return {"error": error}

if __name__ == "__main__":
    data = run_nse(args.target, args.nse)
    print(json.dumps(data, indent=2))  # JSON drop for auto.py chain