from math import radians, sin, cos, asin, sqrt

def haversine_km(a_lat, a_lon, b_lat, b_lon):
    p = radians(b_lat - a_lat); q = radians(b_lon - a_lon)
    h = sin(p / 2) ** 2 + cos(radians(a_lat)) * cos(radians(b_lat)) * sin(q / 2) ** 2
    return 2 * 6371 * asin(sqrt(h))

def nearest(lat, lon, spots, n=3):
    return sorted(spots, key=lambda s: haversine_km(lat, lon, s["lat"], s["lon"]))[:n]
