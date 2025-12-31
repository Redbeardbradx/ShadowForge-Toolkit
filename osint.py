import argparse, subprocess, requests, json
from bs4 import BeautifulSoup
from termcolor import colored

def phone_chain(number):
    # PhoneInfoga
    subprocess.run([r'E:\ShadowForge-Toolkit\tools\phoneinfoga\phoneinfoga.exe', 'scan', '-n', number, '--all'])
    # NumLookup scrape
    resp = requests.get(f"https://numlookup.com/{number}")
    soup = BeautifulSoup(resp.text, 'html.parser')
    print(colored(soup.find('span', {'itemprop': 'name'}).text, 'green') if soup.find('span', {'itemprop': 'name'}) else 'N/A')

parser = argparse.ArgumentParser()
parser.add_argument('--phone', help='Number')
args = parser.parse_args()
if args.phone: phone_chain(args.phone)