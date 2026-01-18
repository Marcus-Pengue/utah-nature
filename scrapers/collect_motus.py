#!/usr/bin/env python3
"""
Motus - Access Utah projects
"""

import requests
import json
import bz2
from datetime import datetime

BASE_URL = "https://motus.org/api/sgdata"
USERNAME = "marcuspengue@gmail.com"
PASSWORD = "hDmk6U!9p3CcCzZ"

# Utah project IDs from the website
UTAH_PROJECTS = [623, 684, 745, 840, 956, 961, 968]

def motus_request(endpoint, params=None):
    url = f"{BASE_URL}/{endpoint}"
    data = {"json": json.dumps(params or {})}
    r = requests.post(url, data=data, auth=(USERNAME, PASSWORD), timeout=60)
    if r.status_code == 200:
        try:
            return json.loads(bz2.decompress(r.content))
        except:
            return r.json() if r.text else None
    return None

print("=== Trying Utah Motus Projects ===")

for proj_id in UTAH_PROJECTS:
    print(f"\nProject {proj_id}:")
    
    # Try receivers for project
    result = motus_request("custom/receivers_for_project", {"projectID": proj_id})
    if result and 'error' not in result:
        print(f"  Receivers: {result}")
    
    # Try tag metadata
    result = motus_request("custom/tag_metadata_for_projects", {"projectID": [proj_id]})
    if result and 'error' not in result:
        print(f"  Tags: {type(result)} - {str(result)[:200]}")
    
    # Try batches
    result = motus_request("custom/batches_for_tag_project", {"projectID": proj_id, "batchID": 0})
    if result and 'error' not in result:
        print(f"  Batches: {type(result)}")
