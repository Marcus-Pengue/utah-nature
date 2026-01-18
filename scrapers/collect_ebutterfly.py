#!/usr/bin/env python3
"""
eButterfly Data Collector - Utah Butterfly Observations
Uses their public API for citizen science butterfly records
"""

import requests
import json
import os
import time
from datetime import datetime

OUTPUT_DIR = "data/ebutterfly_cache"
OUTPUT_FILE = f"{OUTPUT_DIR}/utah_ebutterfly.json"

# Utah bounding box
UTAH_BOUNDS = {
    "min_lat": 36.9,
    "max_lat": 42.0,
    "min_lng": -114.1,
    "max_lng": -109.0
}

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def fetch_butterflies_inat():
    """Fetch butterfly observations from iNaturalist (eButterfly syncs there)"""
    url = "https://api.inaturalist.org/v1/observations"
    
    all_features = []
    
    # Butterfly families - Lepidoptera butterflies (not moths)
    butterfly_taxa = [
        47224,   # Papilionidae (Swallowtails)
        47223,   # Pieridae (Whites/Sulphurs)  
        47922,   # Lycaenidae (Blues/Coppers/Hairstreaks)
        47913,   # Nymphalidae (Brushfoots)
        47225,   # Hesperiidae (Skippers)
        54711,   # Riodinidae (Metalmarks)
    ]
    
    for taxon_id in butterfly_taxa:
        log(f"Fetching taxon {taxon_id}...")
        page = 1
        taxon_total = 0
        
        while page <= 40:  # Max 40 pages per taxon
            params = {
                "taxon_id": taxon_id,
                "swlat": UTAH_BOUNDS["min_lat"],
                "swlng": UTAH_BOUNDS["min_lng"],
                "nelat": UTAH_BOUNDS["max_lat"],
                "nelng": UTAH_BOUNDS["max_lng"],
                "quality_grade": "research,needs_id",
                "per_page": 200,
                "page": page,
                "order_by": "observed_on"
            }
            
            try:
                r = requests.get(url, params=params, timeout=30)
                if r.status_code != 200:
                    break
                    
                data = r.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                for obs in results:
                    lat = obs.get("location", "").split(",")[0] if obs.get("location") else None
                    lng = obs.get("location", "").split(",")[1] if obs.get("location") and "," in obs.get("location") else None
                    
                    if not lat or not lng:
                        continue
                    
                    taxon = obs.get("taxon", {})
                    observed = obs.get("observed_on", "")
                    year = int(observed[:4]) if observed else None
                    month = int(observed[5:7]) if observed and len(observed) > 6 else None
                    
                    features_entry = {
                        "type": "Feature",
                        "geometry": {
                            "type": "Point",
                            "coordinates": [float(lng), float(lat)]
                        },
                        "properties": {
                            "id": obs.get("id"),
                            "species": taxon.get("preferred_common_name", "Unknown"),
                            "scientific_name": taxon.get("name", ""),
                            "family": taxon.get("ancestry", "").split("/")[-2] if taxon.get("ancestry") else "",
                            "iconic_taxon": "Lepidoptera",
                            "observed_on": observed,
                            "year": year,
                            "month": month,
                            "quality_grade": obs.get("quality_grade"),
                            "photo_url": obs.get("photos", [{}])[0].get("url", "").replace("square", "medium") if obs.get("photos") else None,
                            "source": "inat_butterfly"
                        }
                    }
                    all_features.append(features_entry)
                
                taxon_total += len(results)
                page += 1
                time.sleep(0.5)
                
            except Exception as e:
                log(f"  Error: {e}")
                break
        
        log(f"  +{taxon_total} (total: {len(all_features)})")
        time.sleep(1)
    
    return all_features

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    log("=== Utah Butterfly Collection ===")
    
    features = fetch_butterflies_inat()
    
    # Deduplicate by ID
    seen = set()
    unique = []
    for f in features:
        fid = f["properties"]["id"]
        if fid not in seen:
            seen.add(fid)
            unique.append(f)
    
    log(f"Deduped: {len(features)} -> {len(unique)}")
    
    geojson = {
        "type": "FeatureCollection",
        "features": unique,
        "metadata": {
            "collected": datetime.now().isoformat(),
            "source": "iNaturalist butterfly taxa",
            "region": "Utah"
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(geojson, f)
    
    log(f"=== Done: {len(unique)} butterfly observations ===")

if __name__ == "__main__":
    main()
