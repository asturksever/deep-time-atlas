# Deep Time Atlas: handover for Claude Code

Read this first. It doubles as the project's CLAUDE.md (copy or symlink it as `CLAUDE.md` in the repo root).

## What this is

An interactive, single-file web page that recreates a museum plate-tectonics display: a Mollweide world map you can scrub from 600 million years ago (Ma) to today. It uses only open data. The museum screen it copies has a ruler across the top (600, 560, 540 ... 20, 0.05, 0 "million years ago") with a red marker at the current age, and the reconstructed globe below it. The reference was a photo of the exhibit screen.

Live site: https://asturksever.github.io/deep-time-atlas/ (globe) and `atlas.html` (2D map), served from `docs/`. The same pages can also be published as Claude artifacts from `dist/`.

Brief: work out what the museum screen shows and rebuild it on open data.

## Owner preferences (apply to all output)

- Never use em dashes in any output, including UI copy, comments and commit messages.
- For clear requests, answer first and then flag assumptions. Ask a clarifying question when a request is vague.

## Quick start

```bash
pip install --break-system-packages -r requirements.txt   # pygplates 1.0.0, shapely, numpy, playwright
make all        # fetch data -> build/model.json -> dist/deep-time-atlas.html
make shots      # optional visual check (needs: python3 -m playwright install chromium)
```

Rebuilding takes about 10 seconds after the data is fetched. Output is about 2 MB, fully self-contained except for d3 from cdnjs.

## Repo layout

```
HANDOVER.md            this file
DESIGN.md              design system for the Atlas and Globe (Stitch-ready)
Makefile               data / model / page / shots
requirements.txt
scripts/fetch_model.sh sparse-clones the Merdith 2021 files into data/MERDITH2021
scripts/reconstruct.py exports present-day geometry + per-plate rotation quaternions to build/model.json
scripts/build.py       injects model.json into src/template.html at __MODEL__ -> dist/
scripts/screenshot.py  Playwright screenshots at 600/240/90/0 Ma, desktop and phone
src/template.html      the page: HTML, CSS, JS (d3 v7.9.0 from cdnjs)
dist/deep-time-atlas.html  current build
dist/deep-time-atlas-v1.html  v1 build, kept for reference
```

## Data and licence

- Model: Merdith, A.S. et al. (2021), "A continuous, kinematic full-plate motion model from 1 Ga to present", Earth-Science Reviews 214, 103477. CC BY 4.0. The attribution in the page footer must stay.
- Source used: GitHub `GPlates/gplates-web-service`, path `django/GWS/data/deprecated/MODELS/MERDITH2021/`:
  - `1000_0_rotfile_Merdith_et_al.rot` (rotations, palaeomagnetic reference frame)
  - `shapes_static_polygons_Merdith_et_al.gpmlz` (crust; `gpml:Basin` features dropped = oceanic)
  - `shapes_coastlines_Merdith_et_al_v2.gpmlz` (land, covers the full 1 Ga; v1 only goes back to about 400 Ma)
- The canonical upstream is EarthByte (earthbyte.org webdav, Zenodo). Those hosts were blocked in the build sandbox, which is why we used the GitHub copy. If they're reachable, prefer the official zip. It also has plate topologies (ridges, trenches) that the GitHub copy lacks.
- The folder `MULLER2022` in the same repo holds the optimised-mantle-frame rotation file for the same geometry (Müller et al. 2022). It's a drop-in alternative if you want a mantle reference frame instead of palaeomag.
- Period colours and boundaries come from the ICS chart 2023/09 (hard-coded in `PERIODS`).

## Architecture (why it's built this way)

