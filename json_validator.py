import json
import os

filename = 'ports_baseline.json'
if not os.path.exists(filename) or os.path.getsize(filename) == 0:
    print(f"⚠️  {filename} MIA or void—regen via PS pipe first.")
    exit(1)

with open(filename, 'r', encoding='utf-8-sig') as f:
    content = f.read().strip()

if not content:
    print("🔥 Empty file—PS pipe it raw.")
    exit(1)

try:
    parsed = json.loads(content)
    print(f"💀 JSON valid: True | Array len: {len(parsed)} | 445 hits: {sum(1 for e in parsed if '445' in str(e.get('LocalPort', '')))}")
except json.JSONDecodeError as e:
    print(f"🔥 Malformed: {e}")
    print(f"Trail rot: {repr(content[-100:])}")
    content = content.rstrip().rstrip(',')
    try:
        parsed = json.loads(content)
        print(f"💀 Trimmed & valid: True | 445 hits: {sum(1 for e in parsed if '445' in str(e.get('LocalPort', '')))}")
    except json.JSONDecodeError as e2:
        print(f"🔥 Trim failed: {e2}. Regen PS pipe or peek raw: Get-Content ports_baseline.json -Raw")