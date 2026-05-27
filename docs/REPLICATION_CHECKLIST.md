# Replication Checklist

Use this checklist before citing the repository as evidence in a paper, SSRN upload, or admissions portfolio.

## Minimum Credible Replication

- Add real hourly OHLCV broker exports to `data/raw/`.
- Use at least two independent sources if possible, for example two MT4/MT5 brokers.
- Confirm timestamps are UTC or convert them before running the pipeline.
- Run the base specification:

```powershell
python scripts/run_pipeline.py --input data/raw/EURUSD_H1.csv --symbol EURUSD --transaction-cost-r 0.04
python scripts/run_pipeline.py --input data/raw/XAUUSD_H1.csv --symbol XAUUSD --transaction-cost-r 0.04
```

- Run the trend-filter specification:

```powershell
python scripts/run_pipeline.py --input data/raw/EURUSD_H1.csv --symbol EURUSD --transaction-cost-r 0.04 --trend-filter
python scripts/run_pipeline.py --input data/raw/XAUUSD_H1.csv --symbol XAUUSD --transaction-cost-r 0.04 --trend-filter
```

- Run sensitivity sweeps:

```powershell
python scripts/sensitivity_sweep.py --input data/raw/EURUSD_H1.csv --symbol EURUSD --transaction-cost-r 0.04
python scripts/sensitivity_sweep.py --input data/raw/XAUUSD_H1.csv --symbol XAUUSD --transaction-cost-r 0.04
```

## Evidence Standard

The repository is strong enough to support the paper when the following are documented:

- data source, broker, export date, timezone, and spread assumptions
- exact command used to generate each result table
- `summary.csv`, `yearly_summary.csv`, and `sensitivity.csv`
- whether results survive transaction costs
- whether results improve under trend filtering
- whether the 2023-2024 deterioration appears in live data

## What Would Make It Hard To Challenge

- Similar results across two brokers.
- Similar results on CME EUR futures and COMEX gold futures with real volume.
- No large dependence on a single exact parameter value.
- Net-positive expectancy after realistic round-trip costs.
- Honest reporting if the live-data result weakens or disappears.
