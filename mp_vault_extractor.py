import json
import os
from urllib.request import urlopen, Request
import time
from urllib.error import HTTPError

MP_URL = "https://www.unrealengine.com/marketplace"
JSON_DIR = "./data"
OUT_FILE = "mp_vault_list.md"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def main():
    mp_jsons = []
    cost = 0.
    disc = 0.
    currency = ""
    count = 0
    for f in os.listdir(JSON_DIR):
        if not f.endswith(".json"):
            continue
        with open(os.path.join(JSON_DIR, f), encoding='utf-8') as fd:
            j = json.load(fd)
            count += len(j['data']['elements'])
            mp_jsons.append(j)
    
    with open(OUT_FILE, "w+", encoding='utf-8') as fd:
        fd.write(f"# Vault content\n\n")
        i = 0
        for j in mp_jsons:
            for el in j['data']['elements']:
                i += 1
                print(f"\rProcessing Vault {i}/{count}", end="")
                asset_url = f"{MP_URL}/api/assets/asset/{el['id']}"
                print(f"\nFetching URL: {asset_url}")

                req = Request(asset_url, headers=headers)

                try:
                    with urlopen(req) as f:
                        jj = json.load(f)
                        jjd = jj['data']['data']
                        fd.write(f"* [{jjd['title']}]({MP_URL}/en-US/product/{jjd['urlSlug']})\n")
                        cost += jjd['priceValue']
                        currency = jjd['currencyCode']
                        try:
                            disc += jjd['discountPriceValue']
                        except KeyError:
                            pass
                
                except HTTPError as e:
                    if e.code == 403:
                        print(f"HTTP Error 403: Forbidden for URL {asset_url}. Skipping...")
                    else:
                        print(f"HTTP Error {e.code}: {e.reason}")
                
                time.sleep(1)  # Increase the delay to 3 seconds

        fd.write(f"\n# Vault stats\n\n")
        fd.write(f"* Value: {cost / 100}{currency}\n")
        fd.write(f"* Current cost: {disc / 100}{currency}\n")
        fd.write(f"* Size: {count}\n")


if __name__ == '__main__':
    main()
