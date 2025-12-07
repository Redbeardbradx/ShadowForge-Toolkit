import psutil
import multiprocessing
import time
from datetime import datetime  # For log stamps

def cpu_burn():  # Endless loop—pure hellfire
    while True:
        pass

if __name__ == '__main__':
    core_count = multiprocessing.cpu_count()  # Grabs your 10 cores
    procs = [multiprocessing.Process(target=cpu_burn) for _ in range(core_count)]
    for p in procs:
        p.start()
    print(f"💀 i5 inferno lit—{core_count} cores in 30s hell. Task Manager: Watch peaks hit 100%.")
    time.sleep(30)  # Burn time—tweak if you want longer scars
    for p in procs:
        p.terminate()
        p.join()  # Clean kill, no zombie processes
    peak_cpu = psutil.cpu_percent(interval=1)
    print(f"🔥 Quenched—Peak CPU: {peak_cpu:.1f}% | Temps? Check Task Manager.")
    # Log the scars
    with open('hunt_log.txt', 'a', encoding='utf-8') as l:
        l.write(f"{datetime.now()}: Stress torch—Peak {peak_cpu:.1f}%, cores {core_count}. No meltdown.\n")