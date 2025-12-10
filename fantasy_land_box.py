
#!/usr/bin/env python3
import argparse, os
from rich.console import Console
from rich.table import Table
from rich import box
from graphviz import Digraph
import shutil

console = Console()
console.print('[bold red]FANTASY LAND BOX v99  FINAL & PERFECT[/] @redbeardbradx')

parser = argparse.ArgumentParser()
parser.add_argument('--phone')
parser.add_argument('--name')
parser.add_argument('--address')
parser.add_argument('--username')
args = parser.parse_args()

seed = args.phone or args.name or args.address or args.username or 'NO SEED'
console.print(f'[bold green]Seed locked:[/] [yellow]{seed}[/]')

found = {'Names': [], 'Addresses': [], 'Phones': [], 'Usernames': []}

if args.name: found['Names'].append(args.name)
if args.address: found['Addresses'].append(args.address)
if args.phone: found['Phones'].append(args.phone)
if args.username: found['Usernames'].append(args.username)

table = Table(box=box.ROUNDED)
table.add_column('Type', style='cyan')
table.add_column('Data', style='white')
for k, v in found.items():
    if v:
        table.add_row(k, '\n'.join(v))
console.print(table)

dot = Digraph()
dot.node('SEED', seed, shape='box', style='filled', color='red')
i = 0
for items in found.values():
    for item in items:
        dot.node(str(i), item, shape='ellipse', color='lightblue')
        dot.edge('SEED', str(i))
        i += 1
dot.render('dossier', format='png', cleanup=True)
console.print('[bold magenta]MAP FORGED  dossier.png[/]')

shutil.copy2('dossier.png', os.path.expanduser('~/Desktop/dossier.png'))
console.print('[green]Saved to Desktop[/]')

console.print('[bold red]FANTASY LAND BOX v99  YOU ARE NOW UNSTOPPABLE[/]')
