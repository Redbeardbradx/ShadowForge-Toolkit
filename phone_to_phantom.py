
#!/usr/bin/env python3
import argparse, requests
from rich.console import Console
from rich.table import Table
from rich import box
from graphviz import Digraph
import shutil, os

console = Console()
console.print('[bold red]PHONE TO PHANTOM v2  REAL DATA[/] @redbeardbradx')

parser = argparse.ArgumentParser()
parser.add_argument('--phone', required=True)
args = parser.parse_args()

phone = args.phone.replace('-','').replace(' ','').replace('(','').replace(')','')
console.print(f'[bold green]Hunting:[/] [yellow]{phone}[/]')

found = {'Names': [], 'Addresses': [], 'Carrier': []}

# NumLookupAPI  free tier, always works
r = requests.get(f'https://api.numlookupapi.com/v1/validate/{phone}?apikey=DEMO')
data = r.json()
if data.get('valid'):
    if data.get('name'): found['Names'].append(data['name'])
    if data.get('location'): found['Addresses'].append(data['location'])
    if data.get('carrier'): found['Carrier'].append(data['carrier'])

# Table
table = Table(box=box.ROUNDED)
table.add_column('Type', style='cyan')
table.add_column('Result', style='white')
for k, v in found.items():
    if v:
        table.add_row(k, '\n'.join(v))
console.print(table)

# PNG with blue boxes
dot = Digraph()
dot.node('A', phone, shape='box', style='filled', color='red')
i = 0
for v in found.values():
    for item in v:
        dot.node(str(i), item, shape='ellipse', color='lightblue')
        dot.edge('A', str(i))
        i += 1
dot.render('dossier', format='png', cleanup=True)
console.print('[bold magenta]MAP  dossier.png[/]')

shutil.copy2('dossier.png', os.path.expanduser('~/Desktop/dossier.png'))
console.print('[green]Copied to Desktop[/]')
