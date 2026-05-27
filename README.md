# Stop-Loss Cluster Excursions and Intraday Reversal Predictability

Reproducible Python research code for the working paper:

**Stop-Loss Cluster Excursions and Intraday Reversal Predictability in EUR/USD and XAU/USD on the One-Hour Timeframe**

The project operationalises a liquidity-sweep / stop-loss-cluster reversal setup as a testable event study on hourly OHLCV data. It focuses on:

- rolling support/resistance zone detection from swing highs and lows
- wick excursions beyond active zones
- rejection candles closing back into the zone
- tick-volume anomaly confirmation
- fixed reward-to-risk trade outcome labelling
- statistical tests for win rate, session effects, and expected value

The paper reports null directional predictability above 50% win rate, but positive gross expectancy under a 1.5:1 reward-to-risk exit structure. This codebase is designed to make those claims auditable and to support live-data replication.

## Repository Layout

```text
forex_sweep_research/
  data/
    raw/             # MT4/MT5 CSV exports, not committed
    processed/       # cleaned parquet/CSV outputs
  outputs/
    figures/         # generated charts
    tables/          # generated result tables
  scripts/
    run_pipeline.py  # end-to-end reproduction script
  src/forex_sweep_research/
    data_loader.py
    indicators.py
    sr_zones.py
    sweep_detector.py
    backtest.py
    stats.py
    regime.py
    simulate.py
    visualise.py
  tests/
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pip install -e .
```

## Data Format

Place one-hour OHLCV CSV files in `data/raw/`. The loader accepts common MT4/MT5-style column names and normalises them to:

```text
timestamp, open, high, low, close, volume
```

Example:

```csv
timestamp,open,high,low,close,volume
2020-01-02 08:00:00,1.1200,1.1220,1.1188,1.1196,1420
```

For live replication, use broker exports for `EURUSD_H1.csv` and `XAUUSD_H1.csv`.

## Reproduce With Simulated Data

The paper's current limitation is simulation-calibrated OHLCV data. This repo includes a deterministic simulator so the full workflow can run before live broker data is added.

```powershell
python scripts/run_pipeline.py --simulate
```

Outputs are written to:

- `outputs/tables/events.csv`
- `outputs/tables/trades.csv`
- `outputs/tables/summary.csv`
- `outputs/tables/yearly_summary.csv`
- `outputs/figures/equity_curve.png`

## Run On Real Data

```powershell
python scripts/run_pipeline.py --input data/raw/EURUSD_H1.csv --symbol EURUSD
python scripts/run_pipeline.py --input data/raw/XAUUSD_H1.csv --symbol XAUUSD
```

To include transaction costs and test the trend-regime extension:

```powershell
python scripts/run_pipeline.py --input data/raw/EURUSD_H1.csv --symbol EURUSD --transaction-cost-r 0.04 --trend-filter
```

To run a parameter sensitivity sweep:

```powershell
python scripts/sensitivity_sweep.py --input data/raw/EURUSD_H1.csv --symbol EURUSD --transaction-cost-r 0.04
```

See `docs/REPLICATION_CHECKLIST.md` for the evidence standard needed before treating the results as publication-grade.

## Core Parameters

| Parameter | Default | Paper Section |
|---|---:|---|
| ATR window | 14 | 4.2 |
| Swing window | 10 | 4.2 |
| Active SR lookback | 40 candles | 4.2 |
| Zone half-width | 0.3 x ATR(14) | 4.2 |
| Wick extension | 0.1 x ATR(14) | 4.3 |
| Volume Z threshold | 1.5 | 4.3 |
| Reward-to-risk | 1.5 | 4.4 |
| Outcome horizon | 20 candles | 4.4 |
| Transaction cost | 0.0 R by default | 6.3 |
| Trend filter | off by default | 9 |
| London open window | 08:00-10:00 GMT | 3.3 |
| New York open window | 13:00-15:00 GMT | 3.3 |

## Tests

```powershell
pytest
```

## Research Notes

This repository is not trading advice. It is a research implementation intended for auditability and extension. The highest-impact next steps are:

1. Replicate on live MT4/MT5 data from at least two brokers.
2. Add higher-timeframe trend-regime filters.
3. Add composite currency-strength conditioning.
4. Extend to GBP/USD, USD/JPY, AUD/USD, XAG/USD, CME FX futures, and COMEX gold futures.
5. Add parameter sensitivity sweeps for ATR zone width, wick threshold, and volume Z threshold.
