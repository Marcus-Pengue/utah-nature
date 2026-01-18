#!/usr/bin/env python3
"""Download all NEON CSV files from manifest."""

import requests
import json
import os
import time
from datetime import datetime

OUTPUT_DIR = "../data/neon_cache/csvs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def main():
    with open('../data/neon_cache/neon_manifest.json') as f:
        files = json.load(f)
    
    log(f"Downloading {len(files)} files...")
    
    for i, f in enumerate(files):
        url = f.get('url')
        name = f.get('file', f'file_{i}.csv')
        path = f"{OUTPUT_DIR}/{name}"
        
        if os.path.exists(path):
            continue
        
        try:
            r = requests.get(url, timeout=60)
            if r.status_code == 200:
                with open(path, 'wb') as out:
                    out.write(r.content)
            
            if i % 50 == 0:
                log(f"  {i}/{len(files)} downloaded")
            
            time.sleep(0.3)
        except Exception as e:
            log(f"  Error {name}: {e}")
    
    log(f"Done! Files in {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
