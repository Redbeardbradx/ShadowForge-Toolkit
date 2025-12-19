import subprocess
import os

def amass_enum(domain, output_file="amass_output.txt"):
    # Build the command — amass.exe must be in PATH or specify full path
    cmd = [
    "tools\\amass.exe", "enum", "-passive", "-d", domain,
    "-o", output_file
]
    print(f"[+] Running passive Amass enum on {domain}")
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if os.path.exists(output_file):
            print(f"[+] Results saved to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"[!] Amass failed: {e.stderr}")
    except FileNotFoundError:
        print("[!] amass.exe not found. Check PATH or tools folder.")

if __name__ == "__main__":
    # Quick test when running the file directly
    amass_enum("example.com")