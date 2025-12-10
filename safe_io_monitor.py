# safe_io_monitor.py — logs per-process I/O bursts (no suspend)
import psutil, time, json
from datetime import datetime

def io_hog_hunt_log(interval=1, threshold_bytes=5*1024*1024):
    prev = {}
    while True:
        curr = {}
        bursts = []
        for p in psutil.process_iter(['pid','name']):
            try:
                io = p.io_counters()
                total = io.read_bytes + io.write_bytes
                curr[p.pid] = {'total': total, 'name': p.info['name']}
                if p.pid in prev:
                    delta = total - prev[p.pid]['total']
                    if delta > threshold_bytes:
                        bursts.append({'time': datetime.utcnow().isoformat()+'Z',
                                       'pid': p.pid, 'name': p.info['name'], 'delta': delta})
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        if bursts:
            with open('io_bursts.log','a') as f:
                for b in bursts:
                    f.write(json.dumps(b)+'\n')
            print(f"Logged {len(bursts)} I/O bursts.")
        prev = curr
        time.sleep(interval)

if __name__ == '__main__':
    io_hog_hunt_log()
