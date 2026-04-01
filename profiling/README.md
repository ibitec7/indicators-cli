# Profiling

This directory contains reproducible profiling scripts for `indicators-cli`.

## Quick Start (Via CLI)

Run profiling directly from the command line without separate scripts:

```bash
# Run all profiling suites in cached mode (fast, deterministic)
indicators --profile --profile-mode cached

# Run only e2e profiling
indicators --profile --profile-suite e2e --profile-mode cached

# Run one specific scenario  
indicators --profile --profile-scenario e2e_cpu_cached
```

## Scripts and Direct Use

For advanced workflows, you can also run scripts directly:

```bash
python profiling/run_profiles.py --suite all --mode cached
python profiling/profile_e2e.py --scenario e2e_cpu_cached
```

## Scenarios

Default scenarios are defined in `profiling/scenarios.json`.

Key fields:
- `suite`: `e2e`, `source`, `calculation`, or `write`
- `mode`: `live` or `cached`
- `engine`: `cpu` or `gpu`
- `repeat`: number of iterations

## Live Mode Prerequisite

Live `source` and `e2e` scenarios go through the current `source_data` conversion path, which requires `pyarrow` in this environment.

```bash
pip install pyarrow
```

## Outputs

Outputs are written to `profiling/results/`:

- Per-suite JSON summary: `profiling/results/<suite>_<run_id>.json`
- Per-suite CSV rows: `profiling/results/<suite>_<run_id>.csv`
- Aggregate JSON: `profiling/results/latest.json`
- Aggregate CSV: `profiling/results/latest.csv`
- Raw cProfile files: `profiling/results/raw/*.prof`

GPU scenarios are auto-skipped when GPU execution is unavailable, and skip reasons are included in JSON/CSV artifacts.
