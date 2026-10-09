SEVERITY = {"GO": 0, "CAUTION": 1, "NO-GO": 2, "UNKNOWN": 3}

def transition(prev: dict | None, new: dict) -> dict:
    """Describe what changed since the last cycle. Pure, no side effects."""
    if not prev:
        return {"changed": False, "first": True, "escalated": False, "from": None, "to": new["state"]}
    a, b = prev.get("state"), new["state"]
    return {"changed": a != b, "first": False, "escalated": SEVERITY.get(b, 3) > SEVERITY.get(a, 3),
            "from": a, "to": b}
