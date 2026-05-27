from __future__ import annotations

import numpy as np
import pandas as pd


def add_indicators(df: pd.DataFrame, atr_window: int = 14, volume_window: int = 20) -> pd.DataFrame:
    out = df.copy()
    prev_close = out["close"].shift(1)
    true_range = pd.concat(
        [
            out["high"] - out["low"],
            (out["high"] - prev_close).abs(),
            (out["low"] - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    out["atr"] = true_range.rolling(atr_window, min_periods=atr_window).mean()

    vol_mean = out["volume"].shift(1).rolling(volume_window, min_periods=volume_window).mean()
    vol_std = out["volume"].shift(1).rolling(volume_window, min_periods=volume_window).std(ddof=0)
    out["volume_z"] = (out["volume"] - vol_mean) / vol_std.replace(0, np.nan)
    return out
