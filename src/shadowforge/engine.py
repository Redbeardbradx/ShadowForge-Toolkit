# engine.py – Viking Port-Scan Core (Threaded Socket Raid)
import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

def port_scan(target,ports=range(1, 1025),threads=100):
    """
    Ethical port hammer: Scans 1-1024, guesses services.
    Returns dict: {'open': [{'port': 80, 'service': 'http'}],'closed': count, 'summary': str}
    Test: localhost only—#RanchNetRaid
    """
    open_ports = []
    closed_count = 0
    lock = threading.Lock()  # Thread-safe count

    def scan_port(port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((target, port))
            sock.close()
            if result == 0:
                services = {21: 'ftp', 22: 'ssh', 23: 'telnet', 25: 'smtp', 53: 'dns',
                            80: 'http', 110: 'pop3', 143: 'imap', 443: 'https', 993: 'imaps',
                            995: 'pop3s', 1723: 'pptp', 3306: 'mysql', 3389: 'rdp', 5432: 'postgres',
                            5900: 'vnc', 8080: 'http-alt'}
                service = services.get(port, 'unknown')
                with lock:
                    open_ports.append({'port': port, 'service': service})
            else:
                with lock:
                    nonlocal closed_count
                    closed_count += 1
        except Exception:
            pass  # Socket ghosts—grind on

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = [executor.submit(scan_port, port) for port in ports]
        for future in as_completed(futures):
            future.result()  # Harvest all

    return {
        'target': target,
        'open': open_ports,
        'closed': closed_count,
        'summary': f"{len(open_ports)} open / {len(ports) - len(open_ports)} closed (scanned {len(ports)} ports)"
    }

if __name__ == '__main__':
    import sys
    target = sys.argv[1] if len(sys.argv) > 1 else 'localhost'
    print(port_scan(target))