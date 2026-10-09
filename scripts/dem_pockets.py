"""Depth of the low pocket at each spot, from Copernicus DEM GLO-30 (public S3, no creds).
UNTESTED SCAFFOLD: run it, eyeball results against the real site, fix what breaks.
Usage: python scripts/dem_pockets.py data/spots.seed.json > data/spots.pockets.json
Method: depth = median elevation of a 150 m ring minus the minimum within 30 m.
DEM accuracy over built-up Delhi is coarse (30 m); treat the depth as a ranking signal, not metres.
"""
import json, math, sys
import numpy as np, rasterio

BUCKET = "https://copernicus-dem-30m.s3.amazonaws.com"

def tile_url(lat, lon):
    la, lo = math.floor(lat), math.floor(lon)
    ns, ew = ("N" if la >= 0 else "S"), ("E" if lo >= 0 else "W")
    name = f"Copernicus_DSM_COG_10_{ns}{abs(la):02d}_00_{ew}{abs(lo):03d}_00_DEM"
    return f"{BUCKET}/{name}/{name}.tif"

def pocket_depth(lat, lon):
    with rasterio.open(tile_url(lat, lon)) as ds:
        r, c = ds.index(lon, lat)
        k = 6  # ~180 m at 30 m
        win = ds.read(1, window=((r - k, r + k + 1), (c - k, c + k + 1))).astype(float)
    yy, xx = np.mgrid[-k:k + 1, -k:k + 1]
    dist = np.hypot(yy, xx) * 30
    ring = win[(dist >= 120) & (dist <= 180)]
    core = win[dist <= 30]
    return round(float(np.median(ring) - core.min()), 2)

if __name__ == "__main__":
    data = json.load(open(sys.argv[1]))
    for s in data["spots"]:
        s["pocket_depth_m"] = pocket_depth(s["lat"], s["lon"])
    json.dump(data, sys.stdout, indent=2)
