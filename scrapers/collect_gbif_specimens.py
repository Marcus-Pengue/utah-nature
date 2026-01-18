#!/usr/bin/env python3
"""
GBIF Museum Specimen Collector
Gets historical museum records that are NOT from iNaturalist
These are unique physical specimens in collections
"""

import requests
import json
import os
import time
from datetime import datetime

OUTPUT_DIR = "data/gbif_specimens_cache"
OUTPUT_FILE = f"{OUTPUT_DIR}/utah_specimens.json"
PROGRESS_FILE = f"{OUTPUT_DIR}/progress.json"

UTAH_POLY = "POLYGON((-114.1 37,-109 37,-109 42,-114.1 42,-114.1 37))"

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}")

def save_progress(features, last_basis, last_offset):
    with open(PROGRESS_FILE, 'w') as f:
        json.dump({"features": features, "last_basis": last_basis, "last_offset": last_offset}, f)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE) as f:
            d = json.load(f)
            return d.get("features", []), d.get("last_basis", ""), d.get("last_offset", 0)
    return [], "", 0

def fetch_specimens():
    url = "https://api.gbif.org/v1/occurrence/search"
    
    features, last_basis, last_offset = load_progress()
    log(f"Resuming: {len(features)} existing, last_basis={last_basis}, offset={last_offset}")
    
    specimen_types = [
        "PRESERVED_SPECIMEN",
        "FOSSIL_SPECIMEN", 
        "LIVING_SPECIMEN",
        "MATERIAL_SAMPLE"
    ]
    
    # Skip to where we left off
    start_idx = specimen_types.index(last_basis) if last_basis in specimen_types else 0
    
    for basis in specimen_types[start_idx:]:
        log(f"\n=== {basis} ===")
        current_offset = last_offset if basis == last_basis else 0
        
        while True:
            params = {
                "geometry": UTAH_POLY,
                "basisOfRecord": basis,
                "hasCoordinate": "true",
                "hasGeospatialIssue": "false",
                "limit": 300,
                "offset": current_offset
            }
            
            try:
                r = requests.get(url, params=params, timeout=60)
                if r.status_code != 200:
                    log(f"  Error {r.status_code}")
                    break
                
                data = r.json()
                results = data.get("results", [])
                
                if not results:
                    break
                
                for rec in results:
                    dataset = rec.get("datasetName", "").lower()
                    if "inaturalist" in dataset:
                        continue
                    
                    lat = rec.get("decimalLatitude")
                    lng = rec.get("decimalLongitude")
                    if not lat or not lng:
                        continue
                    
                    year = rec.get("year")
                    month = rec.get("month")
                    day = rec.get("day")
                    
                    features.append({
                        "type": "Feature",
                        "geometry": {"type": "Point", "coordinates": [lng, lat]},
                        "properties": {
                            "id": f"gbif_{rec.get('gbifID')}",
                            "species": rec.get("vernacularName") or rec.get("species") or rec.get("genus") or "Unknown",
                            "scientific_name": rec.get("scientificName", ""),
                            "family": rec.get("family", ""),
                            "order": rec.get("order", ""),
                            "class": rec.get("class", ""),
                            "kingdom": rec.get("kingdom", ""),
                            "basis_of_record": basis,
                            "institution": rec.get("institutionCode", ""),
                            "collection": rec.get("collectionCode", ""),
                            "catalog_number": rec.get("catalogNumber", ""),
                            "recorded_by": rec.get("recordedBy", ""),
                            "observed_on": f"{year}-{month:02d}-{day:02d}" if year and month and day else None,
                            "year": year,
                            "month": month,
                            "source": "gbif_specimen"
                        }
                    })
                
                current_offset += len(results)
                log(f"  Offset {current_offset}: {len(features)} total specimens")
                
                if len(features) % 1000 < 300:
                    save_progress(features, basis, current_offset)
                
                if data.get("endOfRecords"):
                    break
                    
                time.sleep(0.3)
                
            except Exception as e:
                log(f"  Error: {e}")
                save_progress(features, basis, current_offset)
                time.sleep(5)
        
        last_offset = 0
    
    return features

def main():
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    log("=== GBIF Museum Specimen Collection (non-iNat) ===")
    
    features = fetch_specimens()
    
    seen = set()
    unique = []
    for f in features:
        fid = f["properties"]["id"]
        if fid not in seen:
            seen.add(fid)
            unique.append(f)
    
    geojson = {
        "type": "FeatureCollection",
        "features": unique,
        "metadata": {
            "collected": datetime.now().isoformat(),
            "source": "GBIF museum specimens (excluding iNaturalist)",
            "region": "Utah"
        }
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(geojson, f)
    
    log(f"=== Done: {len(unique)} museum specimens ===")

if __name__ == "__main__":
    main()
