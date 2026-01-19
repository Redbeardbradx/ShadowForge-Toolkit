# safe_tree_map.py — prints process tree for a target PID
import psutil, json
def rig_tree_map(target_pid=None):
    try:
        if target_pid is None:
            target_pid = psutil.Process().pid
        root = psutil.Process(target_pid)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        print("Target PID not accessible")
        return []
    tree = {'pid': root.pid, 'name': root.name(), 'parent': root.ppid(), 'children':[]}
    for c in root.children(recursive=True):
        tree['children'].append({'pid':c.pid, 'name':c.name(), 'parent':c.ppid()})
    print(json.dumps(tree, indent=2))
    return tree

if __name__ == '__main__':
    rig_tree_map()