1. **Pre-baking frames was rejected.** Reconstructing every 5 Myr with pygplates and storing rings came to 31 MB raw (11 MB gzipped). Too big.
2. **What we do instead:** ship each polygon once in present-day coordinates (lon/lat x100 ints) plus one rotation per plate per 5 Myr step, stored as a unit quaternion x1e7. That's 432 plates x 121 steps. The browser slerps between steps and rotates each ring on the fly, so playback is smooth at any fractional age.
3. **Precision trap:** quaternions quantised at 1e5 gave up to 0.19 degrees of error at 550 Ma. At 1e7 they match pygplates to better than 0.001 degrees. Keep 1e7.
4. **Simplification:** Douglas-Peucker at 0.12 degrees on unwrapped longitudes (shapely), with slivers under 2.5e-5 sr dropped. That leaves about 37k vertices in total.
5. **Valid time:** each feature carries its begin/end age, and the page hides it outside that window (`alive()`). Features that end before 600 Ma are dropped at export.
6. **Rendering:** canvas 2D with d3-geo. The Mollweide raw projection is hand-written in the page, so only d3 core is needed. Rings are reversed when `d3.geoArea > 2π` to fix winding. Draw order: ocean (radial gradient), crust (lighter blue), land (olive), then the graticule and city pins on top.
7. **Cities:** a present-day point is assigned to a plate with `pygplates.PlatePartitioner` on the static polygons, then rotated with that plate's quaternion. Cape Town lands on plate 77032 (a small Merdith sub-plate), which is correct.

## UI spec (v1, keep unless asked)

- One dark "museum display case" look (single theme on purpose, with `color-scheme: dark`). Fonts: Bricolage Grotesque (display) and JetBrains Mono (numbers and labels).
- The ruler uses the exhibit's exact tick stops. You can drag or click it (it snaps to ticks within about 6 px), and arrow keys step between ticks. A strip of ICS period colours runs underneath.
- Play animates 600 to 0 Ma. Speed slider runs 5 to 60 Myr per second, default 20. "Back to 600 Ma" resets.
- The story panel shows the period name and dot plus a short caption from `STORY`. Each caption covers the ages up to the next one.
- City toggles (London, New York, Rio, Cape Town, Mumbai, Sydney, Tokyo, Istanbul) draw pins and show a palaeolatitude readout.
- Must work at 390 px wide with no horizontal scroll. Verified in v1.

## v2 interaction rules (added 12 Oct 2026, keep unless asked)

- One rAF loop (`tick`) drives everything that moves: playback, the age spring, pin springs and globe inertia. It stops when nothing is moving. Anything that changes state calls `render()`.
- Springs use Apple's response/damping-ratio parameters (`stepSpring`). Default damping 1.0. Only a flick gets damping 0.85.
- Ruler: responds on pointer-down. A press on the cursor grabs it with its offset kept; a press elsewhere springs there straight away. Dragging tracks 1:1 and rubber-bands past 0 and 600. On release, the velocity from the last 100 ms is projected (`project`, deceleration 0.998). A flick lands on the stop nearest the projected point; a slow release only snaps within 6 px.
- Keyboard steps are instant on purpose. Don't animate keyboard actions.
- Globe: drag tracks the surface 1:1 and release keeps the spin, decaying at 0.998 per ms. Map/Globe switch is a 240 ms fade+scale+blur.
- Deep links: `#ma240`, `#globe`, `#globe-ma240`. The hash is rewritten when motion settles.
- `prefers-reduced-motion`: springs and inertia become instant jumps; the story swap becomes an opacity-only fade.
- Local check: `build/preview.html` is the same page with a doctype. Serve `build/` and open it, since the bare dist file renders in quirks mode outside the Artifact host.

## Deep Time Globe (3D, added 15 Oct 2026)

`src/globe.html` -> `dist/deep-time-globe.html`, a full-screen photorealistic globe (three.js 0.160.0 from jsDelivr via an import map). It needs `model.json`, `earth-2k.jpg`, `earth-4k.jpg` and `places.json` next to it: NASA Blue Marble Next Generation, topography and bathymetry, July 2004, resized to 4096x2048 (`assets/earth-4k.jpg`; the 5400x2700 original is in `assets/src/`). When publishing as an Artifact, pass it in `files`.

