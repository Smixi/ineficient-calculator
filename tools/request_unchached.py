import argparse
import requests
import argparse
from time import sleep

parser = argparse.ArgumentParser()
parser.add_argument("path")
args = parser.parse_args()
i =0
while True:
    i = i + 1
    r = requests.post(f'http://localhost/{args.path}', json={'expression': '1+' + str(i)})
    if r.status_code != 200:
        print(r)
    else: 
        print(r, r.json())
    sleep(0.3)