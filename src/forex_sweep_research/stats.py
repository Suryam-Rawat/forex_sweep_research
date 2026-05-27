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
    net_expectancy = float(decisive["net_pnl_r"].mean()) if "net_pnl_r" in decisive and n else expectancy
    cumulative = decisive["net_pnl_r"].cumsum() if "net_pnl_r" in decisive else decisive["pnl_r"].cumsum()
    max_drawdown = _max_drawdown(cumulative)
    sharpe_like = _trade_sharpe(decisive["net_pnl_r"] if "net_pnl_r" in decisive else decisive["pnl_r"])

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
        "net_expectancy_r": net_expectancy,
        "max_drawdown_r": max_drawdown,
        "trade_sharpe": sharpe_like,
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


def yearly_summary(trades: pd.DataFrame, symbol: str = "UNKNOWN") -> pd.DataFrame:
    if trades.empty:
        return pd.DataFrame()
    decisive = trades[trades["outcome"].isin(["win", "loss"])].copy()
    if decisive.empty:
        return pd.DataFrame()
    decisive["year"] = pd.to_datetime(decisive["timestamp"], utc=True).dt.year
    pnl_col = "net_pnl_r" if "net_pnl_r" in decisive.columns else "pnl_r"
    grouped = decisive.groupby("year")
    out = grouped.agg(
        events=("outcome", "size"),
        wins=("outcome", lambda s: int((s == "win").sum())),
        losses=("outcome", lambda s: int((s == "loss").sum())),
        pnl_r=(pnl_col, "sum"),
    ).reset_index()
    out["symbol"] = symbol
    out["win_rate"] = out["wins"] / out["events"]
    return out[["symbol", "year", "events", "wins", "losses", "win_rate", "pnl_r"]]


def _max_drawdown(cumulative: pd.Series) -> float:
    if cumulative.empty:
        return math.nan
    running_high = cumulative.cummax()
    drawdown = cumulative - running_high
    return float(drawdown.min())


def _trade_sharpe(pnl: pd.Series) -> float:
    if len(pnl) < 2:
        return math.nan
    std = float(pnl.std(ddof=1))
    if std == 0:
        return math.nan
    return float(pnl.mean() / std * math.sqrt(len(pnl)))
