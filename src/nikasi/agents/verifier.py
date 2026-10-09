"""Damps flapping without ever delaying a warning: getting worse is accepted at once,
getting better must hold for two consecutive 15-minute readings."""
from .sentinel import SEVERITY

def verify(prev: dict | None, new: dict) -> dict:
    out = dict(new)
    out["hold"] = 0
    if not prev:
        return out
    a, b = prev.get("state"), new["state"]
    if a in ("GO", "CAUTION", "NO-GO") and SEVERITY[b] < SEVERITY[a] and int(prev.get("hold", 0) or 0) < 1:
        out.update(state=a, act_as=prev.get("act_as", a), hold=1,
                   minutes_to_no_go=prev.get("minutes_to_no_go"),
                   reasons=list(new.get("reasons", [])) + [f"holding {a}: improvement must last 15 more min"])
    return out
