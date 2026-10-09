import pytest
from nikasi.agents import sentinel, verifier, alerter, dispatcher, graph

def it(state, act=None, eta=None, name="X underpass", hold=0):
    return {"spot_id": "x", "name": name, "state": state, "act_as": act or ("NO-GO" if state == "UNKNOWN" else state),
            "reasons": ["load 41.0 mm"], "minutes_to_no_go": eta, "hold": hold}

def test_sentinel_flags_escalation_and_first_run():
    assert sentinel.transition(None, it("GO"))["first"]
    t = sentinel.transition(it("GO"), it("NO-GO"))
    assert t["changed"] and t["escalated"]

def test_worse_passes_immediately():
    assert verifier.verify(it("GO"), it("NO-GO"))["state"] == "NO-GO"

def test_better_is_held_one_cycle_then_accepted():
    held = verifier.verify(it("NO-GO"), it("GO"))
    assert held["state"] == "NO-GO" and held["act_as"] == "NO-GO" and held["hold"] == 1
    assert verifier.verify(held, it("GO"))["state"] == "GO"

def test_unknown_recovers_without_hold():
    assert verifier.verify(it("UNKNOWN"), it("GO"))["state"] == "GO"

def test_template_used_without_model():
    text, src = alerter.write_alert(it("NO-GO"))
    assert src == "template" and text.startswith("NO-GO")

def test_model_text_accepted_when_it_keeps_verdict_and_numbers():
    ok = lambda p: "NO-GO: X underpass. Water likely, 41.0 mm already counted. Take another road."
    base = "NO-GO: X underpass. Water is likely. Take another route. [load 41.0 mm]"
    assert alerter.accept(ok(""), base)

@pytest.mark.parametrize("bad", [
    "Looks fine now, X underpass",                       # wrong verdict word
    "NO-GO: X underpass, 99 mm of rain",                # invented number
    "NO-GO: X underpass but the other side is safe",    # safety claim
    "NO-GO: " + "x" * 300,                              # too long
])
def test_model_text_rejected(bad):
    base = "NO-GO: X underpass. Water is likely. [load 41.0 mm]"
    assert not alerter.accept(bad, base)

def test_bad_model_falls_back_to_template():
    text, src = alerter.write_alert(it("NO-GO"), llm=lambda p: "all clear, 5 mm")
    assert src == "template"

def test_model_never_asked_about_unknown():
    called = []
    text, src = alerter.write_alert(it("UNKNOWN"), llm=lambda p: called.append(p) or "x")
    assert not called and src == "template"

def test_model_exception_falls_back():
    def boom(p): raise RuntimeError("bedrock down")
    assert alerter.write_alert(it("NO-GO"), llm=boom)[1] == "template"

def test_dispatch_needs_named_approval():
    d = dispatcher.build([it("NO-GO", name="A"), it("GO", name="B"), it("UNKNOWN", name="C")])
    assert d["status"] == "PENDING_APPROVAL" and not dispatcher.sendable(d)
    assert "A" in d["text"] and "B" not in d["text"] and "no fresh data" in d["text"]
    with pytest.raises(ValueError):
        dispatcher.approve(d, "  ", "t")
    assert dispatcher.sendable(dispatcher.approve(d, "Ward officer R. Singh", "2026-10-09T12:00:00Z"))

def test_graph_alerts_only_on_action_change():
    r = graph.process(it("GO"), it("NO-GO"))
    assert r["alert"] and r["alert"]["source"] == "template"
    assert graph.process(it("NO-GO"), it("NO-GO"))["alert"] is None
