import json, sys
from datetime import datetime, timedelta
sys.path.insert(0, "scripts")
from nikasi.templates import render
from nikasi.api import lambda_handler as api
import backtest

def item(state, act, eta=None):
    return {"name": "X underpass", "state": state, "act_as": act, "reasons": ["r"], "minutes_to_no_go": eta}

def test_templates_cover_every_state():
    assert render(item("UNKNOWN", "NO-GO")).startswith("NO-GO (no fresh data)")
    assert render(item("NO-GO", "NO-GO")).startswith("NO-GO:")
    assert "30 min" in render(item("CAUTION", "CAUTION", 30))
    assert render(item("GO", "GO")).startswith("GO:")

class T:
    def get_item(self, Key): return {}
    def scan(self): return {"Items": [{"spot_id": "a"}]}

def test_api_missing_spot_fails_safe():
    r = api({"pathParameters": {"id": "nope"}}, None, table=T())
    assert r["statusCode"] == 404 and json.loads(r["body"])["act_as"] == "NO-GO"

def test_api_lists_spots():
    assert json.loads(api({}, None, table=T())["body"])["spots"][0]["spot_id"] == "a"

def test_backtest_metrics_on_synthetic_day():
    start = datetime(2024, 6, 27)
    times = [start + timedelta(hours=h) for h in range(72)]
    vals = [0.0] * 72
    for h in (36, 37, 38):  # heavy rain mid-day 28th
        vals[h] = 25.0
    cfg = {"id": "s", "name": "s", "pocket_depth_m": 1.0, "known_flood_spot": True}
    ev = [{"spot_id": "s", "flooded_from": "2024-06-28T13:00", "flooded_to": "2024-06-28T16:00"}]
    out = backtest.run(cfg, ev, "2024-06-28", (times, vals))
    assert out["recall"] == 1.0 and out["lead_minutes_first_warning_vs_reported_start"][0] > 0
