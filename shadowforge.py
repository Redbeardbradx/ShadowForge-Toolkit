#!/usr/bin/env python3
import argparse, subprocess, json, os, time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
import requests
from graphviz import Digraph  # For auto PNG
from PIL import Image  # Pillow for image handling if needed

console = Console()

console.print(Panel("[bold red]ShadowForge-Toolkit v1.0 – GOD TIER[/]\n[cyan]@redbeardbradx[/]\n[white]One command. Full visual phantom.[/]", expand=False, box=box.ROUNDED))

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="module")
person = sub.add_parser("person", help="Full visual dossier from ANY seed")
person.add_argument("--name")
person.add_argument("--phone")
person.add_argument("--email")
person.add_argument("--username")
person.add_argument("--address")
args = parser.parse_args()

if args.module != "person":
    exit()

seed = args.username or args.name or args.phone or args.email or args.address
console.print(f"[bold green]Target locked:[/] [yellow]{seed}[/]")
results = {"emails": [], "phones": [], "usernames": [], "profiles": [], "addresses": []}

# 1. Sherlock
if args.username or args.name:
    uname = args.username or args.name.replace(" ", "").lower()
    console.print("[*] Sherlock hunting username...")
    try:
        cmd = ["python", "-m", "sherlock", uname, "--print-found", "--timeout", "8"]
        out = subprocess.check_output(cmd, cwd="sherlock", text=True, stderr=subprocess.DEVNULL)
        for line in out.splitlines():
            if "http" in line:
                results["profiles"].append(line.strip())
    except Exception as e:
        console.print(f"[red]Sherlock snag: {e}[/]")

# 2. TheHarvester
if args.email or args.name:
    domain = args.email.split("@")[-1] if args.email else args.name.replace(" ", "")
    console.print("[*] TheHarvester reaping emails...")
    try:
        subprocess.run(["python", "theHarvester.py", "-d", domain, "-b", "all", "-l", "300", "-f", "temp.json"], 
                       cwd="theHarvester", stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
        if os.path.exists("theHarvester/temp.json"):
            with open("theHarvester/temp.json") as f:
                data = json.load(f)
            results["emails"] += data.get("emails", [])
        # Clean temp
        os.remove("theHarvester/temp.json")
    except Exception as e:
        console.print(f"[red]Harvester snag: {e}[/]")

# 3. Epieos phone/email flip (free tier)
if args.phone or args.email:
    console.print("[*] Epieos reverse lookup...")
    try:
        r = requests.get(f"https://epieos.com/api/v1/lookup?query={args.phone or args.email}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("google"):
                results["profiles"].append(f"Google Account → {data['google']}")
            if data.get("accounts"):
                for acc in data["accounts"][:5]:
                    results["profiles"].append(acc)
    except Exception as e:
        console.print(f"[red]Epieos snag: {e}[/]")

# 4. Final table
table = Table(title=f"DOSSIER – {seed}", box=box.ROUNDED)
table.add_column("Type", style="cyan")
table.add_column("Count", style="green")
table.add_column("Preview", style="white")
table.add_row("Profiles", str(len(results["profiles"])), "\n".join(results["profiles"][:3]))
table.add_row("Emails", str(len(set(results["emails"]))), "\n".join(list(set(results["emails"]))[:3]))
console.print(table)

# 5. Auto PNG Graph (Graphviz magic)
console.print("[*] Forging visual map...")
try:
    dot = Digraph(comment='Dossier Graph')
    dot.node(seed, shape='box', style='filled', color='red', label=seed)
    for p in results["profiles"][:10] + list(set(results["emails"])[:5]):
        dot.node(p[:20], shape='ellipse', color='blue')
        dot.edge(seed, p[:20])
    dot.render('dossier', format='png', cleanup=True)
    console.print("[bold magenta]Visual map forged → dossier.png[/] (check folder!)")
except Exception as e:
    console.print(f"[red]Graph snag: {e} (install graphviz: choco install graphviz if on Windows)[/]")

console.print("\n[bold red]PHANTOM FORGED – @redbeardbradx[/]\n[green]Empire ready. Squat 225x5, then test on a dummy.[/]")