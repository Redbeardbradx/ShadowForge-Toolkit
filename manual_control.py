# manual_control.py — requires explicit console confirmation before any action
import psutil
pid = int(input("pid to act on: "))
p = psutil.Process(pid)
print(p.info if hasattr(p,'info') else (p.pid, p.name()))
c = input("Type 'TERMINATE' to kill, 'SUSPEND' to suspend, anything else to cancel: ")
if c == 'TERMINATE':
    p.terminate()
    print("Terminated")
elif c == 'SUSPEND':
    p.suspend()
    print("Suspended")
else:
    print("Cancelled")
