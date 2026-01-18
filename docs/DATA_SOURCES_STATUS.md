# Utah Wildlife Data Sources - Status & Requirements

## ✅ WORKING - Data Collected

| Source | Records | Type | Notes |
|--------|---------|------|-------|
| iNaturalist (expanded) | 450k+ | Observations | Running, all taxa |
| eBird Historical | 131k+ | Birds | Running, 5 years daily |
| iDigBio | 60k+ | Museum specimens | Running |
| GBIF Specimens | 33k+ | Museum only | Running, excludes iNat |
| Movebank | 168k | GPS tracks | Coyotes, pumas, curlews |
| Native Bees | 27,534 | Pollinators | Andrenidae, Halictidae |
| eBird Recent | 14k | Birds | 30-day hotspot data |
| EDDMapS | 14,951 | Invasive species | Complete |
| NPS Species | 9,883 | Park inventories | 12 Utah parks |
| Neotoma | 7,534 | Paleontology | Fossil/pollen sites |
| OBIS | 4,000 | Aquatic | Great Salt Lake area |
| Mushroom Observer | 1,595 | Fungi | Used bbox center |
| Xeno-canto | 1,320 | Bird audio | v3 API with key |
| Fire History | 1,087 | NIFC perimeters | Habitat disturbance |
| USGS Water | 827 | Stream gauges | Water quality |
| NOAA Weather | 6 years | Climate | Historical |
| HawkCount | 3 | Raptor migration | Limited sites |

## 🔐 NEEDS AUTHENTICATION/ACCESS

| Source | Status | Requirements |
|--------|--------|--------------|
| Motus | Auth works, no project access | Request access to Utah projects: 623, 684, 745, 840, 956, 961, 968 |
| FeederWatch | 403 Forbidden | Cornell account + data request |
| Wildlife Insights | 401 Unauthorized | Register at wildlifeinsights.org |
| HerpMapper | No API | Submit data request form |
| SEINet/Symbiota | 403 Forbidden | May need institutional access |

## ❌ API DOWN/UNAVAILABLE

| Source | Status | Notes |
|--------|--------|-------|
| BISON (USGS) | DNS failure | bison.usgs.gov not resolving |
| VertNet | 500/404 errors | Server issues |
| FishBase | Connection error | API appears down |
| AntWeb | 403 Forbidden | Blocked |

## 📄 NO PUBLIC API (Would need scraping/bulk download)

| Source | Status | How to get data |
|--------|--------|-----------------|
| BAMONA (Butterflies/Moths) | 404 on API | Manual data request |
| Odonata Central | No API found | Contact for data export |
| BugGuide | 403 | No public API |
| CalPhotos | Returns HTML | Would need HTML scraping |
| USGS BBS | CSV downloads | Download from sciencebase.gov |
| Reef Life Survey | 403 | Request data access |
| PRISM Climate | Bulk downloads | Download gridded data |

## 🔄 DUPLICATES OF iNATURALIST (Skip)

| Source | Why skip |
|--------|----------|
| Native bees filter | Subset of expanded iNat |
| Monarch filter | Subset of expanded iNat |
| Butterfly filter | Subset of expanded iNat |
| Odonata filter | Subset of expanded iNat |
| Audubon winter birds | Subset of expanded iNat |

## 📋 TO TRY NEXT

- SCAN (Symbiota Collections) - different portal
- Utah DWR hunting surveys - state data
- Great Salt Lake bird surveys - specialized
- USDA PLANTS database - expanded
- NatureServe - conservation status
