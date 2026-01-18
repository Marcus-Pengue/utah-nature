"""
Collect ALL Utah iNaturalist observations using place_id pagination.
"""

import requests
import csv
import time
import gzip
from datetime import datetime

PLACE_ID = 39
OUTPUT_FILE = "../data/inat_utah_full.csv.gz"
PER_PAGE = 200
RATE_LIMIT = 1.0

def collect_all():
    id_above = 0
    total = None
    count = 0
    
    with gzip.open(OUTPUT_FILE, 'wt', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['species','common_name','latitude','longitude','year','month','day','source','taxon','observation_id'])
        
        while True:
            params = {
                'place_id': PLACE_ID,
                'per_page': PER_PAGE,
                'order': 'asc',
                'order_by': 'id',
                'id_above': id_above
            }
            
            try:
                r = requests.get('https://api.inaturalist.org/v1/observations', 
                                params=params, timeout=60)
                
                if r.status_code != 200:
                    print(f"Error {r.status_code}, retrying...")
                    time.sleep(5)
                    continue
                
                data = r.json()
                results = data.get('results', [])
                
                if total is None:
                    total = data.get('total_results', 0)
                    print(f"Total to collect: {total:,}")
                
                if not results:
                    break
                
                for obs in results:
                    taxon = obs.get('taxon') or {}
                    geojson = obs.get('geojson') or {}
                    coords = geojson.get('coordinates') or [None, None]
                    
                    date = obs.get('observed_on') or ''
                    year, month, day = '', '', ''
                    if date:
                        parts = date.split('-')
                        year = parts[0] if len(parts) > 0 else ''
                        month = parts[1] if len(parts) > 1 else ''
                        day = parts[2] if len(parts) > 2 else ''
                    
                    writer.writerow([
                        taxon.get('name', ''),
                        taxon.get('preferred_common_name', ''),
                        coords[1],
                        coords[0],
                        year, month, day,
                        'inaturalist',
                        taxon.get('iconic_taxon_name', ''),
                        obs.get('id', '')
                    ])
                    count += 1
                
                id_above = results[-1]['id']
                
                if count % 10000 == 0:
                    print(f"{datetime.now().strftime('%H:%M:%S')} - {count:,} / {total:,} ({100*count/total:.1f}%)")
                    f.flush()
                
                time.sleep(RATE_LIMIT)
                
            except Exception as e:
                print(f"Error: {e}, retrying...")
                time.sleep(10)
    
    print(f"Done! Total: {count:,}")

if __name__ == "__main__":
    collect_all()
