#!/usr/bin/env python3
import argparse, subprocess, os
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from graphviz import Digraph

console = Console()

console.print(Panel("[bold red]ShadowForge-Toolkit v2.0  FINAL[/]\n[cyan]@redbeardbradx[/]\n[white]One command. Full visual phantom.[/]", box=box.ROUNDED))

parser = argparse.ArgumentParser()
sub = parser.add_subparsers(dest="module")
person = sub.add_parser("person")
person.add_argument("--username")
person.add_argument("--name")
person.add_argument("--phone")
person.add_argument("--email")
args = parser.parse_args()

if not args.module:
    parser.print_help()
    exit()

seed = args.username or args.name or args.phone or args.email or "NO SEED"
console.print(f"[bold green]Target locked:[/] [yellow]{seed}[/]")

results = {"profiles": []}

# SHERLOCK  100% working
if args.username or args.name:
    uname = (args.username or args.name or "").replace(" ", "").lower()
    console.print("[*] Sherlock hunting username...")
    try:
        cmd = ['python', 'sherlock.py', uname, '--print-found', '--timeout', '10']
        out = subprocess.check_output(cmd, cwd='sherlock', text=True, stderr=subprocess.STDOUT)
        for line in out.splitlines():
            if "http" in line:
                results["profiles"].append(line.strip())
    except Exception as e:
        console.print(f"[red]Sherlock failed (run manual test): {e}[/]")

# TABLE
table = Table(title=f"DOSSIER  {seed}", box=box.ROUNDED)
table.add_column("Type", style="cyan")
table.add_column("Count", style="green")
table.add_column("Preview", style="white")
table.add_row("Profiles", str(len(results["profiles"])), "\n".join(results["profiles"][:8]))
console.print(table)

# PNG GRAPH  guaranteed to work
console.print("[*] Forging PNG map...")
dot = Digraph()
dot.node(seed, shape='box', style='filled', color='red')
for i, p in enumerate(results["profiles"][:20]):
    dot.node(str(i), p[:50], shape='ellipse', color='lightblue')
    dot.edge(seed, str(i))
dot.render('dossier', format='png', cleanup=True)
console.print("[bold magenta]PNG CREATED  dossier.png[/]")

console.print("\n[bold red]GOD TIER ACHIEVED  @redbeardbradx[/]")
