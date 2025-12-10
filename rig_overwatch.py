import psutil
from datetime import datetime

def rig_overwatch(log_file='os_log.txt'):
    users = psutil.users()
    temps = psutil.sensors_temperatures()
    core_temp = temps.get('coretemp', [None])[0].current if temps.get('coretemp') else 'N/A'
    print(f"💀 Users logged: {len(users)} | CPU Temp: {core_temp}C")
    for user in users():
        print(f"  - {user.name} from {user.host} on {user.terminal}")
    if core_temp != 'N/A' and core_temp > 80:
        print("🚨 Heat alert—throttling cores...")
        for p in psutil.process_iter(['pid', 'name']):
            if p.info['name'] == 'chrome.exe':  # Example hog
                p.nice(psutil.HIGH_PRIORITY_CLASS)  # Lower priority
    # Log scars
    with open(log_file, 'a') as l:
        l.write(f"{datetime.now()}: Overwatch—{len(users)} users, temp {core_temp}C.\n")

rig_overwatch()  # Fire it—maps SSH ghosts or heat spikes on your i5 torch