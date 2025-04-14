import polars as pl
import yfinance as yf
import asyncio
import os
import json
import time

DEFAULT_CONFIG = """
{
    "sma_window": {
        "ytd": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 },
        "10y": { "1d": 200, "1wk": 100, "1mo": 50, "3mo": 25 },
        "max": { "1d": 200, "1wk": 100, "1mo": 50, "3mo": 25 }
    },
    "ema_window": {
        "ytd": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 },
        "10y": { "1d": 200, "1wk": 100, "1mo": 50, "3mo": 25 },
        "max": { "1d": 200, "1wk": 100, "1mo": 50, "3mo": 25 }
    },
    "macd_short": {
        "ytd": { "1d": 12, "1wk": 6, "1mo": 4, "3mo": 3 },
        "1y": { "1d": 12, "1wk": 6, "1mo": 4, "3mo": 3 },
        "2y": { "1d": 12, "1wk": 6, "1mo": 4, "3mo": 3 },
        "5y": { "1d": 12, "1wk": 6, "1mo": 4, "3mo": 3 },
        "10y": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 },
        "max": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 }
    },
    "macd_long": {
        "ytd": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 },
        "1y": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 },
        "2y": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 },
        "5y": { "1d": 26, "1wk": 13, "1mo": 8, "3mo": 5 },
        "10y": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 },
        "max": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 }
    },
    "macd_signal": {
        "ytd": { "1d": 9, "1wk": 5, "1mo": 3, "3mo": 2 },
        "1y": { "1d": 9, "1wk": 5, "1mo": 3, "3mo": 2 },
        "2y": { "1d": 9, "1wk": 5, "1mo": 3, "3mo": 2 },
        "5y": { "1d": 9, "1wk": 5, "1mo": 3, "3mo": 2 },
        "10y": { "1d": 18, "1wk": 9, "1mo": 5, "3mo": 3 },
        "max": { "1d": 18, "1wk": 9, "1mo": 5, "3mo": 3 }
    },
    "rsi_window": {
        "ytd": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 21, "1wk": 10, "1mo": 7, "3mo": 5 },
        "10y": { "1d": 30, "1wk": 15, "1mo": 10, "3mo": 7 },
        "max": { "1d": 30, "1wk": 15, "1mo": 10, "3mo": 7 }
    },
    "bb_window": {
        "ytd": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 },
        "10y": { "1d": 100, "1wk": 50, "1mo": 25, "3mo": 12 },
        "max": { "1d": 100, "1wk": 50, "1mo": 25, "3mo": 12 }
    },
    "roc_window": {
        "ytd": { "1d": 10, "1wk": 5, "1mo": 3, "3mo": 2 },
        "1y": { "1d": 10, "1wk": 5, "1mo": 3, "3mo": 2 },
        "2y": { "1d": 10, "1wk": 5, "1mo": 3, "3mo": 2 },
        "5y": { "1d": 20, "1wk": 10, "1mo": 5, "3mo": 3 },
        "10y": { "1d": 90, "1wk": 45, "1mo": 20, "3mo": 10 },
        "max": { "1d": 90, "1wk": 45, "1mo": 20, "3mo": 10 }
    },
    "atr_window": {
        "ytd": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 20, "1wk": 10, "1mo": 7, "3mo": 5 },
        "10y": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 },
        "max": { "1d": 50, "1wk": 25, "1mo": 15, "3mo": 8 }
    },
    "stochastic_window": {
        "ytd": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "1y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "2y": { "1d": 14, "1wk": 7, "1mo": 5, "3mo": 3 },
        "5y": { "1d": 21, "1wk": 10, "1mo": 7, "3mo": 5 },
        "10y": { "1d": 30, "1wk": 15, "1mo": 10, "3mo": 7 },
        "max": { "1d": 30, "1wk": 15, "1mo": 10, "3mo": 7 }
    }
}
"""

def macd(df, macd_short, macd_long, macd_signal):
    df = df.with_columns(
        (pl.col("close").ewm_mean(span=macd_short, adjust=False) - pl.col("close")\
            .ewm_mean(span=macd_long, adjust=False)).alias("macd")
    )

    df = df.with_columns(
        pl.col("macd").ewm_mean(span=macd_signal, adjust=False).alias("signal_line")
    )

    df = df.with_columns(
        (pl.col("macd") - pl.col("signal_line")).alias("macd_hist")
    )

    return df

def rsi(df, win):
    df = df.with_columns(
        pl.col("close").diff(1).alias("returns")
    )

    df = df.with_columns(
        (100 / (1 + (pl.when(pl.col("returns") > 0)
        .then(pl.col("returns")).otherwise(0).rolling_mean(window_size=win) \
            / pl.when(pl.col("returns") < 0).
            then(pl.col("returns")).otherwise(0).rolling_mean(window_size=win)))).alias("rsi")
    )

    return df

def bbands(df, win):
    df = df.with_columns(
        (pl.col("close").rolling_mean(window_size=win) - 2 * pl.col("close").rolling_std(window_size=win)).alias("bb_lower")
    )
    
    df = df.with_columns(
        (pl.col("close").rolling_mean(window_size=win) + 2 * pl.col("close").rolling_std(window_size=win)).alias("bb_upper")
    )

    return df

