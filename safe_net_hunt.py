import psutil, json, time
from datetime import datetime

def net_ghost_hunt(logfile='net_ghosts.log'):
    entries = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED' and conn.raddr:
            try:
                p = psutil.Process(conn.pid)
                owner = p.name()
                cmd = " ".join(p.cmdline())[:80]
            except:
                owner = "UNKNOWN"
                cmd = ""

            entry = {
                "local": f"{conn.laddr.ip}:{conn.laddr.port}",
                "remote": f"{conn.raddr.ip}:{conn.raddr.port}",
                "pid": conn.pid,
                "owner": owner,
                "cmd": cmd,
                "time": str(datetime.now())
            }
            entries.append(entry)

    with open(logfile, "a") as f:
        for e in entries:
            f.write(json.dumps(e) + "\n")

    print(f"Logged {len(entries)} ESTABLISHED connections.")

net_ghost_hunt()
