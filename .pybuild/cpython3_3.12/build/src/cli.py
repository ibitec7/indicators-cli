#!/usr/bin/env python3

import click
from src import indicators

VERSION="0.1.7"

@click.command()
@click.version_option(VERSION)
@click.argument("ticker")
@click.option("-p", "--period", default="5y", help="Period of Stock data.\
    Must be one of {\"ytd\", \"1y\", \"2y\", \"5y\", \"max\"}")
@click.option("-o", "--output", default="indicators.csv", help="Output CSV file name")

def main(ticker, period, output):
    """Fetch stock indicators for a given TICKER and save to a CSV file."""
    indicators.calculate_indicators(ticker, period, output)
    click.echo(f"Indicators saved to {output} for {ticker} over {period}")

if __name__ == "__main__":
    main()
