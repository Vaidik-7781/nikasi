"""Fixed alert templates. The model is never on the critical path: these render
straight from a state item, and every number comes from that item."""
from __future__ import annotations

def render(item: dict) -> str:
    name, act = item["name"], item["act_as"]
    eta = item.get("minutes_to_no_go")
    why = "; ".join(item.get("reasons", [])) or "no detail"
    if item["state"] == "UNKNOWN":
        return f"NO-GO (no fresh data): {name}. Treat as closed until data returns. [{why}]"
    if act == "NO-GO":
        return f"NO-GO: {name}. Water is likely. Take another route. [{why}]"
    if act == "CAUTION":
        tail = f" Expected NO-GO in about {eta} min." if eta else ""
        return f"CAUTION: {name}. Rain is building.{tail} [{why}]"
    tail = f" Could turn NO-GO in about {eta} min." if eta else ""
    return f"GO: {name} looks clear right now.{tail}"
