from __future__ import annotations

import argparse
from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from profiling.common import RESULTS_DIR, RAW_DIR, ensure_dirs, write_csv, write_json
from profiling.profile_calculation import run_suite as run_calc
from profiling.profile_e2e import run_suite as run_e2e
from profiling.profile_source import run_suite as run_source
from profiling.profile_write import run_suite as run_write


def main() -> None:
    parser = argparse.ArgumentParser(description="Run profiling suites for indicators-cli")
    parser.add_argument(
        "--suite",
        default="all",
        choices=["all", "e2e", "source", "calculation", "write"],
        help="Suite to run",
    )
    parser.add_argument("--scenario", default=None, help="Single scenario name to run")
    parser.add_argument("--mode", choices=["live", "cached"], default=None, help="Scenario mode filter")
    parser.add_argument("--scenarios", default=None, help="Path to scenarios JSON")
    args = parser.parse_args()

    ensure_dirs()

    summaries = []
    if args.suite in {"all", "e2e"}:
        summaries.append(run_e2e(args.scenarios, args.scenario, args.mode))
    if args.suite in {"all", "source"}:
        summaries.append(run_source(args.scenarios, args.scenario, args.mode))
    if args.suite in {"all", "calculation"}:
        summaries.append(run_calc(args.scenarios, args.scenario, args.mode))
    if args.suite in {"all", "write"}:
        summaries.append(run_write(args.scenarios, args.scenario, args.mode))

    all_records = []
    for summary in summaries:
        all_records.extend(summary.get("records", []))

    latest_json = RESULTS_DIR / "latest.json"
    latest_csv = RESULTS_DIR / "latest.csv"
    payload = {
        "suite": args.suite,
        "mode": args.mode,
        "scenario": args.scenario,
        "summaries": summaries,
        "records": all_records,
    }
    write_json(latest_json, payload)
    write_csv(latest_csv, all_records)

    print(f"✓ Wrote aggregate summary: {latest_json}")
    print(f"✓ Wrote aggregate csv: {latest_csv}")
    print(f"✓ Output artifacts preserved in: {RAW_DIR}")
    print(f"  - Timings: profiling/results/latest.json and latest.csv")
    print(f"  - Raw .prof files: profiling/results/raw/")
    print(f"  - Indicator output: profiling/results/raw/<run_id>/<scenario>/<iteration>/")
    print(f"\nRun completed successfully. Profiling data saved with full reproducibility.")


if __name__ == "__main__":
    main()