def roc(df, win):
    return df.with_columns(
        ((pl.col("close") - pl.col("close").shift(win)) / pl.col("close").shift(win) * 100).alias("roc")
    )

def atr(df, win):
    df = df.with_columns((pl.col("high") - pl.col("low")).alias("hi_lo"))
    df = df.with_columns(abs(pl.col("high") - pl.col("close").shift()).alias("hi_close"))
    df = df.with_columns(abs(pl.col("low") - pl.col("close").shift()).alias("lo_close"))
    df = df.with_columns(pl.max_horizontal(pl.col("hi_lo"), pl.col("hi_close"), pl.col("lo_close")).alias("true_range"))
    df = df.with_columns(pl.col("true_range").rolling_mean(win).alias("ATR"))

    return df

def obv(df):
    return df.with_columns(pl.col("close").pct_change().cum_sum().alias("obv"))

def stochastic_oscillator(df, period):
    df = df.with_columns(
        ((pl.col("close") - pl.col("low").rolling_min(window_size=period)) - 
        (pl.col("high").rolling_max(window_size=period) - pl.col("low").rolling_min(window_size=period))
        * 100).alias("K")
    )

    df = df.with_columns(
        pl.col("K").rolling_mean(window_size=3).alias("D")
    )

    return df

def source_data(tickers, period, timeframe) -> pl.LazyFrame:
    schema = {
        "Date": pl.Date,
        "Open": pl.Float32,
        "High": pl.Float32,
        "Low": pl.Float32,
        "Close": pl.Float32,
        "Volume": pl.UInt64,
        "Dividends": pl.Float32,
        "Stock Splits": pl.Float32
    }

    if isinstance(timeframe, dict):
        data = yf.Tickers(tickers).history(period=period, interval=timeframe[period]).reset_index()
    else:
        data = yf.Tickers(tickers).history(period=period, interval=timeframe).reset_index()

    try:
        df = pl.from_pandas(data, schema_overrides=schema).lazy()
    except Exception as e:
        print(f"Error converting data: {e}")
        return []

    return_package = []
    cols = ["Close", "High", "Low", "Open", "Volume", "Dividends", "Stock Splits"]

    valid_tickers = []
    for ticker in tickers:
        try:
            test_col = f"('Close', '{ticker}')"
            if test_col not in df.collect_schema().names():
                print(f"Skipping ticker {ticker} - no data found")
                continue
            valid_tickers.append(ticker)
        except Exception as e:
            print(f"Error checking ticker {ticker}: {e}")
            continue

    for ticker in valid_tickers:
        try:
            names = {"('Date', '')": "Date"} | {f"('{col}', '{ticker}')": col for col in cols}
            valid_cols = [col for col in names.keys() if col in df.collect_schema().names()]
            valid_names = {k: names[k] for k in valid_cols}
            package = {
                "data": df.select(valid_cols).rename(valid_names),
                "ticker": ticker,
                "period": period
            }
            return_package.append(package)
        except Exception as e:
            print(f"Error processing ticker {ticker}: {e}")

    return return_package

def calculate_indicators(df: pl.LazyFrame, ticker, period, time_frame, config=None, engine="cpu") -> pl.DataFrame:

    #Default configuration values for the indicators
    defaults = json.loads(DEFAULT_CONFIG)

    if config is not None:
        sma_window = config["sma_window"][period][time_frame] if "sma_window" in config else defaults["sma_window"][period][time_frame]
        ema_window = config["ema_window"][period][time_frame] if "ema_window" in config else defaults["ema_window"][period][time_frame]
        macd_short, macd_long, macd_signal = config["macd_short"][period][time_frame] if "macd_short" in config else defaults["macd_short"][period][time_frame],\
              config["macd_long"][period][time_frame] if "macd_long" in config else defaults["macd_long"][period][time_frame],\
                  config["macd_signal"][period][time_frame] if "macd_signal" in config else defaults["macd_signal"][period][time_frame]
        rsi_window = config["rsi_window"][period][time_frame] if "rsi_window" in config else defaults["rsi_window"][period][time_frame]
        bb_window = config["bb_window"][period][time_frame] if "bb_window" in config else defaults["bb_window"][period][time_frame]
        roc_window = config["roc_window"][period][time_frame] if "roc_window" in config else defaults["roc_window"][period][time_frame]
        atr_window = config["atr_window"][period][time_frame] if "atr_window" in config else defaults["atr_window"][period][time_frame]
        stochastic_window = config["stochastic_window"][period][time_frame] if "stochastic_window" in config else defaults["stochastic_window"][period][time_frame]
    else:
        sma_window = defaults["sma_window"][period][time_frame]
        ema_window = defaults["ema_window"][period][time_frame]
        macd_short, macd_long, macd_signal = defaults["macd_short"][period][time_frame], defaults["macd_long"][period][time_frame], defaults["macd_signal"][period][time_frame]
        rsi_window = defaults["rsi_window"][period][time_frame]
        bb_window = defaults["bb_window"][period][time_frame]
        roc_window = defaults["roc_window"][period][time_frame]
        atr_window = defaults["atr_window"][period][time_frame]
        stochastic_window = defaults["stochastic_window"][period][time_frame]

    try:
        columns = df.collect_schema().names()
    except Exception as e:
        print(f"Error collecting schema: {e}")
        # Define fallback standard column names if schema collection fails
        columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
        print(f"Using default column names: {columns}")

    df = df.rename({old: new for old, new in zip(columns, [x.lower() for x in columns])})

    df = df.with_columns(
        pl.col("close").rolling_mean(window_size=sma_window).alias(f"sma")
    )
    
    df = df.with_columns(
        pl.col("close").ewm_mean(span=ema_window).alias(f"ema")
    )

    df = macd(df, macd_short, macd_long, macd_signal)
    df = rsi(df, rsi_window)
    df = bbands(df, bb_window)
    df = roc(df, roc_window)
    df = atr(df, atr_window)
    df = obv(df)
    df = stochastic_oscillator(df, stochastic_window)

    return_package = {
        "data": df.collect(engine=engine),
        "ticker": ticker,
        "period": period
    }

    return return_package

