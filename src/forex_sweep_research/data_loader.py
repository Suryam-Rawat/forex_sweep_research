from __future__ import annotations

from pathlib import Path

import pandas as pd


COLUMN_ALIASES = {
    "time": "timestamp",
    "date": "timestamp",
    "datetime": "timestamp",
    "<date>": "date",
    "<time>": "time",
    "<open>": "open",
    "<high>": "high",
    "<low>": "low",
    "<close>": "close",
    "<tickvol>": "volume",
    "tick_volume": "volume",
    "tickvol": "volume",
    "vol": "volume",
}


def load_ohlcv(path: str | Path) -> pd.DataFrame:
    """Load an OHLCV CSV and normalise common broker export column names."""
    df = pd.read_csv(path)
    df.columns = [COLUMN_ALIASES.get(c.strip().lower(), c.strip().lower()) for c in df.columns]

    if "timestamp" not in df.columns and {"date", "time"}.issubset(df.columns):
        df["timestamp"] = df["date"].astype(str) + " " + df["time"].astype(str)

    required = ["timestamp", "open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required OHLCV columns: {missing}")

    out = df[required].copy()
    out["timestamp"] = pd.to_datetime(out["timestamp"], utc=True, errors="coerce")
    for col in ["open", "high", "low", "close", "volume"]:
        out[col] = pd.to_numeric(out[col], errors="coerce")

    out = out.dropna(subset=required).sort_values("timestamp").drop_duplicates("timestamp")
    out = out.set_index("timestamp")
    return validate_ohlcv(out)


def validate_ohlcv(df: pd.DataFrame) -> pd.DataFrame:
    required = ["open", "high", "low", "close", "volume"]
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    bad_high = df["high"] < df[["open", "close", "low"]].max(axis=1)
    bad_low = df["low"] > df[["open", "close", "high"]].min(axis=1)
    if bad_high.any() or bad_low.any():
        raise ValueError("Invalid OHLC rows: high/low bounds are inconsistent.")

    if (df["volume"] < 0).any():
        raise ValueError("Volume must be non-negative.")

    return df
