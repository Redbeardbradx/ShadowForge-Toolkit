from datetime import datetime
import subprocess
import json
from typing import Dict

def run_audit(level: str = 'quick') -> Dict:
    """
    Automate rig lockdown. Levels: 'quick' (5min), 'full' (15min). Ethical: Local only.
    Returns JSON: {'updates': 3, 'antivirus': 'ON', 'open_ports': [80, 443], 'risks': ['RDP open']}.
    """
    audit = {'level': level, 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'), 'risks': []}
    try:
        # Updates check
        result = subprocess.run(['wuauclt', '/detectnow'], capture_output=True, text=True)
        audit['updates'] = 'Scanning...' if result.returncode == 0 else 'Error: Reboot needed'
        # Antivirus status
        mp_status = subprocess.run(['powershell', 'Get-MpComputerStatus | Select AntivirusEnabled, RealTimeProtectionEnabled'], capture_output=True, text=True)
        audit['antivirus'] = 'ON' if 'True' in mp_status.stdout else 'OFF - Fix now!'
        if 'OFF' in audit['antivirus']:
            audit['risks'].append('Defender offline')
        # Firewall status
        fw_status = subprocess.run(['powershell', 'Get-NetFirewallProfile | Select Name, Enabled'], capture_output=True, text=True)
        audit['firewall'] = 'All ON' if all('True' in line for line in fw_status.stdout.split('\n') if 'Enabled' in line) else 'Some OFF - Lock it!'
        # Open ports (top 10)
        ports = subprocess.run(['netstat', '-an'], capture_output=True, text=True, shell=True)
        open_ports = [line.split()[1].split(':')[-1] for line in ports.stdout.split('\n') if ':' in line and 'LISTENING' in line]
        audit['open_ports'] = list(set(open_ports))[:10]
        if '3389' in audit['open_ports']:  # RDP risk
            audit['risks'].append('RDP open—close unless needed')
        # Full scan tease (if 'full')
        if level == 'full':
            subprocess.run(['powershell', 'Start-MpScan -ScanType FullScan'], capture_output=True)
            audit['full_scan'] = 'Running—check Task Manager'
        return audit
    except Exception as e:
        audit['error'] = str(e)
        return audit

def log_audit(audit: Dict, filepath: str = 'reports/audit.json') -> str:
    """Dump to JSON for Todoist import."""
    with open(filepath, 'w') as f:
        json.dump(audit, f, indent=2)
    return f"Audit dumped to {filepath}—risks: {len(audit['risks'])}"