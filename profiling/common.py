from __future__ import annotations

import cProfile
import csv
import datetime as dt
import json
import os
import platform
import pstats
import tempfile
import time
import uuid
from pathlib import Path
from typing import Any, Callable

import polars as pl

ROOT_DIR = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT_DIR / "profiling" / "results"
RAW_DIR = RESULTS_DIR / "raw"


def ensure_dirs() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def new_run_id(prefix: str = "run") -> str:
    stamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{prefix}_{stamp}_{uuid.uuid4().hex[:8]}"


def load_json(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)


def load_scenarios(scenarios_path: str | Path | None = None) -> list[dict[str, Any]]:
    path = Path(scenarios_path) if scenarios_path else ROOT_DIR / "profiling" / "scenarios.json"
    payload = load_json(path)
    return payload.get("scenarios", [])


def select_scenarios(
    scenarios: list[dict[str, Any]],
    suites: set[str],
    scenario_names: set[str] | None = None,
    mode: str | None = None,
) -> list[dict[str, Any]]:
    selected = []
    for scenario in scenarios:
        if suites and scenario.get("suite") not in suites:
            continue
        if scenario_names and scenario.get("name") not in scenario_names:
            continue
        if mode and scenario.get("mode") != mode:
            continue
        selected.append(scenario)
    return selected


def env_snapshot() -> dict[str, Any]:
    return {
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "processor": platform.processor(),
        "polars_version": pl.__version__,
    }


def gpu_available() -> tuple[bool, str | None]:
    try:
        frame = pl.DataFrame({"x": [1, 2, 3]}).lazy().select(pl.col("x") + 1).collect(engine="gpu")
        if frame.height == 3:
            return True, None
        return False, "GPU collect returned unexpected result"
    except Exception as error:
        return False, str(error)


def profile_callable(callable_obj: Callable[[], Any], prof_path: Path) -> tuple[Any, float]:
    profiler = cProfile.Profile()
    started = time.perf_counter()
    result = profiler.runcall(callable_obj)
    elapsed = time.perf_counter() - started
    profiler.dump_stats(str(prof_path))
    return result, elapsed


def top_profile_stats(prof_path: Path, count: int = 10) -> str:
    with tempfile.TemporaryFile(mode="w+") as tmp:
        stats = pstats.Stats(str(prof_path), stream=tmp)
        stats.strip_dirs().sort_stats("cumtime").print_stats(count)
        tmp.seek(0)
        return tmp.read()


def write_json(path: Path, payload: dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)


def flatten_record(record: dict[str, Any]) -> dict[str, Any]:
    flat = {
        "run_id": record.get("run_id"),
        "timestamp": record.get("timestamp"),
        "suite": record.get("suite"),
        "scenario": record.get("scenario"),
        "mode": record.get("mode"),
        "engine": record.get("engine"),
        "status": record.get("status"),
        "skip_reason": record.get("skip_reason", ""),
        "elapsed_seconds": record.get("elapsed_seconds"),
        "ticker_count": record.get("ticker_count"),
        "period": record.get("period"),
        "timeframe": record.get("timeframe"),
        "format": record.get("format"),
        "prof_path": record.get("prof_path"),
    }
    phase = record.get("phase_seconds", {}) or {}
    for key, value in phase.items():
        flat[f"phase_{key}"] = value
    return flat


def write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    rows = [flatten_record(record) for record in records]
    if not rows:
        rows = [{}]
    fieldnames: list[str] = []
    for row in rows:
        for key in row.keys():
            if key not in fieldnames:
                fieldnames.append(key)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def summarize(records: list[dict[str, Any]], run_id: str, suite: str) -> dict[str, Any]:
    completed = [x for x in records if x.get("status") == "completed"]
    skipped = [x for x in records if x.get("status") == "skipped"]
    failed = [x for x in records if x.get("status") == "failed"]
    return {
        "run_id": run_id,
        "suite": suite,
        "timestamp": utc_now(),
        "environment": env_snapshot(),
        "total": len(records),
        "completed": len(completed),
        "skipped": len(skipped),
        "failed": len(failed),
        "records": records,
    }


def fixture_frame(rows: int = 2000) -> pl.LazyFrame:
    data = {
        "date": pl.datetime_range(
            start=dt.datetime(2020, 1, 1),
            end=dt.datetime(2020, 1, 1) + dt.timedelta(days=rows - 1),
            interval="1d",
            eager=True,
        ),
        "open": [100.0 + i * 0.01 for i in range(rows)],
        "high": [101.0 + i * 0.01 for i in range(rows)],
        "low": [99.0 + i * 0.01 for i in range(rows)],
        "close": [100.5 + i * 0.01 for i in range(rows)],
        "volume": [1_000_000 + i for i in range(rows)],
        "dividends": [0.0 for _ in range(rows)],
        "stock splits": [0.0 for _ in range(rows)],
    }
    return pl.DataFrame(data).lazy()


def map_timeframe_for_period(timeframe: str, period: str) -> str:
    if timeframe.endswith(".json"):
        payload = load_json(timeframe)
        return payload.get(period, "1d")
    return timeframe


def normalize_tickers(raw: str | list[str]) -> list[str]:
    if isinstance(raw, list):
        return raw
    return [ticker.strip() for ticker in raw.split(",") if ticker.strip()]


def resolve_output_paths(prefix: str, run_id: str) -> tuple[Path, Path]:
    json_path = RESULTS_DIR / f"{prefix}_{run_id}.json"
    csv_path = RESULTS_DIR / f"{prefix}_{run_id}.csv"
    return json_path, csv_path


def result_record(
    run_id: str,
    suite: str,
    scenario: dict[str, Any],
    status: str,
    elapsed_seconds: float | None = None,
    prof_path: str | None = None,
    phase_seconds: dict[str, float] | None = None,
    skip_reason: str | None = None,
    error: str | None = None,
) -> dict[str, Any]:
    tickers = normalize_tickers(scenario.get("tickers", []))
    return {
        "run_id": run_id,
        "timestamp": utc_now(),
        "suite": suite,
        "scenario": scenario.get("name"),
        "mode": scenario.get("mode"),
        "engine": scenario.get("engine"),
        "status": status,
        "skip_reason": skip_reason,
        "error": error,
        "elapsed_seconds": elapsed_seconds,
        "phase_seconds": phase_seconds,
        "ticker_count": len(tickers),
        "period": scenario.get("period"),
        "timeframe": scenario.get("timeframe"),
        "format": scenario.get("format"),
        "prof_path": prof_path,
    }
