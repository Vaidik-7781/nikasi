"""Build src/nikasi/spots.json from three inputs you produce by running the other scripts
on a machine with internet:
  data/osm_underpasses.json    (scripts/osm_underpasses.py)
  data/spots.pockets.json      (scripts/dem_pockets.py, optional)
  data/spots.seed.json         (hand-curated known flood spots)
Seeds always stay. An OSM way within 300 m of a seed replaces the seed's rough coordinates.
Other named OSM ways fill the list up to MAX. Usage: python scripts/build_spots.py"""
from __future__ import annotations
import json, re, sys
sys.path.insert(0, "src")
from nikasi.geo import haversine_km

MAX = 15

def slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def osm_points(osm: dict) -> list[dict]:
    pts = []
    for e in osm.get("elements", []):
        c, name = e.get("center"), (e.get("tags") or {}).get("name")
        if c and name:
            pts.append({"name": name, "lat": c["lat"], "lon": c["lon"], "osm_way": e.get("id")})
    return pts

def build(seed: dict, osm: dict, pockets: dict | None = None, limit: int = MAX) -> list[dict]:
    pts, depth = osm_points(osm), {s["id"]: s.get("pocket_depth_m") for s in (pockets or {}).get("spots", [])}
    out, used = [], set()
    for s in seed["spots"]:
        s = dict(s)
        near = min(pts, key=lambda p: haversine_km(s["lat"], s["lon"], p["lat"], p["lon"]), default=None)
        if near and haversine_km(s["lat"], s["lon"], near["lat"], near["lon"]) <= 0.3:
            s.update(lat=near["lat"], lon=near["lon"], osm_way=near["osm_way"]); used.add(near["osm_way"])
        if depth.get(s["id"]) is not None:
            s["pocket_depth_m"] = depth[s["id"]]
        out.append(s)
    for p in sorted(pts, key=lambda p: p["name"]):
        if len(out) >= limit: break
        sid = slug(p["name"])
        if p["osm_way"] in used or any(o["id"] == sid for o in out): continue
        out.append({"id": sid, "name": p["name"], "lat": p["lat"], "lon": p["lon"], "known_flood_spot": False,
                    "pocket_depth_m": depth.get(sid), "osm_way": p["osm_way"]})
    return out

if __name__ == "__main__":
    load = lambda p: json.load(open(p))
    try: pockets = load("data/spots.pockets.json")
    except FileNotFoundError: pockets = None
    spots = build(load("data/spots.seed.json"), load("data/osm_underpasses.json"), pockets)
    json.dump({"city": "Delhi", "spots": spots}, open("src/nikasi/spots.json", "w"), indent=2)
    print(f"wrote {len(spots)} spots; review them on a map before the demo")
