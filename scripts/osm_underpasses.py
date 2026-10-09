"""List underpass/tunnel ways in a city from OpenStreetMap via Overpass (ODbL).
UNTESTED SCAFFOLD. Usage: python scripts/osm_underpasses.py > data/osm_underpasses.json
Credit OpenStreetMap contributors in the app footer (ODbL)."""
import json, sys, urllib.parse, urllib.request
Q = """[out:json][timeout:60];
area["name"="Delhi"]["admin_level"="4"]->.a;
(way(area.a)["highway"]["tunnel"~"yes|building_passage"]["layer"~"^-"];
 way(area.a)["highway"]["tunnel"="yes"]["name"~"[Uu]nderpass|[Ss]ubway"];);
out center tags;"""
req = urllib.request.Request("https://overpass-api.de/api/interpreter",
                             data=urllib.parse.urlencode({"data": Q}).encode())
json.dump(json.load(urllib.request.urlopen(req, timeout=90)), sys.stdout)
