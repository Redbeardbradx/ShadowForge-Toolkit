import psutil
import json
import sys
from datetime import datetime

try:
    with open('ports_baseline.json', 'r', encoding='utf-8-sig') as f:
        content = f.read().strip()
        if not content:
            print("⚠️  JSON void—regen PS pipe.")
            sys.exit(1)
        ports = json.loads(content)  # Scope locked here—demon slain
    print(f"💀 JSON valid: True | Array len: {len(ports)} | 445 hits: {sum(1 for e in ports if '445' in str(e.get('LocalPort', '')))}")
except json.JSONDecodeError as e:
    print(f"🔥 Malformed: {e}. Regen PS pipe or trim hack.")
    sys.exit(1)
except FileNotFoundError:
    print("❌ JSON MIA—PS pipe it.")
    sys.exit(1)

output = []
if isinstance(ports, list):  # Line 13 safe—ports bound above
    for entry in ports:
        if isinstance(entry, dict) and 'OwningProcess' in entry:
            port_str = str(entry['LocalPort'])
            if '445' in port_str:
                print("🚨 SMB Expo: EternalBlue bait—firewall it (netsh rule block 445).")
                output.append(f"ALERT: Port {port_str} - EternalBlue vector")
            try:
                pid = int(entry['OwningProcess'])
                p = psutil.Process(pid)
                cpu = p.cpu_percent(interval=0.1)
                print(f"Port {port_str}: {p.name()} (PID {pid}) - CPU: {cpu:.1f}%")
                output.append(f"Port {port_str}: {p.name()} - CPU {cpu:.1f}%")
            except (psutil.NoSuchProcess, ValueError, psutil.AccessDenied, psutil.ZombieProcess):
                print(f"Port {port_str}: PID {entry['OwningProcess']} - Ghosted")
                output.append(f"Port {port_str}: PID {entry['OwningProcess']} - Ghost")
else:
    print("⚠️ Not array—PS glitch. Peek raw: Get-Content ports_baseline.json -Head 5")

# Log war diary
with open('hunt_log.txt', 'a', encoding='utf-8') as l:
    l.write(f"{datetime.now()}: {chr(10).join(output)}\n💀 Hunt complete—exploits queued: SMB on 445 (PID4 System).\n")

print("\n💀 Hunt forged—check hunt_log.txt for scars.")