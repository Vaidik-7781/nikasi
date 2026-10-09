from datetime import datetime, timedelta
from nikasi.risk import assess, Spot, Weather, GO, CAUTION, NO_GO, UNKNOWN

NOW = datetime(2026, 10, 9, 12, 0)
SPOT = Spot("t", "Test underpass", pocket_depth_m=1.0, known_flood_spot=True)  # s = 3.0

def wx(past=0.0, steps=(0.0,) * 4, age_min=5):
    return Weather(NOW - timedelta(minutes=age_min), past, list(steps))

def test_dry_is_go():
    assert assess(SPOT, wx(), NOW).state == GO

def test_missing_weather_is_unknown_and_acts_as_no_go():
    a = assess(SPOT, None, NOW)
    assert a.state == UNKNOWN and a.act_as == NO_GO

def test_stale_weather_is_unknown():
    a = assess(SPOT, wx(age_min=60), NOW)
    assert a.state == UNKNOWN and a.act_as == NO_GO

def test_future_timestamp_is_unknown():
    assert assess(SPOT, wx(age_min=-30), NOW).state == UNKNOWN

def test_heavy_rain_now_is_no_go():
    assert assess(SPOT, wx(steps=(20.0, 0, 0, 0)), NOW).state == NO_GO

def test_eta_to_no_go_counts_forecast_steps():
    a = assess(SPOT, wx(steps=(1.0, 3.0, 5.0, 8.0)), NOW)  # no-go at 40/3=13.3 mm; crosses on step 4
    assert a.state != NO_GO and a.minutes_to_no_go == 60

def test_deeper_pocket_trips_earlier():
    shallow = Spot("s", "s", pocket_depth_m=0.0, is_underpass=False)
    deep = Spot("d", "d", pocket_depth_m=2.5, is_underpass=False)
    w = wx(steps=(15.0, 0, 0, 0))
    assert assess(shallow, w, NOW).state == GO
    assert assess(deep, w, NOW).state in (CAUTION, NO_GO)
