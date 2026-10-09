import sys
sys.path.insert(0, "scripts")
from build_spots import build, slug

SEED = {"spots": [{"id": "minto", "name": "Minto", "lat": 28.6330, "lon": 77.2200, "known_flood_spot": True, "pocket_depth_m": None}]}
OSM = {"elements": [
    {"id": 1, "center": {"lat": 28.6335, "lon": 77.2204}, "tags": {"name": "Minto Road Underpass"}},
    {"id": 2, "center": {"lat": 28.70, "lon": 77.10}, "tags": {"name": "Rohini Underpass"}},
    {"id": 3, "center": {"lat": 28.71, "lon": 77.11}, "tags": {}},
]}

def test_seed_snaps_to_nearby_osm_way_and_gets_depth():
    out = build(SEED, OSM, {"spots": [{"id": "minto", "pocket_depth_m": 1.4}]})
    m = out[0]
    assert m["osm_way"] == 1 and m["lat"] == 28.6335 and m["pocket_depth_m"] == 1.4 and m["known_flood_spot"]

def test_extra_named_ways_added_unnamed_skipped_and_limit_respected():
    out = build(SEED, OSM)
    assert [s["id"] for s in out] == ["minto", "rohini-underpass"]
    assert len(build(SEED, OSM, limit=1)) == 1

def test_slug():
    assert slug("Pul Prahladpur  Underpass!") == "pul-prahladpur-underpass"