- Each crust and coastline polygon is triangulated once in present-day lon/lat (earcut via `THREE.ShapeUtils`, with a 4 degree grid of Steiner points), split until no edge is longer than 2 degrees so chords don't sag under the ocean sphere, and textured with today's imagery by its present-day lon/lat. Polygons that wind round a pole are closed along that pole.
- Features are merged per (kind, plate, begin, end), about 1,150 meshes. Each mesh's quaternion is the plate rotation, so the GPU does the reconstruction.
- Crust sits at r=1.004 and land at r=1.0048 to avoid z-fighting. The ocean sphere takes its colour from the imagery's own deep Pacific.
- The camera brings the continents back into view when time carries them away, but not within 4 s of you steering it. Tapping a city label follows that city.
- Every visit opens at 600 Ma. `#ma240` still opens at that age, but the page no longer rewrites the address.
- Default cities on: London, New York, Sydney, Tokyo, Istanbul. City search uses `places.json` (GeoNames cities15000, CC BY 4.0, built by `scripts/gazetteer.py`, fetched on first search). A searched place gets its plate from the smallest present-day static polygon containing it, else a coastline polygon, else the nearest coastline piece within 1.5 degrees. This matches pyGPlates' PlatePartitioner for all eight built-in cities. Added cities and on/off choices persist per viewer in localStorage.
- Layout (16 Oct 2026): the time dock is one slim row (Play, back to 600 Ma, ruler, speed, Cities), and two rows under 760 px. All sources and caveats live in the i sheet ("Sources and limits"); there is no credit line in the dock any more, by the owner's choice. The camera uses `setViewOffset` to centre the planet in the space between the dock (and the card on phones), and `fitDist()` picks the distance that shows the whole planet with its atmosphere. Loading shows an opaque planet-sized veil with a breathing highlight instead of a spinner.
- Mobile: touch targets are 44 px (`pointer: coarse`). Under 640 px the Cities panel is a bottom sheet with a Done button, kept above the on-screen keyboard via `visualViewport`. The search field is 16 px so iOS does not zoom. Landscape phones (height 520 px or less) keep only the age row in the card and a one-row dock. Pixel ratio is capped at 1.75 on touch devices. The panel lives outside the dock because the dock's `backdrop-filter` would trap a fixed-position child.
- Visual checks: the browser pane hangs on this WebGL page while hidden. Use Playwright with the cached headless shell and capture via CDP `Page.captureScreenshot` (`page.screenshot` waits on web fonts that never settle headless).
- Render on demand: the frame loop still runs, but it only draws (WebGL, labels, ruler) when the age, the camera, a city, the ruler press or the window size changed. Anything else that changes the picture must call `invalidate()`. Idle cost went from 60 draws a second to none.
- Labels: widths are measured once per (city, latitude-text length) and DOM styles are written only when they change. The de-overlap test uses 22 px against a 24 px step on purpose: an exact 24 px test looped forever on floating-point rounding and froze the tab (fixed 16 Oct 2026).
- Stress test (16 Oct 2026, Chrome on an M4, CPU throttled for phones), after the loading work: globe ready in 1.0 s desktop (was 2.3), 1.7 s at 4x CPU on fast 4G (was 3.8), 6.5 s at 6x CPU on slow 4G (was 15.4); 1.1 MB transferred before the globe is ready (was 2.6 MB); 60 fps for play, scrub, drag, zoom and resizing; nothing drawn while idle; heap steady at about 16 MB over repeated plays; 60 cities at 58 fps.
- City tracking and leader lines (16 Oct 2026): switching a city on in the list, tapping its pin (within 18 px, 28 px on touch, and only a tap, not a drag) or tapping its label follows it, including through Play. Each label sits 16 px right and 32 px above its pin and is joined to it by an SVG hairline (`#leaders`) with a 14 px invisible hit stroke; pointing at a label or line lights up both, and the followed city's line and label turn coral. Labels that would run off the right edge flip to the left of the pin.
- Cities before their crust exists (16 Oct 2026): each city gets `born`, the latest begin age of the same-plate polygons that contain it today (`cityBorn`). Older than that, the model has no crust under it (Rio's Ribeira belt starts at 520 Ma, Cape Town 500, Sydney 450, Istanbul 319, Tokyo 250), so the pin becomes a hollow ring with a dashed leader and the label reads "from 520 Ma". Don't snap such pins to other land; the gap is real in the model.
- Loading (16 Oct 2026): the globe no longer inlines the model. `scripts/build.py` writes a compact `model.json` (v2: quaternion rows as second differences along time, rings as vertex deltas; lossless, about 400 KB gzipped instead of 570 KB) and the page head preloads it, three.js and `earth-2k.jpg` in parallel. Every device starts on the 2K image (300 KB); `earth-4k.jpg` replaces it in the background only when the planet is more than 1000 device pixels across, Save-Data is off, the network is not 2G/3G, and the 2K image actually arrived at 3 Mbps or more.
- Following state lives in a row at the foot of the info card (it used to be a pill at the top centre, which covered the north-pole tag).
- N and S tags with a short axis stub and ring mark the spin axis, which is fixed in the palaeomagnetic frame.
- Hairline seams between neighbouring plates come from the 0.12 degree polygon simplification. They show in the 2D page too.

## Known limitations (state them honestly in the UI)

- The map shows where today's continental pieces were. It is not a palaeogeography map. The museum screen (likely Scotese PALEOMAP-style imagery) shows ancient shorelines, seas and mountains, and we don't model those.
- Before about 250 Ma, palaeomagnetism constrains latitude only, so longitudes are model choices.
- Pacific absolute positions between 250 and 83 Ma are adjusted (see the model README). Don't use this for Pacific hotspot kinematics.

## Backlog (ranked)

1. **Plate boundaries layer:** ridges, trenches and transforms from the Merdith topology files (`250-0_plate_boundaries`, `410-250_...`, `1000_410-*`). Use `pygplates.resolve_topologies` per 5 Myr step, export boundary sections (they change shape, so they can't be rotated like static polygons), and draw subduction zones with teeth.
2. **Palaeogeography mode closer to the exhibit:** a toggle that drapes open palaeo-DEM rasters, e.g. Scotese & Wright 2018 PALEOMAP PaleoDEMs (check the licence, CC BY 4.0 on Zenodo as far as we know) or Cao et al. 2017 palaeogeography polygons (EarthByte). Ship them as per-step WebP tiles and fetch lazily, so they must sit next to the page, not inlined.
3. ~~Orthographic globe toggle~~ Done in v2.
4. ~~"Find any place" box~~ Done in the globe (GeoNames search, plate lookup in the browser).
5. ~~Deep links~~ Done in v2 (`#ma240`, `#globe-ma240`).
6. ~~Static site deploy~~ Done: GitHub Pages serves `docs/` from `main` at https://asturksever.github.io/deep-time-atlas/ (repo github.com/asturksever/deep-time-atlas). Run `make page` and commit `docs/` to update it.

## Gotchas from the first build

- `pygplates` 1.0.0 is on PyPI. Ring points: use `[p.to_lat_lon() for p in g.get_exterior_ring_points()]`. The view object has no `to_lat_lon_list`.
- `Rotation` has no quaternion getter. Build it from `get_lat_lon_euler_pole_and_angle_degrees()` (see `reconstruct.py`).
- Polygons crossing the dateline need longitude unwrapping before shapely simplification, then re-wrapping.
- The published artifact runs under a CSP: scripts only from cdnjs, jsDelivr, unpkg; no fetch to other hosts; no iframes. Keep d3 pinned at `7.9.0` on cdnjs. For local screenshots in a sandbox that blocks cdnjs, `npm pack d3@7.9.0` and set `D3_LOCAL`.
- Republishing an existing Claude artifact: from a new conversation, pass its URL as `url` and read the artifact first, or the publish will create a new one.

## Definition of done for any change

1. `make all` runs clean.
2. `make shots`: check 600, 240, 90 and 0 Ma on desktop plus 240 Ma on phone. Look for no page errors, scrollWidth equal to the viewport width, continents in sensible places (Pangaea around 250 Ma, open South Atlantic by 90 Ma), and pins inside their continents.
3. The full attribution is still present (the 2D page's footer, the globe's Sources and limits sheet).
4. No em dashes anywhere (`grep -rn "—" src scripts` should return nothing).
