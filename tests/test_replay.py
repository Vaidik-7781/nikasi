from nikasi import replay

def frames():
    return replay.run(replay.scripted_model())

def test_every_spot_is_never_green_without_fresh_data():
    for f in frames():
        for s in f["spots"]:
            if f["outage"]:
                assert s["state"] == "UNKNOWN" and s["act_as"] == "NO-GO"

def test_storm_escalates_in_order_and_alerts_on_change():
    fr = frames()
    minto = [f["spots"][0]["act_as"] for f in fr]
    assert minto[0] == "GO" and "CAUTION" in minto and "NO-GO" in minto
    assert minto.index("CAUTION") < minto.index("NO-GO")
    assert any(f["alerts"] for f in fr)

def test_bad_model_text_is_dropped_but_alert_still_sent():
    alerts = [a for f in frames() for a in f["alerts"]]
    assert {a["source"] for a in alerts} == {"model", "template"}
    assert not any("safe" in a["text"].lower() for a in alerts)

def test_unknown_alert_is_never_model_written():
    alerts = [a for f in frames() if f["outage"] for a in f["alerts"]]
    assert alerts and all(a["source"] == "template" and a["text"].startswith("NO-GO (no fresh data)") for a in alerts)

def test_timeline_renders_and_says_synthetic():
    out = replay.timeline(frames())
    assert out.startswith("SYNTHETIC STORM") and "weather feed down" in out
