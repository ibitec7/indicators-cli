import polars as pl
import numpy as np
import yfinance as yf
import argparse

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

def calculate_indicators(ticker, period, output_file):
    if period in ["ytd","1y","2y"]:
        sma_window = 20
        ema_window = 20
        macd_short, macd_long, macd_signal = 12, 26, 9
        rsi_window = 14
        bb_window = 20
        roc_window = 10
        atr_window = 14
        stochastic_window = 14
    elif period == "5y":
        sma_window = 50
        ema_window = 50
        macd_short, macd_long, macd_signal = 12, 26, 9
        rsi_window = 21
        bb_window = 50
        roc_window = 20
        atr_window = 20
        stochastic_window = 21
    elif period in ["10y","max"]:
        sma_window = 200
        ema_window = 200
        macd_short, macd_long, macd_signal = 26, 50, 18
        rsi_window = 30
        bb_window = 100
        roc_window = 90
        atr_window = 50
        stochastic_window = 30


    schema = {
        "Open": pl.Float32,
        "High": pl.Float32,
        "Low": pl.Float32,
        "Close": pl.Float32,
        "Volume": pl.UInt64,
        "Dividends": pl.Float32,
        "Stock Splits": pl.Float32
    }

    df = pl.from_pandas(yf.Ticker(ticker).history(period), schema_overrides=schema).lazy()
    columns = df.collect_schema().names()
    df = df.rename({old: new for old, new in zip(columns, [x.lower() for x in columns])})

    df = df.with_columns(
        pl.col("close").rolling_mean(window_size=20).alias(f"sma_{sma_window}")
    )
    df.with_columns(
        pl.col("close").ewm_mean(span=20).alias(f"ema_{ema_window}")
    )

    df = macd(df, macd_short, macd_long, macd_signal)
    df = rsi(df, rsi_window)
    df = bbands(df, bb_window)
    df = roc(df, roc_window)
    df = atr(df, atr_window)
    df = obv(df)
    
    if output_file.endswith(".csv"):
        df.collect(engine="cpu").write_csv(output_file)
    elif output_file.endswith(".parquet"):
        df.collect(engine="cpu").write_parquet(output_file)
    elif output_file.endswith(".json"):
        df.collect(engine="cpu").write_json(output_file)
    elif output_file.endswith(".xlsx"):
        df.collect(engine="cpu").write_excel(output_file)
    elif output_file.endswith(".avro"):
        df.collect(engine="cpu").write_avro(output_file)
    else:
        output_file.collect(engine="cpu").write_csv(output_file)