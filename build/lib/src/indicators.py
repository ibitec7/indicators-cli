import polars as pl
import yfinance as yf
import asyncio
import os
import json
import time

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
        (pl.col("close").rolling_mean(window_size=win) - 2 * pl.col("close").rolling_std(window_size=win)).alias("lower")
    )
    
    df = df.with_columns(
        (pl.col("close").rolling_mean(window_size=win) + 2 * pl.col("close").rolling_std(window_size=win)).alias("lower")
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

def calculate_indicators(df: pl.LazyFrame, ticker, period, config=None, engine="cpu") -> pl.DataFrame:

    #Default configuration values for the indicators
    defaults = {
        "sma_window": {
            "ytd": 20,"1y": 20,"2y": 20,"5y": 50,"10y": 200,"max": 200
        },
        "ema_window": {
            "ytd": 20,"1y": 20,"2y": 20,"5y": 50,"10y": 200,"max": 200
        },
        "macd_short": {
            "ytd": 12,"1y": 12,"2y": 12,"5y": 12,"10y": 26,"max": 26
        },
        "macd_long": {
            "ytd": 26,"1y": 26,"2y": 26,"5y": 26,"10y": 50,"max": 50
        },
        "macd_signal": {
            "ytd": 9,"1y": 9,"2y": 9,"5y": 9,"10y": 18,"max": 18
        },
        "rsi_window": {
            "ytd": 14,"1y": 14,"2y": 14,"5y": 21,"10y": 30,"max": 30
        },
        "bb_window": {
            "ytd": 20,"1y": 20,"2y": 20,"5y": 50,"10y": 100,"max": 100
        },
        "roc_window": {
            "ytd": 10,"1y": 10,"2y": 10,"5y": 20,"10y": 90,"max": 90
        },
        "atr_window": {
            "ytd": 14,"1y": 14,"2y": 14,"5y": 20,"10y": 50,"max": 50
        },
        "stochastic_window": {
            "ytd": 14,"1y": 14,"2y": 14,"5y": 21,"10y": 30,"max": 30
        }
    }

    if config is not None:
        sma_window = config["sma_window"][period] if "sma_window" in config else defaults["sma_window"][period]
        ema_window = config["ema_window"][period] if "ema_window" in config else defaults["ema_window"][period]
        macd_short, macd_long, macd_signal = config["macd_short"][period] if "macd_short" in config else defaults["macd_short"][period],\
              config["macd_long"][period] if "macd_long" in config else defaults["macd_long"][period],\
                  config["macd_signal"][period] if "macd_signal" in config else defaults["macd_signal"][period]
        rsi_window = config["rsi_window"][period] if "rsi_window" in config else defaults["rsi_window"][period]
        bb_window = config["bb_window"][period] if "bb_window" in config else defaults["bb_window"][period]
        roc_window = config["roc_window"][period] if "roc_window" in config else defaults["roc_window"][period]
        atr_window = config["atr_window"][period] if "atr_window" in config else defaults["atr_window"][period]
        stochastic_window = config["stochastic_window"][period] if "stochastic_window" in config else defaults["stochastic_window"][period]
    else:
        sma_window = defaults["sma_window"][period]
        ema_window = defaults["ema_window"][period]
        macd_short, macd_long, macd_signal = defaults["macd_short"][period], defaults["macd_long"][period], defaults["macd_signal"][period]
        rsi_window = defaults["rsi_window"][period]
        bb_window = defaults["bb_window"][period]
        roc_window = defaults["roc_window"][period]
        atr_window = defaults["atr_window"][period]
        stochastic_window = defaults["stochastic_window"][period]

    try:
        columns = df.collect_schema().names()
    except Exception as e:
        print(f"Error collecting schema: {e}")
        # Define fallback standard column names if schema collection fails
        columns = ["Date", "Open", "High", "Low", "Close", "Volume", "Dividends", "Stock Splits"]
        print(f"Using default column names: {columns}")

    df = df.rename({old: new for old, new in zip(columns, [x.lower() for x in columns])})

    df = df.with_columns(
        pl.col("close").rolling_mean(window_size=sma_window).alias(f"sma_{sma_window}")
    )
    df.with_columns(
        pl.col("close").ewm_mean(span=ema_window).alias(f"ema_{ema_window}")
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

async def write_output(df: pl.DataFrame, dir,output_file, ticker, period, type):

    if dir is not None and not os.path.exists(dir):
        os.makedirs(dir)

    if output_file is not None and dir is not None:
        output_file = f"{dir}/{output_file}"
    elif output_file is None and dir is not None:
        output_file = f"{dir}/{ticker}_{period}.{type}"
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

    config = dict()
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
            for o in output:
                output.extend(o.split(","))

    sourced_data = []

    start_source = time.time()

    for p in periods:
        sourced_data += source_data(tickers, p, timeframe=time_frame)

    elapsed_source = time.time() - start_source

    start_calc = time.time()

    prepared_data = [calculate_indicators(df=df["data"], ticker=df["ticker"], period=df["period"], config=config, engine=engine) for df in sourced_data]

    elapsed_calc = time.time() - start_calc

    if len(prepared_data) > len(outputs):
        for i in range(len(prepared_data) - len(outputs)):
            outputs.append(None)

    start_write = time.time()

    tasks = [write_output(df["data"], output_file=output,ticker=df["ticker"], period=df["period"], dir=dir, type=format) for df, output in zip(prepared_data, outputs)]
    run_asyncio(tasks)

    elapsed_write = time.time() - start_write

    elapsed = time.time() - start

    print(f"Overall Time: {format_time(elapsed)}    ||      Source Time: {format_time(elapsed_source)}   ||      Calculation Time: {format_time(elapsed_calc)}    ||      Write Time: {format_time(elapsed_write)}")
