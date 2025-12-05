import json
with open('ports_baseline.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()
try:
    parsed = json.loads(content)
    print(f"💀 JSON valid: True | Array len: {len(parsed)} | 445 hits: {sum(1 for e in parsed if '445' in          str(e.get('LocalPort', '')))}")
except json.JSONDecodeError as e:
    print(f"🔥 Malformed: {e}")
    print(f"Trail rot: {repr(content[-100:])}")  # Sniff the end for comma demons or EOF junkexcept FileNotFoundError:
    print("❌ ports_baseline.json MIA—generate it via PS pipe.")
    sys.exit(1)

if isinstance(ports, list):
    for entry in ports:
        if isinstance(entry, dict) and 'OwningProcess' in entry:
            try:
                pid = int(entry['OwningProcess'])
                p = psutil.Process(pid)
                print(f"Port {entry['LocalPort']}: {p.name()} (PID {pid}) - CPU: {p.cpu_percent(interval=0.1):.1f}%")
            except (psutil.NoSuchProcess, ValueError, psutil.AccessDenied):
                print(f"Port {entry['LocalPort']}: PID {entry['OwningProcess']} - Ghosted/Zombie")
else:
    print("⚠️ JSON not an array—PS output glitched? Manual peek: cat ports_baseline.json")

print("\n💀 Hunt complete—exploits queued: SMB on 445 (PID4 System, eternal).")