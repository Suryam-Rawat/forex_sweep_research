from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from forex_sweep_research import StrategyConfig
from forex_sweep_research.backtest import label_trades
from forex_sweep_research.data_loader import load_ohlcv
from forex_sweep_research.simulate import simulate_ohlcv
from forex_sweep_research.stats import summarise_trades, yearly_summary
from forex_sweep_research.sweep_detector import detect_sweeps
from forex_sweep_research.visualise import save_equity_curve


def run_one(df: pd.DataFrame, symbol: str, out_dir: Path, config: StrategyConfig) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    events = detect_sweeps(df, config)
    trades = label_trades(df, events, config)
    summary = summarise_trades(trades, symbol, config.reward_risk)
    events["symbol"] = symbol
    trades["symbol"] = symbol
    return events, trades, summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, help="CSV file with timestamp/open/high/low/close/volume columns.")
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--simulate", action="store_true", help="Run deterministic EURUSD and XAUUSD simulations.")
    parser.add_argument("--out", type=Path, default=Path("outputs"))
    parser.add_argument("--transaction-cost-r", type=float, default=0.0, help="Round-trip cost as a fraction of initial risk.")
    parser.add_argument("--trend-filter", action="store_true", help="Keep only trades aligned with EMA trend regime.")
    parser.add_argument("--trend-ema-span", type=int, default=100)
    args = parser.parse_args()

    config = StrategyConfig(
        transaction_cost_r=args.transaction_cost_r,
        use_trend_filter=args.trend_filter,
        trend_ema_span=args.trend_ema_span,
    )
    table_dir = args.out / "tables"
    figure_dir = args.out / "figures"
    table_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)

    batches = []
    if args.simulate:
        batches = [
            ("EURUSD", simulate_ohlcv("EURUSD", seed=7)),
            ("XAUUSD", simulate_ohlcv("XAUUSD", seed=11)),
        ]
    elif args.input:
        batches = [(args.symbol, load_ohlcv(args.input))]
    else:
        raise SystemExit("Provide --simulate or --input.")

    all_events, all_trades, summaries, yearly = [], [], [], []
    for symbol, df in batches:
        events, trades, summary = run_one(df, symbol, args.out, config)
        all_events.append(events)
        all_trades.append(trades)
        summaries.append(summary)
        yearly.append(yearly_summary(trades, symbol))

    events_df = pd.concat(all_events, ignore_index=True) if all_events else pd.DataFrame()
    trades_df = pd.concat(all_trades, ignore_index=True) if all_trades else pd.DataFrame()
    summary_df = pd.DataFrame(summaries)
    yearly_df = pd.concat(yearly, ignore_index=True) if yearly else pd.DataFrame()

    events_df.to_csv(table_dir / "events.csv", index=False)
    trades_df.to_csv(table_dir / "trades.csv", index=False)
    summary_df.to_csv(table_dir / "summary.csv", index=False)
    yearly_df.to_csv(table_dir / "yearly_summary.csv", index=False)
    save_equity_curve(trades_df, figure_dir / "equity_curve.png")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
