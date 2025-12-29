import socket
import threading
from queue import Queue
from termcolor import colored

def port_scan(target, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((target, port))
        sock.close()
        return result == 0  # Open if 0
    except:
        return False

def threaded_scan(target, ports, num_threads=100):
    queue = Queue()
    print_queue = Queue()
    def worker():
        while not queue.empty():
            port = queue.get()
            if port_scan(target, port):
                print_queue.put(colored(f"Port {port} open", 'green'))
            queue.task_done()
    for port in ports:
        queue.put(port)
    for _ in range(num_threads):
        t = threading.Thread(target=worker)
        t.daemon = True
        t.start()
    queue.join()
    while not print_queue.empty():
        print(print_queue.get())
    print(colored("Scan complete", 'blue'))

# Usage: threaded_scan('127.0.0.1', range(1, 1025))