#!/usr/bin/env python3

import sys
import click
import src.indicators

VERSION="1.3.0"

@click.command()
@click.version_option(VERSION)
@click.argument("ticker", nargs=-1, required=False)
@click.option("-p", "--period", default="5y", help="Period of Stock data.\
    Must be one of {\"ytd\", \"1y\", \"2y\", \"5y\", \"max\"}")
@click.option("-t", "--timeframe", default="1d", help="Time frame of Stock data can be string or json path.\
    Must be one of {\"1d\", \"1wk\", \"1mo\", \"3mo\"}")
@click.option("-o", "--output", default=None, help="Output CSV file name")
@click.option("-f", "--format", default="csv", help="Output format. Must be one of {\"csv\", \"parquet\", \"json\", \"xlsx\", \"avro\"}")
@click.option("-d", "--dir", default=None, help="Output directory")
@click.option("-c", "--config_json", default=None, help="Path of JSON config file for indicators")
@click.option("-e", "--engine", default="cpu", help="Computation engine to use. Must be one of {\"cpu\", \"gpu\"}")
@click.option("--profile", is_flag=True, help="Run profiling suite instead of normal calculation")
@click.option("--profile-suite", type=click.Choice(["all", "e2e", "source", "calculation", "write"]), default="all", help="Profiling suite to run")
@click.option("--profile-mode", type=click.Choice(["live", "cached"]), default=None, help="Profiling mode filter (live or cached)")
@click.option("--profile-scenario", default=None, help="Single profiling scenario to run")
@click.option("--test", is_flag=True, help="Run test suite instead of normal calculation")
@click.option("--test-suite", type=click.Choice(["all", "correctness", "integration", "formats", "batch"]), default="all", help="Test suite to run")

def main(ticker, period, timeframe, output, format, dir, config_json, engine, profile, profile_suite, profile_mode, profile_scenario, test, test_suite):
    """Fetch stock indicators for a given TICKER and save to a CSV file, or run profiling/test suite."""
    
    if test:
        # Testing mode
        import asyncio
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        
        from tests.run_tests import main as run_tests_main
        
        click.echo("Running test suite...")
        exit_code = asyncio.run(run_tests_main(suite_filter=test_suite))
        sys.exit(exit_code)
    
    if profile:
        # Profiling mode
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        if str(root) not in sys.path:
            sys.path.insert(0, str(root))
        
        from profiling.run_profiles import main as run_profiling_main
        
        # Build args for profiling
        argv = ["--suite", profile_suite]
        if profile_scenario:
            argv.extend(["--scenario", profile_scenario])
        if profile_mode:
            argv.extend(["--mode", profile_mode])
        
        # Temporarily replace sys.argv and run profiling
        old_argv = sys.argv
        sys.argv = ["indicators"] + argv
        try:
            run_profiling_main()
        finally:
            sys.argv = old_argv
        return
    
    # Normal mode
    if not ticker:
        raise click.UsageError("TICKER argument required when not using --profile")
    
    click.echo(f"Fetching stock indicators for {ticker} for the period {period} and timeframe {timeframe}")

    src.indicators.run_main(ticker, period, timeframe, output, format, dir, config_json, engine)

    click.echo(f"Indicators saved successfully")

if __name__ == "__main__":
    main()