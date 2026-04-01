from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from profiling.common import (
    RAW_DIR,
    ensure_dirs,
    fixture_frame,
    load_scenarios,
    map_timeframe_for_period,
    new_run_id,
    normalize_tickers,
    profile_callable,
    resolve_output_paths,
    result_record,
    select_scenarios,
    summarize,
    write_csv,
    write_json,
)
from src import indicators


SUITE = "write"


def run_suite(scenarios_path: str | None = None, scenario_name: str | None = None, mode: str | None = None) -> dict:
    ensure_dirs()
    run_id = new_run_id(SUITE)
    all_scenarios = load_scenarios(scenarios_path)
    scenarios = select_scenarios(all_scenarios, {SUITE}, {scenario_name} if scenario_name else None, mode)
    records = []

    for scenario in scenarios:
        tickers = normalize_tickers(scenario.get("tickers", []))
        ticker = tickers[0] if tickers else "AAPL"
        period = scenario.get("period", "1y")
        timeframe = map_timeframe_for_period(scenario.get("timeframe", "1d"), period)
        out_format = scenario.get("format", "csv")
        repeat = max(1, int(scenario.get("repeat", 1)))

        for iteration in range(repeat):
            prof_path = RAW_DIR / f"{run_id}_{scenario['name']}_{iteration + 1}.prof"
            out_dir = RAW_DIR / run_id / scenario["name"] / str(iteration + 1)

            def target() -> int:
                out_dir.mkdir(parents=True, exist_ok=True)
                tasks = [
                    indicators.write_output(
                        df=fixture_frame().collect(),
                        dir=str(out_dir),
                        output_file=None,
                        ticker=ticker,
                        period=period,
                        timeframe=timeframe,
                        type=out_format,
                    )
                ]
                paths = indicators.run_asyncio(tasks)
                return len(paths)

            try:
                _, elapsed_seconds = profile_callable(target, prof_path)
                records.append(
                    result_record(
                        run_id,
                        SUITE,
                        scenario,
                        "completed",
                        elapsed_seconds=elapsed_seconds,
                        prof_path=str(prof_path),
                        phase_seconds={"write": elapsed_seconds},
                    )
                )
            except Exception as error:
                records.append(
                    result_record(
                        run_id,
                        SUITE,
                        scenario,
                        "failed",
                        prof_path=str(prof_path),
                        error=str(error),
                    )
                )

    summary = summarize(records, run_id, SUITE)
    json_path, csv_path = resolve_output_paths(SUITE, run_id)
    write_json(json_path, summary)
    write_csv(csv_path, records)
    print(f"Wrote summary: {json_path}")
    print(f"Wrote csv: {csv_path}")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run write-phase profiling scenarios")
    parser.add_argument("--scenarios", default=None, help="Path to scenarios JSON")
    parser.add_argument("--scenario", default=None, help="Single scenario name to run")
    parser.add_argument("--mode", choices=["live", "cached"], default=None, help="Scenario mode filter")
    args = parser.parse_args()
    run_suite(args.scenarios, args.scenario, args.mode)


if __name__ == "__main__":
    main()
