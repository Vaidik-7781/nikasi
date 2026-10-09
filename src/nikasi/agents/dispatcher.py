"""Ward dispatch list. It is only a proposal: nothing is sendable until a named person
approves it (the human-in-the-loop step)."""
from __future__ import annotations

def build(items: list[dict]) -> dict:
    bad = [i for i in items if i.get("act_as") == "NO-GO"]
    bad.sort(key=lambda i: (i.get("state") != "NO-GO", i["name"]))   # confirmed NO-GO before UNKNOWN
    lines = [f'{n}. {i["name"]} ({"no fresh data" if i["state"] == "UNKNOWN" else "NO-GO"})' for n, i in enumerate(bad, 1)]
    return {"status": "PENDING_APPROVAL", "spots": [i["spot_id"] for i in bad],
            "text": "Underpasses to barricade or check:\n" + "\n".join(lines) if lines else "", "approved_by": None}

def approve(d: dict, approver: str, now_iso: str) -> dict:
    if not approver or not approver.strip():
        raise ValueError("an approver name is required")
    return {**d, "status": "APPROVED", "approved_by": approver.strip(), "approved_at": now_iso}

def sendable(d: dict) -> bool:
    return d.get("status") == "APPROVED" and bool(d.get("approved_by")) and bool(d.get("spots"))
