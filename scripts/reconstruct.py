"""Export the Merdith et al. (2021) plate model to a compact JSON for the browser.

Usage: python3 scripts/reconstruct.py data/MERDITH2021 build/model.json

Output schema (model.json):
  times  : [0, 5, ..., 600]            Ma, 5 Myr step
  pids   : [plate ids]                 sorted
  q      : [[w,x,y,z]*len(times)]      per plate, unit quaternion x 1e7 (ints), rotation present -> t
  f      : [{k:'c'|'l', p:plateId, b:beginMa, e:endMa, r:[lon*100, lat*100, ...]}]
           k=c continental crust (static polygons minus Basin), k=l land (coastlines v2)
  cities : [{n:name, p:plateId, ll:[lon,lat]}]
"""
import json, math, sys
import numpy as np
import pygplates
from shapely.geometry import LineString

MODEL = sys.argv[1]
OUT = sys.argv[2]
rot = pygplates.RotationModel(f"{MODEL}/1000_0_rotfile_Merdith_et_al.rot")

TOL = 0.12          # degrees, Douglas-Peucker tolerance on present-day geometry
MIN_AREA = 2.5e-5   # steradians (~1000 km2) drop slivers


def simplify_ring(latlon):
    lats = np.array([p[0] for p in latlon]); lons = np.array([p[1] for p in latlon])
    lons_u = np.degrees(np.unwrap(np.radians(lons)))  # continuous longitudes
    coords = list(zip(lons_u, lats)) + [(lons_u[0], lats[0])]
    s = LineString(coords).simplify(TOL, preserve_topology=False)
    out = [((x + 180) % 360 - 180, y) for x, y in list(s.coords)[:-1]]
    return out if len(out) >= 3 else None


def load(path, keep):
    fc = pygplates.FeatureCollection(path)
    out = []
    for ft in fc:
        if not keep(ft):
            continue
        new_geoms = []
        for g in ft.get_geometries():
            if not isinstance(g, pygplates.PolygonOnSphere):
                continue
            if g.get_area() < MIN_AREA:
                continue
            r = simplify_ring([p.to_lat_lon() for p in g.get_exterior_ring_points()])
            if r:
                new_geoms.append(pygplates.PolygonOnSphere([(la, lo) for lo, la in r]))
        if new_geoms:
            ft = ft.clone(); ft.set_geometry(new_geoms)
            out.append(ft)
    return out

crust = load(f"{MODEL}/shapes_static_polygons_Merdith_et_al.gpmlz",
             lambda f: f.get_feature_type() != pygplates.FeatureType.gpml_basin)
land = load(f"{MODEL}/shapes_coastlines_Merdith_et_al_v2.gpmlz", lambda f: True)
print("features crust", len(crust), "land", len(land))


CITIES = {"London": (51.5, -0.13), "New York": (40.7, -74.0), "Rio": (-22.9, -43.2),
          "Cape Town": (-33.9, 18.4), "Mumbai": (19.1, 72.9), "Sydney": (-33.9, 151.2),
          "Tokyo": (35.7, 139.7), "Istanbul": (41.0, 29.0)}
static_all = pygplates.FeatureCollection(f"{MODEL}/shapes_static_polygons_Merdith_et_al.gpmlz")
partitioner = pygplates.PlatePartitioner(static_all, rot)
cities = []
for n, (la, lo) in CITIES.items():
    p = partitioner.partition_point(pygplates.PointOnSphere(la, lo))
    cities.append({"n": n, "p": p.get_feature().get_reconstruction_plate_id(), "ll": [lo, la]})

def tclip(x):
    return 99999 if x == float("inf") else (-99999 if x == float("-inf") else round(x, 2))

feats = []
for kind, fs in (("c", crust), ("l", land)):
    for ft in fs:
        b, e = ft.get_valid_time()
        if e > 600:      # gone before our window
            continue
        for g in ft.get_geometries():
            pts = g.get_exterior_ring_points()
            ring = []
            for q in pts:
                la, lo = q.to_lat_lon(); ring += [round(lo * 100), round(la * 100)]
            feats.append({"k": kind, "p": ft.get_reconstruction_plate_id(), "b": tclip(b), "e": tclip(e), "r": ring})

pids = sorted({f["p"] for f in feats} | {c["p"] for c in cities})
times = list(range(0, 605, 5))
Q = []
for pid in pids:
    row = []
    for t in times:
        R = rot.get_rotation(float(t), pid)
        lat, lon, ang = R.get_lat_lon_euler_pole_and_angle_degrees()
        a = np.radians(ang) / 2; la, lo = np.radians(lat), np.radians(lon)
        v = [np.cos(a), np.sin(a)*np.cos(la)*np.cos(lo), np.sin(a)*np.cos(la)*np.sin(lo), np.sin(a)*np.sin(la)]
        row += [round(x * 1e7) for x in v]
    Q.append(row)
print("features", len(feats), "plates", len(pids))
json.dump({"times": times, "pids": pids, "q": Q, "f": feats, "cities": cities}, open(OUT, "w"), separators=(",", ":"))
