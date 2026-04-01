# Profiling Artifacts Overview

Each profiling run generates timestamped outputs that prove the tool executed and computed real results.

## Directory Structure

```
profiling/results/
├── latest.json                      # Latest run aggregate summary
├── latest.csv                       # Latest run aggregate CSV
├── e2e_<run_id>.json               # E2E suite summary
├── e2e_<run_id>.csv                # E2E suite results  
├── source_<run_id>.json            # Source suite summary
├── source_<run_id>.csv             # Source suite results
├── calculation_<run_id>.json       # Calculation suite summary
├── calculation_<run_id>.csv        # Calculation suite results
├── write_<run_id>.json             # Write suite summary
├── write_<run_id>.csv              # Write suite results
└── raw/
    ├── <run_id>_<scenario>_<iter>.prof         # cProfile dump
    ├── <run_id>_<scenario>_<iter>.prof         # cProfile dump
    └── <run_id>/
        └── <scenario>/
            └── <iteration>/
                ├── AAPL_1y_1d.csv              # Computed indicators CSV
                ├── AAPL_1y_1d.parquet         # Computed indicators Parquet
                └── ...
```

## Run ID Format

`<suite>_<YYYYMMDD>_<HHMMSS>_<uuid_suffix>`

Example: `e2e_20260401_202812_af92b3e5`

Ensures timestamped uniqueness so results never overwrite.

## Proof of Execution

### 1. Timing Data (JSON/CSV)

```json
{
  "run_id": "e2e_20260401_202812_af92b3e5",
  "status": "completed",
  "elapsed_seconds": 0.01345,
  "phase_seconds": {
    "source": 0.00335,
    "calculation": 0.00395,
    "write": 0.00589
  }
}
```

### 2. cProfile Dumps (.prof)

Binary cProfile output showing:
- Function call counts
- Cumulative time per function
- Call graph for performance analysis

Load and analyze:
```bash
python3 -c "import pstats; p = pstats.Stats('profiling/results/raw/e2e_*.prof'); p.print_stats()"
```

### 3. Computed Output Files

CSV/Parquet files with all 10 computed indicators:
- sma, ema, macd, signal_line, macd_hist
- rsi, bb_lower, bb_upper, roc, atr
- obv, K (%Stochastic), D

Example: `AAPL_1y_1d.csv` with 2000+ rows of OHLCV + indicators.

### 4. Metadata Snapshot

Environment info captured in every run:
- Python version
- Platform / processor
- Polars version
- Timestamp (UTC)

## Running Profiling

### Via CLI (Recommended)

```bash
# Cached mode (no network, deterministic)
indicators --profile --profile-mode cached

# Live mode (fetches real data)
indicators --profile --profile-suite e2e --profile-mode live

# Single scenario
indicators --profile --profile-scenario e2e_cpu_cached
```

### Results

All outputs in `profiling/results/`:
- Timings in `latest.json` and `latest.csv`
- Raw profiles in `raw/*.prof`
- Computed outputs in `raw/<run_id>/<scenario>/<iteration>/`

## Reproducibility

Each run is fully reproducible:
1. Run ID includes timestamp + UUID
2. Scenarios are versioned in `scenarios.json`
3. Environment snapshot captured
4. All function calls logged in cProfile
5. Output files preserved with exact timestamps

Historical runs are never lost—check `profiling/results/` for all past runs.
