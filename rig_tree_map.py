import psutil

def rig_tree_map(target_pid=None):
    if not target_pid:
        target_pid = psutil.Process().pid  # Current process tree
    tree = []
    p = psutil.Process(target_pid)
    tree.append({'pid': p.pid, 'name': p.name(), 'parent': p.ppid(), 'children': []})
    for child in p.children(recursive=True):
        tree[0]['children'].append({'pid': child.pid, 'name': child.name(), 'parent': child.ppid()})
    print("💀 Process tree map:")
    for node in tree:
        print(f"  PID {node['pid']} ({node['name']}) <- parent {node['parent']}")
        for child in node['children']:
            print(f"    └ Child PID {child['pid']} ({child['name']})")
    return tree  # Chain to auto.py for kill tree

rig_tree_map()  # Fire it—maps your recon.py spawn and its kids