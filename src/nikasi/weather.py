"""Open-Meteo fetch (CC BY 4.0, keyless). Returns None on any failure so the
risk engine fails safe to UNKNOWN."""
from __future__ import annotations
import json, urllib.request
from datetime import datetime, timezone
from .risk import Weather

URL = ("https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}"
       "&minutely_15=precipitation&hourly=precipitation&past_days=1&forecast_days=1"
       "&timezone=UTC")

def fetch(lat: float, lon: float, now: datetime, timeout: float = 8.0) -> Weather | None:
    try:
        with urllib.request.urlopen(URL.format(lat=lat, lon=lon), timeout=timeout) as r:
            d = json.load(r)
        m15 = d["minutely_15"]
        times = [datetime.fromisoformat(t).replace(tzinfo=timezone.utc) for t in m15["time"]]
        vals = [v or 0.0 for v in m15["precipitation"]]
        now_u = now.astimezone(timezone.utc)
        idx = max(i for i, t in enumerate(times) if t <= now_u)
        past = sum(vals[max(0, idx - 96):idx])  # 96 x 15 min = 24 h
        return Weather(now_u, round(past, 2), vals[idx:idx + 8])
    except Exception:
        return None
