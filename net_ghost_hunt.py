import psutil

def net_ghost_hunt(interface='wlan0'):
    ghosts = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED' and conn.raddr:  # Live connections only
            try:
                p = psutil.Process(conn.pid)
                ghosts.append({
                    'local': f"{conn.laddr.ip}:{conn.laddr.port}",
                    'remote': f"{conn.raddr.ip}:{conn.raddr.port}",
                    'family': 'IPv4' if conn.family == psutil.AF_INET else 'IPv6',
                    'pid': conn.pid,
                    'owner': p.name(),
                    'cmdline': ' '.join(p.cmdline())[:50]  # Truncate for log
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                ghosts.append({'local': f"{conn.laddr.ip}:{conn.laddr.port}", 'remote': f"{conn.raddr.ip}:{conn.raddr.port}", 'pid': conn.pid, 'owner': 'Ghost'})
    print(f"💀 {len(ghosts)} ESTABLISHED ghosts on {interface}:")
    for g in ghosts:
        print(f"  PID {g['pid']}: {g['owner']} from {g['local']} to {g['remote']}")

net_ghost_hunt()  # Fire it—spots your Chrome exfil or SSH drops