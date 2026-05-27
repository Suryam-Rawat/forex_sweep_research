from __future__ import annotations

import pandas as pd

from .config import StrategyConfig
from .indicators import add_indicators
from .sr_zones import active_zones_at, confirmed_swing_points


def detect_sweeps(df: pd.DataFrame, config: StrategyConfig = StrategyConfig()) -> pd.DataFrame:
    """Detect wick-extension, rejection, and volume-anomaly events."""
    panel = add_indicators(df, config.atr_window, config.volume_window)
    swings = confirmed_swing_points(panel, config.swing_window)
    events: list[dict] = []

    min_i = max(config.atr_window, config.volume_window, 2 * config.swing_window + 1)
    for i in range(min_i, len(panel)):
        row = panel.iloc[i]
        if pd.isna(row["atr"]) or pd.isna(row["volume_z"]):
            continue
        if row["volume_z"] < config.volume_z_threshold:
            continue

        delta = config.zone_atr_mult * row["atr"]
        wick_extension = config.wick_atr_mult * row["atr"]

        for zone in active_zones_at(panel, i, swings, config.sr_lookback):
            bearish = (
                zone.kind == "resistance"
                and row["high"] > zone.level + delta
                and row["high"] > zone.level + wick_extension
                and row["close"] < zone.level + delta
            )
            bullish = (
                zone.kind == "support"
                and row["low"] < zone.level - delta
                and row["low"] < zone.level - wick_extension
                and row["close"] > zone.level - delta
            )
            if bearish or bullish:
                events.append(
                    {
                        "timestamp": panel.index[i],
                        "row": i,
                        "direction": "short" if bearish else "long",
                        "zone_kind": zone.kind,
                        "zone_level": zone.level,
                        "zone_age": zone.age,
                        "entry": row["close"],
                        "wick_extreme": row["high"] if bearish else row["low"],
                        "atr": row["atr"],
                        "volume_z": row["volume_z"],
                        "in_session": is_in_session(panel.index[i], config),
                    }
                )
                break

    return pd.DataFrame(events)


def is_in_session(ts: pd.Timestamp, config: StrategyConfig = StrategyConfig()) -> bool:
    hour = ts.tz_convert("UTC").hour if ts.tzinfo else ts.hour
    london_start, london_end = config.london_open
    ny_start, ny_end = config.new_york_open
    return london_start <= hour < london_end or ny_start <= hour < ny_end
