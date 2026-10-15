"""Inject build/model.json into the page templates.

src/template.html -> dist/deep-time-atlas.html   (2D museum screen, single self-contained file)
src/globe.html    -> dist/deep-time-globe.html   (3D globe; needs earth-4k.jpg next to it)

build/ also gets preview copies with a doctype for local checks (the Artifact host adds its own skeleton).
docs/ is the GitHub Pages site: index.html (globe) and atlas.html (2D), with a doctype, plus the files they load.
"""
import shutil
from pathlib import Path
root = Path(__file__).resolve().parent.parent
model = (root / "build/model.json").read_text()
HEAD = '<!doctype html>\n<html lang="en">\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
(root / "docs").mkdir(exist_ok=True)
(root / "docs/.nojekyll").write_text("")
for src, name, site in [("src/template.html", "deep-time-atlas", "atlas.html"), ("src/globe.html", "deep-time-globe", "index.html")]:
    html = (root / src).read_text()
    assert "__MODEL__" in html, src
    page = html.replace("__MODEL__", model)
    (root / f"dist/{name}.html").write_text(page)
    (root / f"build/{name}.preview.html").write_text(HEAD + page)
    (root / f"docs/{site}").write_text(HEAD + page)
    print(root / f"dist/{name}.html", len(page) // 1024, "KB")
for d in ("dist", "build", "docs"):
    shutil.copy(root / "assets/earth-4k.jpg", root / d / "earth-4k.jpg")
if (root / "build/places.json").exists():   # made by scripts/gazetteer.py
    for d in ("dist", "docs"):
        shutil.copy(root / "build/places.json", root / d / "places.json")
