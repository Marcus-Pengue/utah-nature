#!/usr/bin/env python3
"""
EXPANDED Collection v2 - by month, resumes, loops incomplete
"""

import requests
import json
import time
import os
from datetime import datetime

OUTPUT_DIR = "../data/expanded_cache"
PROGRESS_FILE = f"{OUTPUT_DIR}/progress.json"
RATE_LIMIT_DELAY = 0.8

BOUNDS = {"swlat": 36.9, "swlng": -114.1, "nelat": 42.0, "nelng": -109.0}

TAXONS = [
    {"id": 3, "name": "Aves"}, {"id": 47158, "name": "Insecta"},
    {"id": 47126, "name": "Plantae"}, {"id": 40151, "name": "Mammalia"},
    {"id": 47170, "name": "Fungi"}, {"id": 47119, "name": "Arachnida"},
    {"id": 26036, "name": "Reptilia"}, {"id": 20978, "name": "Amphibia"},
    {"id": 47115, "name": "Mollusca"}, {"id": 47178, "name": "Actinopterygii"},
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%H:%M:%S")
    print(f"[{ts}] {msg}")
    with open(f"{OUTPUT_DIR}/v2.log", "a") as f:
        f.write(f"[{ts}] {msg}\n")

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            return json.load(f)
    return {"completed": {}, "features": []}

def save_progress(data):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(data, f)

def collect_month(taxon_id, taxon_name, year, month):
    """Collect one month. Returns (features, is_complete)."""
    features = []
    page = 1
    
    while page <= 50:
        params = {
            "taxon_id": taxon_id,
            "swlat": BOUNDS["swlat"], "swlng": BOUNDS["swlng"],
            "nelat": BOUNDS["nelat"], "nelng": BOUNDS["nelng"],
            "per_page": 200, "page": page,
            "d1": f"{year}-{month:02d}-01",
            "d2": f"{year}-{month:02d}-28" if month == 2 else f"{year}-{month:02d}-30",
            "order_by": "observed_on"
        }
        
        try:
            resp = requests.get("https://api.inaturalist.org/v1/observations", 
                              params=params, timeout=60)
            data = resp.json()
            results = data.get("results", [])
            total = data.get("total_results", 0)
            
            if not results:
                break
            
            for obs in results:
                if obs.get("location"):
                    try:
                        lat, lng = map(float, obs["location"].split(","))
                        features.append({
                            "id": f"inat_{obs['id']}",
                            "species": obs.get("taxon", {}).get("name", ""),
                            "taxon": taxon_name,
                            "lat": lat, "lng": lng,
                            "year": year, "month": month,
                            "source": "inat"
                        })
                    except:
                        pass
            
            if len(results) < 200:
                return features, True
            
            page += 1
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            log(f"  Error: {e}")
            time.sleep(5)
    
    is_complete = len(features) < 10000
    return features, is_complete

def main():
    progress = load_progress()
    completed = progress.get("completed", {})
    all_features = progress.get("features", [])
    
    log(f"Resuming: {len(all_features):,} records, {len(completed)} months done")
    
    incomplete = []
    
    for taxon in TAXONS:
        for year in range(2008, 2027):
            for month in range(1, 13):
                key = f"{taxon['id']}-{year}-{month}"
                
                if key in completed:
                    continue
                
                features, is_complete = collect_month(taxon['id'], taxon['name'], year, month)
                all_features.extend(features)
                
                status = "✓" if is_complete else "⚠"
                log(f"{taxon['name']} {year}-{month:02d}: +{len(features):,} {status} (total: {len(all_features):,})")
                
                if is_complete:
                    completed[key] = len(features)
                else:
                    incomplete.append(key)
                
                progress = {"completed": completed, "features": all_features}
                save_progress(progress)
    
    log(f"\nDone! {len(all_features):,} total, {len(incomplete)} incomplete months")

if __name__ == "__main__":
    main()
