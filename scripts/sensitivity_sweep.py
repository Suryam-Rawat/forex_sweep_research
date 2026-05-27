from __future__ import annotations

import argparse
import itertools
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from forex_sweep_research import StrategyConfig
from forex_sweep_research.backtest import label_trades
from forex_sweep_research.data_loader import load_ohlcv
from forex_sweep_research.simulate import simulate_ohlcv
from forex_sweep_research.stats import summarise_trades
from forex_sweep_research.sweep_detector import detect_sweeps


def parse_float_grid(raw: str) -> list[float]:
    return [float(x.strip()) for x in raw.split(",") if x.strip()]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path)
    parser.add_argument("--symbol", default="EURUSD")
    parser.add_argument("--simulate", action="store_true")
    parser.add_argument("--zone-grid", default="0.2,0.3,0.4")
    parser.add_argument("--wick-grid", default="0.05,0.1,0.15")
    parser.add_argument("--volume-z-grid", default="1.0,1.5,2.0")
    parser.add_argument("--rr-grid", default="1.0,1.5,2.0")
    parser.add_argument("--transaction-cost-r", type=float, default=0.0)
    parser.add_argument("--out", type=Path, default=Path("outputs/tables/sensitivity.csv"))
    args = parser.parse_args()

    if args.simulate:
        datasets = {
            "EURUSD": simulate_ohlcv("EURUSD", seed=7),
            "XAUUSD": simulate_ohlcv("XAUUSD", seed=11),
        }
    elif args.input:
        datasets = {args.symbol: load_ohlcv(args.input)}
    else:
        raise SystemExit("Provide --simulate or --input.")

    rows: list[dict] = []
    grid = itertools.product(
        parse_float_grid(args.zone_grid),
        parse_float_grid(args.wick_grid),
        parse_float_grid(args.volume_z_grid),
        parse_float_grid(args.rr_grid),
    )
    for zone_atr_mult, wick_atr_mult, volume_z_threshold, reward_risk in grid:
        config = StrategyConfig(
            zone_atr_mult=zone_atr_mult,
            wick_atr_mult=wick_atr_mult,
            volume_z_threshold=volume_z_threshold,
            reward_risk=reward_risk,
            transaction_cost_r=args.transaction_cost_r,
        )
        for symbol, df in datasets.items():
            events = detect_sweeps(df, config)
            trades = label_trades(df, events, config)
            summary = summarise_trades(trades, symbol, config.reward_risk)
            summary.update(
                {
                    "zone_atr_mult": zone_atr_mult,
                    "wick_atr_mult": wick_atr_mult,
                    "volume_z_threshold": volume_z_threshold,
                    "reward_risk": reward_risk,
                    "transaction_cost_r": args.transaction_cost_r,
                }
            )
            rows.append(summary)

    out = pd.DataFrame(rows)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    out.to_csv(args.out, index=False)
    print(out.sort_values(["symbol", "net_expectancy_r"], ascending=[True, False]).head(20).to_string(index=False))


if __name__ == "__main__":
    main()
