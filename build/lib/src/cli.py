#!/usr/bin/env python3

import click
from .indicators import calculate_indicators, source_data, write_output
import json
import asyncio

VERSION="1.1.0"

def run_asyncio(tasks):
    if not tasks:
        return []
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        tasks_future = [asyncio.ensure_future(task) for task in tasks]
        return loop.run_until_complete(asyncio.gather(*tasks_future))
    finally:
        loop.close()

@click.command()
@click.version_option(VERSION)
@click.argument("ticker", nargs=-1)
@click.option("-p", "--period", default="5y", help="Period of Stock data.\
    Must be one of {\"ytd\", \"1y\", \"2y\", \"5y\", \"max\"}")
@click.option("-t", "--timeframe", default="daily", help="Time frame of Stock data can be string or json path.\
    Must be one of {\"1d\", \"1wk\", \"1mo\", \"3mo\"}")
@click.option("-o", "--output", default=None, help="Output CSV file name")
@click.option("-f", "--format", default="csv", help="Output format. Must be one of {\"csv\", \"parquet\", \"json\", \"xlsx\", \"avro\"}")
@click.option("-d", "--dir", default=None, help="Output directory")
@click.option("-c", "--config_json", default=None, help="Path of JSON config file for indicators")
@click.option("-e", "--engine", default="cpu", help="Computation engine to use. Must be one of {\"cpu\", \"gpu\"}")

def main(ticker, period, timeframe, output, format, dir, config_json, engine):
    """Fetch stock indicators for a given TICKER and save to a CSV file."""
    click.echo(f"Fetching stock indicators for {ticker} for the period {period} and timeframe {timeframe}")

    if timeframe.endswith(".json"):
        with open(timeframe, "r") as f:
            time_frame = json.load(f)
    else:
        time_frame = timeframe

    config = dict()
    if config_json is not None:
        with open(config_json, "r") as f:
            config = json.load(f)

    tickers = []

    if ticker[0].endswith(".txt"):
        with open(ticker[0], "r") as f:
            tickers = f.read().split("\n")
    else:
        for t in ticker:
            tickers.extend(t.split(","))

    periods = []
    if period.endswith(".txt"):
        with open(period, "r") as f:
            periods = f.read().split("\n")
    else:
        for p in period:
            periods.extend(p.split(","))

    outputs = []
    if output is not None:
        if output.endswith(".txt"):
            with open(output, "r") as f:
                outputs = [line.strip() for line in f if line.strip()]
        else:
            for o in output:
                output.extend(o.split(","))

    sourced_data = []

    for p in periods:
        sourced_data += source_data(tickers, p, timeframe=time_frame)

    prepared_data = [calculate_indicators(df=df["data"], ticker=df["ticker"], period=df["period"], config=config, engine=engine) for df in sourced_data]

    if len(prepared_data) > len(outputs):
        for i in range(len(prepared_data) - len(outputs)):
            outputs.append(None)

    tasks = [write_output(df["data"], output_file=output,ticker=df["ticker"], period=df["period"], dir=dir, type=format) for df, output in zip(prepared_data, outputs)]
    run_asyncio(tasks)

    click.echo(f"Indicators saved successfully")

if __name__ == "__main__":
    main()