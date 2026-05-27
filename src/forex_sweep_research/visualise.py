from __future__ import annotations

from pathlib import Path

import pandas as pd

from .backtest import equity_curve


def save_equity_curve(trades: pd.DataFrame, path: str | Path) -> None:
    curve = equity_curve(trades)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    try:
        import matplotlib.pyplot as plt
    except ModuleNotFoundError:
        curve.to_csv(path.with_suffix(".csv"), header=["cumulative_r"])
        return

    fig, ax = plt.subplots(figsize=(9, 4.8))
    if not curve.empty:
        curve.plot(ax=ax, color="#1f6f8b", linewidth=2)
    ax.axhline(0, color="#333333", linewidth=0.8)
    ax.set_title("Cumulative PnL in Risk Units")
    ax.set_xlabel("Event time")
    ax.set_ylabel("Cumulative R")
    ax.grid(True, alpha=0.25)
    fig.tight_layout()
    fig.savefig(path, dpi=300)
    plt.close(fig)
