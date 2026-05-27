# Notebooks

Suggested notebook sequence:

1. `01_EDA.ipynb` - inspect raw broker data quality, gaps, and session volume.
2. `02_Backtest.ipynb` - run the sweep detector and trade labelling interactively.
3. `03_Results.ipynb` - reproduce headline tables and statistical tests.
4. `04_Robustness.ipynb` - parameter sweeps, sub-period tests, and transaction costs.

The scripted pipeline in `scripts/run_pipeline.py` should remain the canonical reproduction path.