async def write_output(df: pl.DataFrame, dir, output_file, ticker, period, timeframe, type):

    if dir is not None and not os.path.exists(dir):
        os.makedirs(dir)

    if output_file is not None and dir is not None and type is None:
        output_file = os.path.join(dir, output_file[0])
    elif output_file is not None and dir is not None and type is not None:
        output_file = os.path.join(dir, f"{output_file[0].split(".")[0]}.{type}")
    elif output_file is None and dir is not None:
        output_file = os.path.join(dir,f"{ticker}_{period}_{timeframe}.{type}")
    elif output_file is None and dir is None:
        output_file = f"{ticker}_{period}.{type}"

    if output_file.endswith(".csv"):
        await asyncio.to_thread(df.write_csv, output_file)
    elif output_file.endswith(".parquet"):
        await asyncio.to_thread(df.write_parquet, output_file)
    elif output_file.endswith(".json"):
        await asyncio.to_thread(df.write_json, output_file)
    elif output_file.endswith(".xlsx"):
        await asyncio.to_thread(df.write_excel, output_file)
    elif output_file.endswith(".avro"):
        await asyncio.to_thread(df.write_avro, output_file)
    else:
        await asyncio.to_thread(df.write_csv, output_file)

    return output_file

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

def format_time(seconds):
    """Format time in the most appropriate unit."""
    if seconds < 0.001:
        return f"{seconds*1000000:.2f} μs"
    elif seconds < 1:
        return f"{seconds*1000:.2f} ms"
    elif seconds < 60:
        return f"{seconds:.2f} s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.2f} min"
    else:
        hours = seconds / 3600
        return f"{hours:.2f} h"

def run_main(ticker, period, timeframe, output, format, dir, config_json, engine):

    start = time.time()

    if timeframe.endswith(".json"):
        with open(timeframe, "r") as f:
            time_frame = json.load(f)
    else:
        time_frame = timeframe

    config = None
    if config_json is not None:
        with open(config_json, "r") as f:
            config = json.load(f)

    tickers = []

    if ticker[0].endswith(".txt"):
        with open(ticker[0], "r") as f:
            tickers = f.read().split("\n")
    elif "," in ticker:
        tickers.extend(ticker.split(","))
    else:
        tickers = list(ticker)

    periods = []
    if period.endswith(".txt"):
        with open(period, "r") as f:
            periods = f.read().split("\n")
    elif "," in period:
        periods.extend(period.split(","))
    else:
        periods.append(period)

    outputs = []
    
    if output is not None:
        if output.endswith(".txt"):
            with open(output, "r") as f:
                outputs = [line.strip() for line in f if line.strip()]
        else:
            # If there is a comma in the string, split it, otherwise just use the string as a single element list
            outputs = output.split(",") if "," in output else [output]

    sourced_data = []

    start_source = time.time()

    for p in periods:
        sourced_data += source_data(tickers, p, timeframe=time_frame)

    elapsed_source = time.time() - start_source

    start_calc = time.time()

    prepared_data = [calculate_indicators(df=df["data"], ticker=df["ticker"], time_frame=time_frame, period=df["period"], config=config, engine=engine) for df in sourced_data]

    elapsed_calc = time.time() - start_calc

    if len(prepared_data) > len(outputs):
        for i in range(len(prepared_data) - len(outputs)):
            outputs.append(None)

    start_write = time.time()

    tasks = [write_output(df["data"], output_file=output,ticker=df["ticker"], period=df["period"], timeframe=time_frame, dir=dir, type=format) for df, output in zip(prepared_data, outputs)]
    run_asyncio(tasks)

    elapsed_write = time.time() - start_write

    elapsed = time.time() - start

    print(f"Overall Time: {format_time(elapsed)}    ||      Source Time: {format_time(elapsed_source)}   ||      Calculation Time: {format_time(elapsed_calc)}    ||      Write Time: {format_time(elapsed_write)}")
