from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class Zone:
    level: float
    kind: str
    formed_at: pd.Timestamp
    age: int


def confirmed_swing_points(df: pd.DataFrame, swing_window: int = 10) -> pd.DataFrame:
    """Mark swing points only after the right-side confirmation window has elapsed."""
    out = pd.DataFrame(index=df.index)
    high_roll = df["high"].rolling(2 * swing_window + 1, center=True).max()
    low_roll = df["low"].rolling(2 * swing_window + 1, center=True).min()
    out["swing_high"] = (df["high"] == high_roll).shift(swing_window).fillna(False).astype(bool)
    out["swing_low"] = (df["low"] == low_roll).shift(swing_window).fillna(False).astype(bool)
    return out


def active_zones_at(
    df: pd.DataFrame,
    i: int,
    swings: pd.DataFrame,
    sr_lookback: int = 40,
) -> list[Zone]:
    """Return active zones known at row i, using only previously confirmed swing points."""
    start = max(0, i - sr_lookback)
    zones: list[Zone] = []
    for j in range(start, i):
        ts = df.index[j]
        if swings["swing_high"].iloc[j]:
            zones.append(Zone(float(df["high"].iloc[j]), "resistance", ts, i - j))
        if swings["swing_low"].iloc[j]:
            zones.append(Zone(float(df["low"].iloc[j]), "support", ts, i - j))
    return _dedupe_recent_zones(zones)


def _dedupe_recent_zones(zones: list[Zone], max_count: int = 12) -> list[Zone]:
    deduped: list[Zone] = []
    for zone in sorted(zones, key=lambda z: z.age):
        if all(abs(zone.level - existing.level) > 1e-12 for existing in deduped):
            deduped.append(zone)
    return deduped[:max_count]
