import subprocess
import argparse
import os
import platform
from datetime import datetime
import socket
import threading
from queue import Queue
from termcolor import colored

def nmap_scan(target):
    cmd = ['nmap', '-sS', '-T4', '-oN', 'scan.txt', target]  # SYN scan, aggressive timing, output file.
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

parser = argparse.ArgumentParser()
parser.add_argument('--target', required=True)
args = parser.parse_args()
print(nmap_scan(args.target))

def ping_sweep(network, start_ip=1, end_ip=255):
    """ICMP-based ping sweep for live host discovery.
    
    Protocol: Sends ICMP echo request (type 8, code 0) packets. Live hosts respond with echo reply (type 0, code 0).
    Why it works: Most systems reply unless ICMP is filtered. Flaw: Firewalls often block ICMP, leading to false negatives.
    Defense: Configure firewall rules to drop ICMP echo requests (e.g., iptables -A INPUT -p icmp --icmp-type echo-request -j DROP on Linux).
    """
    net_parts = network.split('.')
    net_prefix = '.'.join(net_parts[:3]) + '.'
    oper = platform.system()
    ping_cmd = "ping -n 1 " if oper == "Windows" else "ping -c 1 "
    t1 = datetime.now()
    print(colored("[*] Scanning in progress...", "blue"))
    live_hosts = []
    for ip_suffix in range(start_ip, end_ip + 1):
        addr = net_prefix + str(ip_suffix)
        comm = ping_cmd + addr
        response = os.popen(comm)
        output = response.read()
        if "TTL" in output.upper():  # Case-insensitive check for reliability
            print(colored(f"[+] {addr} --> Live", "green"))
            live_hosts.append(addr)
    t2 = datetime.now()
    total_time = t2 - t1
    print(colored(f"[*] Scan completed in: {total_time}", "blue"))
    return live_hosts

def tcp_port_scan(target, port_range='1-1024', aggressive=False):
    """TCP connect port scanner for service enumeration.
    
    Protocol: Full 3-way handshake (SYN -> SYN-ACK -> ACK/RST). Open ports complete it; closed send RST.
    Why it works: Services listen on ports, responding to connections. Flaw: Detectable/logged as full connections.
    Defense: IDS rules for scan patterns (e.g., Suricata: alert tcp any any -> any any (msg:"Port Scan"; flow:stateless; detection_filter:track by_src, count 10, seconds 5; sid:1000001;)).
    """
    try:
        t_ip = socket.gethostbyname(target)
    except socket.gaierror:
        print(colored(f"[-] Invalid target: {target}", "red"))
        return []
    
    start_port, end_port = map(int, port_range.split('-'))
    print(colored(f"[*] Scanning ports {start_port}-{end_port} on {t_ip}...", "blue"))
    t1 = datetime.now()
    open_ports = []
    
    def scan_port(port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)  # Balance speed/detection
        try:
            conn = s.connect_ex((t_ip, port))
            if conn == 0:
                print(colored(f"[+] Port {port}: OPEN", "green"))
                open_ports.append(port)
        except:
            pass
        finally:
            s.close()
    
    if aggressive:
        # Threaded for speed
        print_lock = threading.Lock()
        q = Queue()
        def threader():
            while True:
                port = q.get()
                scan_port(port)
                q.task_done()
        
        for _ in range(100):  # Threads; adjust < your cores (16) to avoid overload
            t = threading.Thread(target=threader)
            t.daemon = True
            t.start()
        
        for port in range(start_port, end_port + 1):
            q.put(port)
        
        q.join()
    else:
        # Sequential for stealth/learning
        for port in range(start_port, end_port + 1):
            scan_port(port)
    
    t2 = datetime.now()
    total_time = t2 - t1
    print(colored(f"[*] Scan completed in: {total_time}", "blue"))
    return open_ports

def run(args):
    if not args.target:
        print(colored("[-] --target required (e.g., 192.168.1.1 or example.com)", "red"))
        return
    
    # Add --ports arg in main.py later; hardcode for now
    port_range = '1-1024'  # Default; override if needed
    
    # Run ping sweep first if full chain
    if args.full:
        print(colored("[+] Running full recon chain...", "green"))
        network = '.'.join(args.target.split('.')[:3] + ['0'])  # Assume /24
        live_hosts = ping_sweep(network)
        for host in live_hosts:
            tcp_port_scan(host, port_range, args.aggressive)
    else:
        tcp_port_scan(args.target, port_range, args.aggressive)