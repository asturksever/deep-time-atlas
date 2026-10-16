"""Build the pages from the templates and build/model.json.

src/template.html -> dist/deep-time-atlas.html   (2D museum screen, model inlined, single self-contained file)
src/globe.html    -> dist/deep-time-globe.html   (3D globe; loads model.json, earth-2k.jpg, earth-4k.jpg and places.json next to it)

The globe's model.json is a compact v2 encoding of build/model.json: each plate's quaternion row is stored as second
differences along time (4 interleaved components), and each ring as differences between consecutive vertices. The
numbers are exactly the same after decoding; it only compresses better (about 400 KB gzipped instead of 570 KB).

build/ also gets preview copies with a doctype for local checks (the Artifact host adds its own skeleton).
docs/ is the GitHub Pages site: index.html (globe) and atlas.html (2D), with a doctype, plus the files they load.
"""
import json
import shutil
from pathlib import Path

root = Path(__file__).resolve().parent.parent
model_text = (root / "build/model.json").read_text()
HEAD = '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'


def diff(row, k):
    return row[:k] + [row[i] - row[i - k] for i in range(k, len(row))]


def compact(m):
    out = dict(m, v=2)
    out["q"] = [diff(diff(r, 4), 4) for r in m["q"]]
    out["f"] = [dict(f, r=diff(f["r"], 2)) for f in m["f"]]
    return json.dumps(out, separators=(",", ":"))


(root / "docs").mkdir(exist_ok=True)
(root / "docs/.nojekyll").write_text("")
pages = [("src/template.html", "deep-time-atlas", "atlas.html", True), ("src/globe.html", "deep-time-globe", "index.html", False)]
for src, name, site, inline in pages:
    html = (root / src).read_text()
    if inline:
        assert "__MODEL__" in html, src
        html = html.replace("__MODEL__", model_text)
    (root / f"dist/{name}.html").write_text(html)
    (root / f"build/{name}.preview.html").write_text(HEAD + html)
    (root / f"docs/{site}").write_text(HEAD + html)
    print(root / f"dist/{name}.html", len(html) // 1024, "KB")

compact_text = compact(json.loads(model_text))
for d in ("dist", "docs"):
    (root / d / "model.json").write_text(compact_text)
print("model.json", len(compact_text) // 1024, "KB (globe, compact v2)")
for d in ("dist", "build", "docs"):
    for img in ("earth-2k.jpg", "earth-4k.jpg"):
        shutil.copy(root / "assets" / img, root / d / img)
if (root / "build/places.json").exists():   # made by scripts/gazetteer.py
    for d in ("dist", "docs"):
        shutil.copy(root / "build/places.json", root / d / "places.json")
