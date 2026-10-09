from __future__ import annotations
from . import sentinel, verifier, alerter

def process(prev: dict | None, item: dict, llm=None) -> dict:
    """One spot, one cycle. Returns the item to store plus an alert when the action changed."""
    t = sentinel.transition(prev, item)
    final = verifier.verify(prev, item)
    alert = None
    if prev and prev.get("act_as") != final["act_as"]:
        text, source = alerter.write_alert(final, llm)
        alert = {"text": text, "source": source}
    return {"item": final, "alert": alert, "transition": t}
