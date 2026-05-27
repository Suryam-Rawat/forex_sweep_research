from __future__ import annotations

import numpy as np
import pandas as pd


def add_ema_regime(df: pd.DataFrame, span: int = 100) -> pd.DataFrame:
    out = df.copy()
    out["ema"] = out["close"].ewm(span=span, adjust=False).mean()
    out["ema_slope"] = out["ema"].diff()
    out["trend_regime"] = np.where(out["ema_slope"] > 0, "up", "down")
    return out


def add_adx_proxy(df: pd.DataFrame, window: int = 14) -> pd.DataFrame:
    out = df.copy()
    directional_range = (out["close"] - out["close"].shift(window)).abs()
    total_range = (out["high"] - out["low"]).rolling(window).sum()
    out["adx_proxy"] = 100 * directional_range / total_range.replace(0, np.nan)
    return out
