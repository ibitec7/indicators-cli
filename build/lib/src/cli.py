#!/usr/bin/env python3

import click
import src.indicators

VERSION="1.2.7"

@click.command()
@click.version_option(VERSION)
@click.argument("ticker", nargs=-1)
@click.option("-p", "--period", default="5y", help="Period of Stock data.\
    Must be one of {\"ytd\", \"1y\", \"2y\", \"5y\", \"max\"}")
@click.option("-t", "--timeframe", default="1d", help="Time frame of Stock data can be string or json path.\
    Must be one of {\"1d\", \"1wk\", \"1mo\", \"3mo\"}")
@click.option("-o", "--output", default=None, help="Output CSV file name")
@click.option("-f", "--format", default="csv", help="Output format. Must be one of {\"csv\", \"parquet\", \"json\", \"xlsx\", \"avro\"}")
@click.option("-d", "--dir", default=None, help="Output directory")
@click.option("-c", "--config_json", default=None, help="Path of JSON config file for indicators")
@click.option("-e", "--engine", default="cpu", help="Computation engine to use. Must be one of {\"cpu\", \"gpu\"}")

def main(ticker, period, timeframe, output, format, dir, config_json, engine):
    """Fetch stock indicators for a given TICKER and save to a CSV file."""
    click.echo(f"Fetching stock indicators for {ticker} for the period {period} and timeframe {timeframe}")

    src.indicators.run_main(ticker, period, timeframe, output, format, dir, config_json, engine)

    click.echo(f"Indicators saved successfully")

if __name__ == "__main__":
    main()