"""
Central config for all Utah Nature scrapers
"""

# Paths
DATA_DIR = "../data"
FULL_CACHE_DIR = f"{DATA_DIR}/full_cache"
EXPANDED_CACHE_DIR = f"{DATA_DIR}/expanded_cache"

# Utah bounds (full state)
UTAH_BOUNDS = {
    "min_lat": 36.99,
    "max_lat": 42.00,
    "min_lng": -114.05,
    "max_lng": -109.04
}

# iNat place_id for Utah
INAT_PLACE_ID = 39

# Rate limits (seconds)
RATE_LIMIT = 1.0

# Expected totals (for progress tracking)
EXPECTED = {
    "inat_total": 3_477_516,
    "gbif_total": 11_592_339
}
