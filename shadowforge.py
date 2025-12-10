#!/usr/bin/env python3
import argparse, requests, os, time, random, shutil
from rich.console import Console
from rich.table import Table
from rich import box
from graphviz import Digraph
from bs4 import BeautifulSoup
from datetime import datetime

console = Console()
console.print('[bold red]ShadowForge v5.2  BLUE BOXES FULL SYSTEM MODE[/] @redbeardbradx')

# -----------------------------------
# ARGUMENT PARSER
# -----------------------------------
parser = argparse.ArgumentParser()
parser.add_argument('--phone', required=True)
args = parser.parse_args()
phone = args.phone.replace('-', '').replace(' ', '')

console.print(f'[bold green]Hunting:[/] [yellow]{phone}[/]')


# ===================================
#   USER AGENT ROTATION
# ===================================
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 16_2 like Mac OS X)"
]


def get_headers():
    return {"User-Agent": random.choice(USER_AGENTS)}


# ===================================
#   PROXY ROTATION (Option A)
# ===================================
PROXY_LIST = [
    "http://198.8.94.170:4145",
    "http://45.91.93.166:80",
    "http://103.169.187.25:8080",
    "http://51.159.66.158:3128",
]

def get_proxy():
    return {"http": random.choice(PROXY_LIST), "https": random.choice(PROXY_LIST)}


# ===================================
#   LOGGING SYSTEM
# ===================================
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
logfile = os.path.join(LOG_DIR, f"{datetime.now().date()}.txt")

def log(msg):
    with open(logfile, "a") as f:
        f.write(msg + "\n")


# ===================================
#   EXTRACTION STORAGE
# ===================================
data = {'Name': [], 'Address': [], 'Relatives': []}


# ===================================
#   SITE SCRAPERS
# ===================================

# --- TPS -------------------------------------------------------
def scrape_truepeoplesearch(phone):
    console.print("[cyan]Attempting TruePeopleSearch...[/]")

    url = f"https://www.truepeoplesearch.com/results?phoneno={phone}"

    try:
        r = requests.get(url, headers=get_headers(), proxies=get_proxy(), timeout=10)
    except:
        return False

    if r.status_code != 200 or "captcha" in r.text.lower() or "access denied" in r.text.lower():
        return False

    soup = BeautifulSoup(r.text, 'lxml')
    hits = soup.select('.result-box')
    if not hits:
        return False

    first = hits[0]
    name = first.select_one('.name-link')
    addr = first.select_one('.address-link')
    relatives = first.select('.link-to-more-relatives')

    if name: data['Name'].append(name.get_text(strip=True))
    if addr: data['Address'].append(addr.get_text(strip=True))
    for rel in relatives[:5]:
        data['Relatives'].append(rel.get_text(strip=True))

    return True


# --- FPS -------------------------------------------------------
def scrape_fastpeoplesearch(phone):
    console.print("[cyan]Fallback: FastPeopleSearch...[/]")

    url = f"https://www.fastpeoplesearch.com/phone/{phone}"

    try:
        r = requests.get(url, headers=get_headers(), proxies=get_proxy(), timeout=10)
    except:
        return False

    if r.status_code != 200 or "captcha" in r.text.lower():
        return False

    soup = BeautifulSoup(r.text, 'lxml')
    name = soup.select_one('span.name, h1')
    addr = soup.select_one('.detail-box, .address')
    relatives = soup.select('.relative-name a')

    if name: data['Name'].append(name.get_text(strip=True))
    if addr: data['Address'].append(addr.get_text(strip=True))
    for rel in relatives[:5]:
        data['Relatives'].append(rel.get_text(strip=True))

    return True


# --- ZLookup -------------------------------------------------------
def scrape_zlookup(phone):
    console.print("[cyan]Fallback: ZLookup...[/]")

    url = f"https://www.zlookup.com/phone/{phone}"

    try:
        r = requests.get(url, headers=get_headers(), proxies=get_proxy(), timeout=10)
    except:
        return False

    if r.status_code != 200:
        return False

    if "Unknown" in r.text:
        return False

    # Just stores basic meta because ZLookup doesn't give names
    data['Name'].append("ZLookup Result")
    data['Address'].append("Basic carrier/location lookup")
    return True


# ===================================
#   MASTER SCRAPER
# ===================================
def run_all_scrapers():
    if scrape_truepeoplesearch(phone):
        log(f"{phone}: TPS SUCCESS")
        return

    if scrape_fastpeoplesearch(phone):
        log(f"{phone}: FPS SUCCESS")
        return

    if scrape_zlookup(phone):
        log(f"{phone}: ZLookup SUCCESS")
        return

    log(f"{phone}: NO DATA FOUND")


# Run scrapers
run_all_scrapers()


# ===================================
#   TABLE OUTPUT
# ===================================
table = Table(box=box.ROUNDED)
table.add_column("Type")
table.add_column("Result")

for k, v in data.items():
    if v:
        table.add_row(k, "\n".join(v))

console.print(table)


# ===================================
#   GRAPHVIZ OUTPUT
# ===================================
dot = Digraph()
dot.node("A", phone, shape="box", style="filled", color="red")

i = 0
for v in data.values():
    for item in v:
        dot.node(str(i), item[:40], shape="ellipse", color="lightblue")
        dot.edge("A", str(i))
        i += 1

dot.render("dossier", format="png", cleanup=True)
console.print("[bold magenta]dossier.png created  BLUE BOXES LIVE[/]")

try:
    shutil.copy2("dossier.png", os.path.expanduser("~/Desktop/dossier.png"))
    console.print("[green]Copied to Desktop[/]")
except:
    console.print("[yellow]Could not copy to desktop.[/]")
