import argparse
import os
import requests
import time
import random
from termcolor import colored
import pandas as pd

TOR_PROXIES = {'http': 'socks5h://127.0.0.1:9050', 'https': 'socks5h://127.0.0.1:9050'}
UAS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
]
LOG_FILE = r"E:\ShadowForge-Toolkit\osint_logs.csv"

def numverify_lookup(number, proxies):
    key = os.getenv('NUMVERIFY_API_KEY')
    if not key:
        print(colored("[!] No key set", "red"))
        return None
    try:
        url = f"https://apilayer.net/api/validate?access_key={key}&number={number.lstrip('+')}&country_code=US&format=1"
        headers = {'User-Agent': random.choice(UAS)}
        resp = requests.get(url, headers=headers, proxies=proxies, timeout=30)
        data = resp.json()
        if data.get('valid'):
            print(colored(f"[+] Valid: {data['international_format']}", "green"))
            print(colored(f"[+] Carrier: {data.get('carrier', 'N/A')}", "green"))
            print(colored(f"[+] Location: {data.get('location', 'N/A')}", "green"))
            print(colored(f"[+] Line Type: {data.get('line_type', 'N/A')}", "green"))
        return data
    except Exception as e:
        print(colored(f"[!] API error: {e}", "red"))
        return None

def bing_dorks(number, proxies):
    clean = number.lstrip('+').replace('-', '')
    dorks = [f'"{clean}"', f'intext:"{clean}" filetype:pdf']
    for dork in dorks:
        try:
            url = f"https://www.bing.com/search?q={requests.utils.quote(dork)}"
            headers = {'User-Agent': random.choice(UAS)}
            resp = requests.get(url, headers=headers, proxies=proxies, timeout=15)
            if "No results" not in resp.text:
                print(colored(f"[HIT] {dork}", "yellow"))
        except: pass
        time.sleep(3)

def log_results(data, number):
    flat = { 'number': number, 'valid': data.get('valid', False) if data else False, 'carrier': data.get('carrier', '') if data else '', 'location': data.get('location', '') if data else '', 'line_type': data.get('line_type', '') if data else '', 'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S') }
    df = pd.DataFrame([flat])
    mode = 'a' if os.path.exists(LOG_FILE) else 'w'
    df.to_csv(LOG_FILE, mode=mode, header=mode=='w', index=False)
    print(colored(f"[+] Logged → {LOG_FILE}", "blue"))

def main():
    parser = argparse.ArgumentParser(description="ShadowForge OSINT — Phone Recon (Tor Ready)")
    parser.add_argument('--phone', required=True)
    parser.add_argument('--no-proxy', action='store_true', help='Disable Tor proxy')
    args = parser.parse_args()

    proxies = None if args.no_proxy else TOR_PROXIES

    print(colored("\n[OFFENSIVE CHAIN STARTED]", "red"))
    print(colored(f"Target: {args.phone}\n", "red"))

    result = numverify_lookup(args.phone, proxies)
    bing_dorks(args.phone, proxies)
    log_results(result or {}, args.phone)

    print(colored("\n[CHAIN COMPLETE]", "red"))

if __name__ == "__main__":
    main()