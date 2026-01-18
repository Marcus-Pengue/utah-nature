#!/usr/bin/env python3
"""
NEON Ecological Observatory - Utah sites
"""

import requests
import json
import time
import os
from datetime import datetime

OUTPUT_DIR = "../data/neon_cache"
os.makedirs(OUTPUT_DIR, exist_ok=True)

UTAH_SITES = ['MOAB', 'ONAQ', 'REDB']

PRODUCTS = [
    'DP1.10003.001',  # Breeding landbird
    'DP1.10022.001',  # Ground beetles
    'DP1.10055.001',  # Plant phenology
    'DP1.10058.001',  # Plant presence
]

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")

def get_available_months(product_code):
    """Get available months per site for a product."""
    r = requests.get(f'https://data.neonscience.org/api/v0/products/{product_code}', timeout=30)
    if r.status_code != 200:
        return {}
    
    data = r.json()
    result = {}
    for s in data.get('data', {}).get('siteCodes', []):
        if s.get('siteCode') in UTAH_SITES:
            result[s['siteCode']] = s.get('availableMonths', [])
    return result

def download_file(url, output_path):
    """Download a file."""
    r = requests.get(url, timeout=120)
    if r.status_code == 200:
        with open(output_path, 'wb') as f:
            f.write(r.content)
        return True
    return False

def main():
    log("=== NEON Utah Data Collection ===")
    
    all_records = []
    
    for product in PRODUCTS:
        log(f"\nProduct: {product}")
        months_by_site = get_available_months(product)
        
        for site, months in months_by_site.items():
            log(f"  {site}: {len(months)} months")
            
            for month in months:
                url = f'https://data.neonscience.org/api/v0/data/{product}/{site}/{month}'
                r = requests.get(url, timeout=60)
                
                if r.status_code != 200:
                    continue
                
                data = r.json()
                files = data.get('data', {}).get('files', [])
                csv_files = [f for f in files if f.get('name', '').endswith('.csv') and 'basic' in f.get('name', '')]
                
                for f in csv_files:
                    all_records.append({
                        'product': product,
                        'site': site,
                        'month': month,
                        'file': f.get('name'),
                        'url': f.get('url'),
                        'size': f.get('size')
                    })
                
                time.sleep(0.5)
            
            log(f"    Found {len([r for r in all_records if r['site']==site])} CSV files")
    
    # Save manifest
    with open(f"{OUTPUT_DIR}/neon_manifest.json", 'w') as f:
        json.dump(all_records, f, indent=2)
    
    log(f"\nTotal: {len(all_records)} data files found")
    log(f"Saved manifest to {OUTPUT_DIR}/neon_manifest.json")

if __name__ == "__main__":
    main()
