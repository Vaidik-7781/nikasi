"""Replay a real flood day through the risk engine.

Needs data/flood_events.json (YOU fill it from news/official reports - never invent):
  {"events": [{"spot_id": "minto-bridge", "flooded_from": "2024-06-28T03:00", "flooded_to": "2024-06-28T12:00", "source": "<url>"}]}
Usage: python scripts/backtest.py data/flood_events.json 2024-06-28
Resolution is hourly (Open-Meteo archive), each hour split into 4 equal 15-min steps.
Report the numbers as they come out. They are not tuned unless you tune them, and say so if you do.
"""
from __future__ import annotations
import json, sys, urllib.request
from datetime import datetime, timedelta, timezone
sys.path.insert(0, "src")
from nikasi.risk import Spot, Weather, assess, NO_GO

ARCHIVE = ("https://archive-api.open-meteo.com/v1/archive?latitude={lat}&longitude={lon}"
           "&start_date={a}&end_date={b}&hourly=precipitation&timezone=UTC")

def fetch_hourly(lat, lon, day: str):
    d = datetime.fromisoformat(day)
    a, b = (d - timedelta(days=1)).date(), (d + timedelta(days=1)).date()
    with urllib.request.urlopen(ARCHIVE.format(lat=lat, lon=lon, a=a, b=b), timeout=30) as r:
        j = json.load(r)["hourly"]
    return [datetime.fromisoformat(t) for t in j["time"]], [v or 0.0 for v in j["precipitation"]]

def run(spot_cfg, events, day, hourly):
    times, vals = hourly
    spot = Spot(spot_cfg["id"], spot_cfg["name"], spot_cfg.get("pocket_depth_m"), spot_cfg.get("known_flood_spot", False))
    mine = [e for e in events if e["spot_id"] == spot.id]
    d0 = datetime.fromisoformat(day)
    rows = []
    for i, t in enumerate(times):
        if not (d0 <= t < d0 + timedelta(days=1)) or i < 24:
            continue
        past = sum(vals[i - 24:i])
        steps = [v / 4 for v in vals[i:i + 2] for _ in range(4)]
        now = t.replace(tzinfo=timezone.utc)
        a = assess(spot, Weather(now, past, steps), now)
        truth = any(datetime.fromisoformat(e["flooded_from"]) <= t < datetime.fromisoformat(e["flooded_to"]) for e in mine)
        rows.append((t, a.state == NO_GO, truth, a.state == NO_GO or a.minutes_to_no_go is not None))
    tp = sum(p and y for _, p, y, _w in rows); fp = sum(p and not y for _, p, y, _w in rows); fn = sum(y and not p for _, p, y, _w in rows)
    lead = []
    for e in mine:
        start = datetime.fromisoformat(e["flooded_from"])
        end = datetime.fromisoformat(e["flooded_to"])
        # a warning = NO-GO now, or a NO-GO countdown running; look back 6 h before reported start
        first = next((t for t, _p, _y, w in rows if w and start - timedelta(hours=6) <= t < end), None)
        if first: lead.append((start - first).total_seconds() / 60)
    return {"spot": spot.id, "hours": len(rows), "tp": tp, "fp": fp, "fn": fn,
            "precision": tp / (tp + fp) if tp + fp else None,
            "recall": tp / (tp + fn) if tp + fn else None,
            "lead_minutes_first_warning_vs_reported_start": lead}

if __name__ == "__main__":
    events = json.load(open(sys.argv[1]))["events"]
    spots = json.load(open("data/spots.seed.json"))["spots"]
    for s in spots:
        print(json.dumps(run(s, events, sys.argv[2], fetch_hourly(s["lat"], s["lon"], sys.argv[2]))))
