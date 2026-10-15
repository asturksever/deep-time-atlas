# Deep Time Atlas

Scrub through 600 million years of plate tectonics on a photorealistic 3D globe, built entirely on open data.

- **Globe:** https://asturksever.github.io/deep-time-atlas/
- **2D museum-screen map:** https://asturksever.github.io/deep-time-atlas/atlas.html

Each piece of continental crust from the Merdith et al. (2021) plate model is draped with today's NASA satellite imagery and turned by its own plate's rotation for the age you pick. Drag the ruler or press Play to travel in time, turn the globe, and search any city of 15,000 people or more to see where its rock was. `#ma240` at the end of the address opens at 240 million years ago.

The surface shows today's Earth carried back in time, so ice, deserts and forests are modern. Before about 250 Ma, east-west positions are the model's best fit, because palaeomagnetism records latitude only.

## Build

```bash
pip install -r requirements.txt   # pygplates, shapely, numpy, playwright
make data model    # optional: fetch the Merdith 2021 files and rebuild build/model.json with pyGPlates
make places        # optional: rebuild build/places.json from GeoNames (needs assets/src, see below)
make page          # writes docs/ (GitHub Pages), dist/ (single files for Artifacts) and build/ previews
```

`build/model.json` and `build/places.json` are committed, so `make page` works without pyGPlates. To preview, serve `docs/` with any static server (for example `python3 -m http.server -d docs`) and open the address it prints.

The raw downloads go in `assets/src/` (ignored by git):
- `bluemarble.jpg`: https://eoimages.gsfc.nasa.gov/images/imagerecords/73000/73751/world.topo.bathy.200407.3x5400x2700.jpg, resized to `assets/earth-4k.jpg` (4096x2048).
- `cities15000.txt` and `countryInfo.txt`: https://download.geonames.org/export/dump/

`HANDOVER.md` explains the architecture and decisions, and `DESIGN.md` is the design system.

## Sources

- Plate model: Merdith, A.S. et al. (2021), *A continuous, kinematic full-plate motion model from 1 Ga to present*, Earth-Science Reviews 214, 103477. CC BY 4.0, via the EarthByte group's GPlates Web Service repository. Rotations computed with pyGPlates.
- Imagery: NASA Earth Observatory, Blue Marble Next Generation with topography and bathymetry, July 2004 (Reto Stöckli).
- City search: GeoNames, CC BY 4.0.
- Geologic time scale and period colours: International Commission on Stratigraphy, ICS chart 2023/09.
- Rendering: three.js (globe) and d3-geo (2D map), loaded from public CDNs.
