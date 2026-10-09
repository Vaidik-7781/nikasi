"""Deterministic risk engine. No model, no network: the safety call lives here.

Fail-safe rule: stale or missing data -> UNKNOWN, and UNKNOWN is shown and
treated as NO-GO. Thresholds below are PLACEHOLDERS to be calibrated by the
backtest (scripts/backtest.py); do not quote them as validated.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime, timedelta

GO, CAUTION, NO_GO, UNKNOWN = "GO", "CAUTION", "NO-GO", "UNKNOWN"
STALE_AFTER = timedelta(minutes=45)
CAUTION_LOAD_MM = 20.0   # placeholder, calibrate
NOGO_LOAD_MM = 40.0      # placeholder, calibrate
PAST24_WEIGHT = 0.3      # wet ground: past rain counts for less than rain now
STEP_MIN = 15


@dataclass(frozen=True)
class Spot:
    id: str
    name: str
    pocket_depth_m: float | None = None  # from DEM; None = unknown
    known_flood_spot: bool = False
    is_underpass: bool = True


@dataclass(frozen=True)
class Weather:
    fetched_at: datetime
    past_24h_mm: float
    next_steps_mm: list[float]  # rain per 15-min step, starting now


@dataclass(frozen=True)
class Assessment:
    state: str
    reasons: list[str] = field(default_factory=list)
    minutes_to_no_go: int | None = None
    load_mm: float | None = None

    @property
    def act_as(self) -> str:
        """What a user should be told to do: UNKNOWN is treated as NO-GO."""
        return NO_GO if self.state == UNKNOWN else self.state


def susceptibility(spot: Spot) -> float:
    s = 1.0
    if spot.pocket_depth_m is not None:
        s += max(0.0, min(spot.pocket_depth_m, 3.0))  # deeper pocket, lower thresholds
    if spot.known_flood_spot:
        s += 0.5
    if spot.is_underpass:
        s += 0.5
    return s


def _state(load: float, s: float) -> str:
    if load >= NOGO_LOAD_MM / s:
        return NO_GO
    if load >= CAUTION_LOAD_MM / s:
        return CAUTION
    return GO


def assess(spot: Spot, wx: Weather | None, now: datetime) -> Assessment:
    if wx is None:
        return Assessment(UNKNOWN, ["no weather data"])
    age = now - wx.fetched_at
    if age > STALE_AFTER:
        return Assessment(UNKNOWN, [f"weather data is {int(age.total_seconds() // 60)} min old"])
    if age < timedelta(minutes=-5):
        return Assessment(UNKNOWN, ["weather timestamp is in the future"])

    s = susceptibility(spot)
    base = wx.past_24h_mm * PAST24_WEIGHT
    state = _state(base, s)
    eta = 0 if state == NO_GO else None
    cum = base
    for i, mm in enumerate(wx.next_steps_mm):
        cum += mm
        if eta is None and _state(cum, s) == NO_GO:
            eta = (i + 1) * STEP_MIN
    # state shown now = state from rain already fallen (past 24h + first step in progress)
    now_load = base + (wx.next_steps_mm[0] if wx.next_steps_mm else 0.0)
    state = _state(now_load, s)
    reasons = [f"load {now_load:.1f} mm vs no-go at {NOGO_LOAD_MM / s:.1f} mm"]
    if spot.known_flood_spot:
        reasons.append("known flood spot")
    if spot.pocket_depth_m:
        reasons.append(f"{spot.pocket_depth_m:.1f} m low pocket")
    return Assessment(state, reasons, None if state == NO_GO else eta, round(now_load, 1))
