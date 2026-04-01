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
    gpu_available,
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


SUITE = "e2e"


def run_suite(scenarios_path: str | None = None, scenario_name: str | None = None, mode: str | None = None) -> dict:
    ensure_dirs()
    run_id = new_run_id(SUITE)
    all_scenarios = load_scenarios(scenarios_path)
    scenarios = select_scenarios(all_scenarios, {SUITE}, {scenario_name} if scenario_name else None, mode)

    gpu_ok, gpu_reason = gpu_available()
    records = []

    for scenario in scenarios:
        scenario_engine = scenario.get("engine", "cpu")
        if scenario_engine == "gpu" and not gpu_ok:
            records.append(result_record(run_id, SUITE, scenario, "skipped", skip_reason=f"GPU unavailable: {gpu_reason}"))
            continue

        tickers = normalize_tickers(scenario.get("tickers", []))
        period = scenario.get("period", "1y")
        timeframe = map_timeframe_for_period(scenario.get("timeframe", "1d"), period)
        out_format = scenario.get("format", "csv")
        repeat = max(1, int(scenario.get("repeat", 1)))

        for iteration in range(repeat):
            prof_path = RAW_DIR / f"{run_id}_{scenario['name']}_{iteration + 1}.prof"
            output_dir = RAW_DIR / run_id / scenario["name"] / str(iteration + 1)

            def target() -> dict[str, float]:
                output_dir.mkdir(parents=True, exist_ok=True)

                start_source = indicators.time.time()
                if scenario.get("mode") == "cached":
                    from profiling.common import fixture_frame
                    sourced_data = [
                        {"data": fixture_frame(), "ticker": ticker, "period": period}
                        for ticker in tickers
                    ]
                else:
                    sourced_data = indicators.source_data(tickers, period, timeframe)
                    if not sourced_data:
                        raise RuntimeError("source_data returned no data. Check ticker availability and dependencies (e.g. pyarrow).")
                elapsed_source = indicators.time.time() - start_source

                start_calc = indicators.time.time()
                prepared_data = [
                    indicators.calculate_indicators(
                        df=frame["data"],
                        ticker=frame["ticker"],
                        period=frame["period"],
                        time_frame=timeframe,
                        config=None,
                        engine=scenario_engine,
                    )
                    for frame in sourced_data
                ]
                elapsed_calc = indicators.time.time() - start_calc

                start_write = indicators.time.time()
                tasks = [
                    indicators.write_output(
                        df=frame["data"],
                        dir=str(output_dir),
                        output_file=None,
                        ticker=frame["ticker"],
                        period=frame["period"],
                        timeframe=timeframe,
                        type=out_format,
                    )
                    for frame in prepared_data
                ]
                indicators.run_asyncio(tasks)
                elapsed_write = indicators.time.time() - start_write

                return {
                    "source": elapsed_source,
                    "calculation": elapsed_calc,
                    "write": elapsed_write,
                }

            try:
                phase_seconds, elapsed_seconds = profile_callable(target, prof_path)
                records.append(
                    result_record(
                        run_id,
                        SUITE,
                        scenario,
                        "completed",
                        elapsed_seconds=elapsed_seconds,
                        phase_seconds=phase_seconds,
                        prof_path=str(prof_path),
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
    parser = argparse.ArgumentParser(description="Run end-to-end profiling scenarios")
    parser.add_argument("--scenarios", default=None, help="Path to scenarios JSON")
    parser.add_argument("--scenario", default=None, help="Single scenario name to run")
    parser.add_argument("--mode", choices=["live", "cached"], default=None, help="Scenario mode filter")
    args = parser.parse_args()
    run_suite(args.scenarios, args.scenario, args.mode)


if __name__ == "__main__":
    main()
