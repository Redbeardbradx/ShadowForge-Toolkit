# safe_overwatch.py — logs users & temperature (read-only)
import psutil
from datetime import datetime

def rig_overwatch(log='os_log.txt'):
    users = psutil.users()
    temps = {}
    if hasattr(psutil, 'sensors_temperatures'):
        temps = psutil.sensors_temperatures() or {}
    core_temp = 'N/A'
    if temps:
        for name, entries in temps.items():
            if entries:
                core_temp = entries[0].current
                break
    with open(log,'a') as f:
        f.write(f"{datetime.utcnow().isoformat()} users={len(users)} temp={core_temp}\n")
    print(f"users={len(users)} temp={core_temp}")

if __name__ == '__main__':
    rig_overwatch()
