"""Storm replay: push a SCRIPTED (synthetic) storm through the real pipeline.

This is NOT a recorded flood and proves nothing about accuracy (scripts/backtest.py is
for that). It shows behaviour: the risk engine, Verifier hold, guarded Alerter and the
fail-safe UNKNOWN path, using the same code the Lambda runs, one 15-minute step at a time.

    python -m nikasi.replay          # readable timeline
    python -m nikasi.replay --json   # frames for the local demo server
"""
from __future__ import annotations
import json, os, sys
from datetime import datetime, timedelta, timezone
from .risk import Spot, Weather, assess
from .agents import graph

# mm of rain per 15-minute step. Synthetic: dry, building, a cloudburst, easing, dry.
RAIN = [0, 0, 0, 0, 1, 2, 3, 5, 6, 7, 6, 5, 4, 3, 2, 1, 0.5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
BASELINE_24H = 2.0                 # mm that fell before the scenario starts
# Demo-only terrain so the three spots behave differently (real depths come from scripts/dem_pockets.py).
DEMO_POCKET_M = {"minto-bridge": 2.0, "pul-prahladpur": 1.0, "zakhira": 0.3}
OUTAGE = range(12, 15)             # steps where the weather feed is down
START = datetime(2026, 7, 15, 4, 0, tzinfo=timezone.utc)   # fictional date
STEP = timedelta(minutes=15)

def load_spots() -> list[dict]:
    path = os.path.join(os.path.dirname(__file__), "spots.json")
    return json.load(open(path))["spots"]

def scripted_model(misbehave_every: int = 3):
    """A stand-in for a language model. Every Nth call it tries to say something unsafe,
    so the demo shows the Alerter dropping it and sending the fixed template instead."""
    calls = {"n": 0}
    def call(prompt: str) -> str:
        calls["n"] += 1
        base = prompt.split("\n", 1)[1]
        if calls["n"] % misbehave_every == 0:
            return "Definitely safe to drive through, nothing to worry about."
        return base
    return call

def run(llm=None) -> list[dict]:
    """Return one frame per step: {step, time, rain_mm, outage, spots:[item], alerts:[...]}."""
    spots = load_spots()
    prev: dict[str, dict] = {}
    frames = []
    for i, rain in enumerate(RAIN):
        now = START + i * STEP
        outage = i in OUTAGE
        wx = None if outage else Weather(now, BASELINE_24H + sum(RAIN[:i]), [float(x) for x in RAIN[i:i + 8]])
        items, alerts = [], []
        for s in spots:
            sp = Spot(s["id"], s["name"], s.get("pocket_depth_m") if s.get("pocket_depth_m") is not None else DEMO_POCKET_M.get(s["id"]), s.get("known_flood_spot", False))
            a = assess(sp, wx, now)
            item = {"spot_id": sp.id, "name": sp.name, "lat": s["lat"], "lon": s["lon"], "state": a.state,
                    "act_as": a.act_as, "reasons": a.reasons, "minutes_to_no_go": a.minutes_to_no_go,
                    "updated_at": now.isoformat()}
            res = graph.process(prev.get(sp.id), item, llm)
            prev[sp.id] = res["item"]
            items.append(res["item"])
            if res["alert"]:
                alerts.append({"spot_id": sp.id, **res["alert"]})
        frames.append({"step": i, "time": now.isoformat(), "rain_mm": rain, "outage": outage,
                       "spots": items, "alerts": alerts})
    return frames

def timeline(frames: list[dict]) -> str:
    names = [s["name"].replace(" underpass", "") for s in frames[0]["spots"]]
    head = f"{'time':5} {'rain':>5}  " + "  ".join(f"{n[:16]:16}" for n in names)
    out = ["SYNTHETIC STORM (not a real event). Same code path as the Lambda.", head, "-" * len(head)]
    for f in frames:
        cells = []
        for s in f["spots"]:
            eta = s.get("minutes_to_no_go")
            tag = s["act_as"] + (f" ~{eta}m" if eta else "") + ("*" if s["state"] == "UNKNOWN" else "") + ("^" if s.get("hold") else "")
            cells.append(f"{tag:16}")
        row = f"{f['time'][11:16]:5} {f['rain_mm']:>5}  " + "  ".join(cells)
        if f["outage"]:
            row += "   <- weather feed down"
        out.append(row)
        for a in f["alerts"]:
            out.append(f"      ALERT [{a['source']}] {a['text']}")
    out.append("* = UNKNOWN (no fresh data, acts as NO-GO)   ^ = improvement held for one more reading")
    return "\n".join(out)

def main(argv: list[str]) -> int:
    frames = run(scripted_model())
    print(json.dumps(frames) if "--json" in argv else timeline(frames))
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
