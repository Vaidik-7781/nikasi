"""Lambda entry point, triggered by EventBridge every 15 minutes.
Writes one state item per spot to DynamoDB (TTL keeps stale rows from lingering)."""
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone
from .risk import Spot, assess
from . import weather

def _spots() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "spots.json")
    return json.load(open(path))["spots"]

def lambda_handler(event, context, table=None, fetch=weather.fetch):
    if table is None:
        import boto3
        table = boto3.resource("dynamodb").Table(os.environ["STATE_TABLE"])
    now = datetime.now(timezone.utc)
    out = []
    for s in _spots():
        spot = Spot(s["id"], s["name"], s.get("pocket_depth_m"), s.get("known_flood_spot", False))
        a = assess(spot, fetch(s["lat"], s["lon"], now), now)
        item = {"spot_id": spot.id, "name": spot.name, "state": a.state, "act_as": a.act_as,
                "reasons": a.reasons, "minutes_to_no_go": a.minutes_to_no_go,
                "updated_at": now.isoformat(), "ttl": int(time.time()) + 3600}
        table.put_item(Item=json.loads(json.dumps(item), parse_float=str))
        out.append(item)
    return {"count": len(out)}
