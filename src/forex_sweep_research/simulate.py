from __future__ import annotations

import numpy as np
import pandas as pd


def simulate_ohlcv(symbol: str, periods: int = 6200, seed: int = 42) -> pd.DataFrame:
    """Create deterministic hourly OHLCV data with session volume structure."""
    rng = np.random.default_rng(seed)
    index = pd.date_range("2015-01-01", periods=periods, freq="h", tz="UTC")
    index = index[index.dayofweek < 5]
    periods = len(index)

    if symbol.upper().startswith("XAU"):
        start, sigma, base_vol = 1200.0, 3.8, 900
    else:
        start, sigma, base_vol = 1.12, 0.0009, 700

    returns = rng.normal(0, sigma, periods)
    close = start + np.cumsum(returns)
    open_ = np.r_[start, close[:-1]]
    spread = np.abs(rng.normal(sigma * 1.4, sigma * 0.45, periods))
    high = np.maximum(open_, close) + spread * rng.uniform(0.25, 1.0, periods)
    low = np.minimum(open_, close) - spread * rng.uniform(0.25, 1.0, periods)

    session_boost = np.where(index.hour.isin([8, 9, 13, 14]), 1.8, 1.0)
    volume = rng.lognormal(np.log(base_vol), 0.35, periods) * session_boost

    spike_idx = rng.choice(np.arange(60, periods - 25), size=max(12, periods // 80), replace=False)
    for i in spike_idx:
        volume[i] *= rng.uniform(2.2, 4.0)
        if rng.random() < 0.5:
            high[i] += spread[i] * rng.uniform(2.0, 4.0)
            close[i] = min(close[i], open_[i])
        else:
            low[i] -= spread[i] * rng.uniform(2.0, 4.0)
            close[i] = max(close[i], open_[i])

    return pd.DataFrame(
        {
            "open": open_,
            "high": high,
            "low": low,
            "close": close,
            "volume": volume.astype(int),
        },
        index=index,
    )
