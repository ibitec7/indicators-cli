import click
from indicators import indicators  # Import your indicators functions

@click.command()
@click.argument("ticker")
@click.argument("period")
@click.option("-o", "--output", default="indicators.csv", help="Output CSV file name")
def main(ticker, period, output):
    """Fetch stock indicators for a given TICKER and save to a CSV file."""
    indicators.calculate_indicators(ticker, output, period)
    click.echo(f"Indicators saved to {output} for {ticker} over {period}")

if __name__ == "__main__":
    main()
