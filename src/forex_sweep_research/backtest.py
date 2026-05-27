from __future__ import annotations

import pandas as pd

from .config import StrategyConfig


def label_trades(
    df: pd.DataFrame,
    events: pd.DataFrame,
    config: StrategyConfig = StrategyConfig(),
) -> pd.DataFrame:
    """Label each event by whether TP or SL is touched first within the forward window."""
    if events.empty:
        return events.assign(outcome=[], pnl_r=[])

    trades: list[dict] = []
    for event in events.to_dict("records"):
        risk = abs(event["entry"] - event["wick_extreme"])
        if risk <= 0:
            continue

        if event["direction"] == "long":
            stop = event["entry"] - risk
            take_profit = event["entry"] + config.reward_risk * risk
        else:
            stop = event["entry"] + risk
            take_profit = event["entry"] - config.reward_risk * risk

        outcome = "neutral"
        pnl_r = 0.0
        start = int(event["row"]) + 1
        end = min(len(df), start + config.outcome_horizon)
        for _, row in df.iloc[start:end].iterrows():
            hit_tp = row["high"] >= take_profit if event["direction"] == "long" else row["low"] <= take_profit
            hit_sl = row["low"] <= stop if event["direction"] == "long" else row["high"] >= stop
            if hit_tp and hit_sl:
                outcome = "loss"
                pnl_r = -1.0
                break
            if hit_tp:
                outcome = "win"
                pnl_r = config.reward_risk
                break
            if hit_sl:
                outcome = "loss"
                pnl_r = -1.0
                break

        event.update({"risk": risk, "stop": stop, "take_profit": take_profit, "outcome": outcome, "pnl_r": pnl_r})
        trades.append(event)

    return pd.DataFrame(trades)


def equity_curve(trades: pd.DataFrame) -> pd.Series:
    if trades.empty:
        return pd.Series(dtype=float)
    return trades.set_index("timestamp")["pnl_r"].cumsum()
