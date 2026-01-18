#!/usr/bin/env python3
"""Collect observations from day 31 (and Feb 29) that were missed."""

import requests
import json
import time
from datetime import datetime

OUTPUT_DIR = "../data/expanded_cache"
PROGRESS_FILE = f"{OUTPUT_DIR}/progress.json"
MISSING_DAYS_FILE = f"{OUTPUT_DIR}/missing_days_progress.json"
RATE_LIMIT_DELAY = 1.1

BOUNDS = {
    "swlat": 36.9979, "swlng": -114.0529,
    "nelat": 42.0013, "nelng": -109.0410
}

# Same taxa as main scraper - adjust if needed
TAXONS = [
    {"id": 47158, "name": "Insecta"},
    {"id": 47157, "name": "Arthropoda"},
    {"id": 1, "name": "Animalia"},
    {"id": 47126, "name": "Plantae"},
    {"id": 3, "name": "Aves"},
    {"id": 47178, "name": "Actinopterygii"},
]

# Months with 31 days
MONTHS_31 = [1, 3, 5, 7, 8, 10, 12]
# Leap years in our range
LEAP_YEARS = [2008, 2012, 2016, 2020, 2024]

def log(msg):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {msg}")
    with open(f"{OUTPUT_DIR}/missing_days.log", "a") as f:
        f.write(f"[{timestamp}] {msg}\n")

def load_missing_progress():
    try:
        with open(MISSING_DAYS_FILE) as f:
            return json.load(f)
    except:
        return {"completed": {}, "features": []}

def save_missing_progress(data):
    with open(MISSING_DAYS_FILE, 'w') as f:
        json.dump(data, f)

def collect_day(taxon_id, taxon_name, year, month, day):
    """Collect one specific day."""
    features = []
    page = 1
    date_str = f"{year}-{month:02d}-{day:02d}"
    
    while page <= 20:  # Fewer pages needed for single day
        params = {
            "taxon_id": taxon_id,
            "swlat": BOUNDS["swlat"], "swlng": BOUNDS["swlng"],
            "nelat": BOUNDS["nelat"], "nelng": BOUNDS["nelng"],
            "per_page": 200, "page": page,
            "d1": date_str,
            "d2": date_str,
            "order_by": "observed_on"
        }
        
        try:
            resp = requests.get("https://api.inaturalist.org/v1/observations", 
                              params=params, timeout=60)
            data = resp.json()
            results = data.get("results", [])
            
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
                            "year": year, "month": month, "day": day,
                            "source": "inat"
                        })
                    except:
                        pass
            
            if len(results) < 200:
                break
            
            page += 1
            time.sleep(RATE_LIMIT_DELAY)
            
        except Exception as e:
            log(f"  Error: {e}")
            time.sleep(5)
            break
    
    return features

def main():
    progress = load_missing_progress()
    completed = progress.get("completed", {})
    all_features = progress.get("features", [])
    
    log(f"=== COLLECTING MISSING DAYS (31st + Feb 29) ===")
    log(f"Resuming: {len(all_features):,} records, {len(completed)} day-keys done")
    
    # Build list of all missing days
    missing_days = []
    
    for year in range(2008, 2027):
        # Day 31 for applicable months
        for month in MONTHS_31:
            missing_days.append((year, month, 31))
        
        # Feb 29 for leap years
        if year in LEAP_YEARS:
            missing_days.append((year, 2, 29))
    
    total_keys = len(missing_days) * len(TAXONS)
    log(f"Total day-taxon combinations to check: {total_keys}")
    
    for taxon in TAXONS:
        for year, month, day in missing_days:
            key = f"{taxon['id']}-{year}-{month}-{day}"
            
            if key in completed:
                continue
            
            features = collect_day(taxon['id'], taxon['name'], year, month, day)
            all_features.extend(features)
            
            log(f"{taxon['name']} {year}-{month:02d}-{day:02d}: +{len(features):,} (total: {len(all_features):,})")
            
            completed[key] = len(features)
            progress = {"completed": completed, "features": all_features}
            save_missing_progress(progress)
    
    log(f"\nDone! {len(all_features):,} additional observations from missing days")

if __name__ == "__main__":
    main()
