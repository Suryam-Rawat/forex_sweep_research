import pandas as pd

from forex_sweep_research import StrategyConfig
from forex_sweep_research.backtest import label_trades
from forex_sweep_research.indicators import add_indicators
from forex_sweep_research.simulate import simulate_ohlcv
from forex_sweep_research.stats import summarise_trades
from forex_sweep_research.sweep_detector import detect_sweeps, is_in_session


def test_indicators_use_trailing_volume_window():
    df = simulate_ohlcv("EURUSD", periods=200, seed=1)
    out = add_indicators(df, atr_window=14, volume_window=20)
    ts = out.index[30]
    trailing = df["volume"].iloc[10:30]
    expected = (df["volume"].iloc[30] - trailing.mean()) / trailing.std(ddof=0)
    assert abs(out.loc[ts, "volume_z"] - expected) < 1e-9


def test_session_windows_are_utc_hour_based():
    assert is_in_session(pd.Timestamp("2024-01-01 08:30:00", tz="UTC"))
    assert is_in_session(pd.Timestamp("2024-01-01 13:30:00", tz="UTC"))
    assert not is_in_session(pd.Timestamp("2024-01-01 03:30:00", tz="UTC"))


def test_pipeline_produces_consistent_summary():
    config = StrategyConfig(volume_z_threshold=1.0)
    df = simulate_ohlcv("XAUUSD", periods=1500, seed=5)
    events = detect_sweeps(df, config)
    trades = label_trades(df, events, config)
    summary = summarise_trades(trades, "XAUUSD", config.reward_risk)
    assert summary["total_events"] == len(trades)
    assert summary["decisive_events"] == summary["wins"] + summary["losses"]
    assert 0 <= summary["win_rate"] <= 1 or pd.isna(summary["win_rate"])
