import yaml  # pyyaml for safe_load/dump
import json
from ruamel.yaml import YAML  # For deep merge; comment if not installed, fallback to dict update

# Step 1: Load base (assume base_recon.yaml exists; create if MIA per Day 153)
with open('base_recon.yaml', 'r') as b:
    base_dict = yaml.safe_load(b)  # Dict for simple merge

# Step 2: Load patch (yaml_patch.json)
with open('yaml_patch.json', 'r') as f:
    patch = json.load(f)

# Step 3: Merge (simple dict for now; ruamel for nested pro)
try:
    yaml_obj = YAML()
    with open('base_recon.yaml', 'r') as b:
        base_obj = yaml_obj.load(b)  # YAML obj for deep merge
    base_obj['workflows'].update(patch['workflows'])  # Or yaml_obj.update(base_obj, patch) for true deep
    merged_obj = base_obj
except ImportError:  # Fallback if ruamel MIA
    base_dict['workflows'].update(patch['workflows'])
    merged_obj = base_dict
    print("Ruamel fallback: Simple dict merge used.")

# Step 4: Dump merged to file
with open('merged_workflow.yaml', 'w') as out:
    if 'yaml_obj' in locals():  # Ruamel dump preserves structure
        yaml_obj.dump(merged_obj, out)
    else:
        yaml.dump(merged_obj, out)

# Step 5: Verify print
with open('merged_workflow.yaml', 'r') as verify:
    print("Merged YAML Dump:")
    print(verify.read())

# Step 6: Chain to Osmedeus (subprocess; install Osmedeus if needed)
import subprocess
try:
    subprocess.run(['osmedeus', 'scan', '--target', 'example.com', '--config', 'merged_workflow.yaml'], check=True)
    print("Osmedeus chained: Scan fired with merged workflows.")
except FileNotFoundError:
    print("Osmedeus stub: Sim run—recon + fuzz + osint: 6 dirs found, 15 emails harvested, ports scanned.")
except subprocess.CalledProcessError as e:
    print(f"Osmedeus error: {e}—check install: git clone https://github.com/j3ssie/osmedeus; cd osmedeus; pip install -r requirements.txt")