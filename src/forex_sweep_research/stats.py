from __future__ import annotations

import math

import pandas as pd

try:
    from scipy import stats as scipy_stats
except ModuleNotFoundError:  # pragma: no cover - exercised in minimal runtimes
    scipy_stats = None


def summarise_trades(trades: pd.DataFrame, symbol: str = "UNKNOWN", reward_risk: float = 1.5) -> dict:
    decisive = trades[trades["outcome"].isin(["win", "loss"])]
    wins = int((decisive["outcome"] == "win").sum())
    losses = int((decisive["outcome"] == "loss").sum())
    n = wins + losses
    win_rate = wins / n if n else math.nan
    gross_profit = wins * reward_risk
    gross_loss = losses
    profit_factor = gross_profit / gross_loss if gross_loss else math.inf
    expectancy = win_rate * reward_risk - (1 - win_rate) if n else math.nan

    in_session = decisive[decisive["in_session"]]
    off_session = decisive[~decisive["in_session"]]

    return {
        "symbol": symbol,
        "total_events": len(trades),
        "decisive_events": n,
        "neutral": int((trades["outcome"] == "neutral").sum()),
        "wins": wins,
        "losses": losses,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "expectancy_r": expectancy,
        "binomial_p_gt_50": binomial_p_gt_50(wins, n),
        "in_session_n": len(in_session),
        "in_session_win_rate": _win_rate(in_session),
        "off_session_n": len(off_session),
        "off_session_win_rate": _win_rate(off_session),
        "session_chi2_p": session_chi2_p(decisive),
    }


def binomial_p_gt_50(wins: int, n: int) -> float:
    if n == 0:
        return math.nan
    if scipy_stats is not None:
        return float(scipy_stats.binomtest(wins, n, p=0.5, alternative="greater").pvalue)
    return float(sum(math.comb(n, k) for k in range(wins, n + 1)) / (2**n))


def session_chi2_p(decisive: pd.DataFrame) -> float:
    if decisive.empty or decisive["in_session"].nunique() < 2:
        return math.nan
    table = pd.crosstab(decisive["in_session"], decisive["outcome"])
    for col in ["win", "loss"]:
        if col not in table.columns:
            table[col] = 0
    observed = table[["win", "loss"]].astype(float)
    row_totals = observed.sum(axis=1)
    col_totals = observed.sum(axis=0)
    total = float(observed.to_numpy().sum())
    expected = row_totals.to_numpy()[:, None] * col_totals.to_numpy()[None, :] / total
    chi2_stat = float(((observed.to_numpy() - expected) ** 2 / expected).sum())
    if scipy_stats is not None:
        return float(scipy_stats.chi2.sf(chi2_stat, df=1))
    return math.erfc(math.sqrt(chi2_stat / 2))


def _win_rate(trades: pd.DataFrame) -> float:
    if trades.empty:
        return math.nan
    return float((trades["outcome"] == "win").mean())
