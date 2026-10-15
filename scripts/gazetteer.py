"""GeoNames cities15000 + countryInfo -> build/places.json, the search list for the globe.

Rows are [name, ascii name or 0 when identical, country code, lat x100, lon x100, population], most populous first.
Source: GeoNames (CC BY 4.0), https://download.geonames.org/export/dump/
"""
import json
from pathlib import Path
root = Path(__file__).resolve().parent.parent
src = root / "assets/src"
countries = {}
for line in (src / "countryInfo.txt").read_text(encoding="utf-8").splitlines():
    if line.startswith("#") or not line.strip():
        continue
    f = line.split("\t")
    countries[f[0]] = f[4]
rows = []
for line in (src / "cities15000.txt").read_text(encoding="utf-8").splitlines():
    f = line.split("\t")
    name, ascii_, lat, lon, cc, pop = f[1], f[2], float(f[4]), float(f[5]), f[8], int(f[14] or 0)
    rows.append([name, 0 if ascii_ == name else ascii_, cc, round(lat * 100), round(lon * 100), pop])
rows.sort(key=lambda r: -r[5])
out = root / "build/places.json"
out.write_text(json.dumps({"c": countries, "r": rows}, ensure_ascii=False, separators=(",", ":")))
print(out, len(rows), "places", out.stat().st_size // 1024, "KB")
