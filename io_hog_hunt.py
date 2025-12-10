import psutil
import time

def io_hog_hunt(interval=1, threshold_bytes=1024*1024):  # 1MB threshold
    prev_io = {}
    while True:
        current_io = {}
        for p in psutil.process_iter(['pid', 'name']):
            try:
                io = p.io_counters()
                current_io[p.info['pid']] = io.read_bytes + io.write_bytes
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        for pid, curr in current_io.items():
            if pid in prev_io:
                delta = curr - prev_io[pid]
                if delta > threshold_bytes:
                    p = psutil.Process(pid)
                    print(f"🚨 Hog PID {pid} ({p.name()}): {delta / 1024 / 1024:.1f}MB I/O burst—throttling...")
                    p.suspend()  # Pause the beast
                    time.sleep(5)  # 5s timeout
                    p.resume()  # Release
        prev_io = current_io
        time.sleep(interval)

io_hog_hunt()  # Fire it—watch Chrome tabs or your MJ tracker hog disk