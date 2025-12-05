import json
with open('ports_baseline.json', 'r', encoding='utf-8-sig') as f:
    content = f.read()
try:
    parsed = json.loads(content)
    print(f"💀 JSON valid: True | Array len: {len(parsed)} | 445 hits: {sum(1 for e in parsed if '445' in str(e.get('LocalPort', '')))}")
except json.JSONDecodeError as e:
    print(f"🔥 Malformed: {e}")
    print(f"Trail rot: {repr(content[-100:])}")
    content = content.rstrip().rstrip(',')
    parsed = json.loads(content)
    print(f"💀 Trimmed & valid: True | 445 hits: {sum(1 for e in parsed if '445' in str(e.get('LocalPort', '')))}")