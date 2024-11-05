import pandas as pd
import numpy as np
import yfinance as yf
import argparse

def macd(close, short, long, signal_span):
    short_ema = close.ewm(span=short, adjust=False).mean()
    long_ema = close.ewm(span=long, adjust=False).mean()
    macd = short_ema - long_ema
    signal_line = macd.ewm(span = signal_span, adjust=False).mean()
    macd_hist = macd - signal_line
    return macd, signal_line, macd_hist

def rsi(close, win):
    delta = close.diff(1)
    gain = delta.where(delta>0, 0)
    loss = -delta.where(delta<0, 0)

    avg_gain = gain.rolling(window=win).mean()
    avg_loss = loss.rolling(window=win).mean()
    rs = avg_gain / avg_loss
    return (100 - (100/(1+rs)))

def bbands(close, win):
    sma = close.rolling(window=win).mean()
    std = close.rolling(window=win).std()
    upper = sma + (std * 2)
    lower = sma - (std * 2)

    return upper, lower

def atr(df, win):
    df["hi_lo"] = df["high"] - df["low"]
    df["hi_close"] = abs(df["high"] - df["close"].shift())
    df["lo_close"] = abs(df["low"] - df["close"].shift())
    df["true_range"] = df[["hi_lo", "hi_close", "lo_close"]].max(axis=1)
    df["ATR"] = df["true_range"].rolling(window=win).mean()

def obv(close, volume):
    daily_return = close.pct_change()
    direction = [1 if x>0 else -1 if x<0 else 0 for x in daily_return]
    vol_direction = direction * daily_return
    return vol_direction.cumsum()

def stochastic_oscillator(df,period):
    lowest_low = df["low"].rolling(window=period).min()
    highest_high = df["high"].rolling(window=period).max()
    K = (df["close"] - lowest_low) / (highest_high - lowest_low) * 100
    D = df["%K"].rolling(window=3).mean()
    return K,D

def calculate_indicators(ticker, period, output_file):
    if period in ["ytd","1y","2y"]:
        sma_window = 20
        ema_window = 20
        macd_short, macd_long, macd_signal = 12, 26, 9
        rsi_window = 14
        bb_window = 20
        atr_window = 14
        stochastic_window = 14
    elif period == "5y":
        sma_window = 50
        ema_window = 50
        macd_short, macd_long, macd_signal = 12, 26, 9
        rsi_window = 21
        bb_window = 50
        atr_window = 20
        stochastic_window = 21
    elif period == "max":
        sma_window = 200
        ema_window = 200
        macd_short, macd_long, macd_signal = 26, 50, 18
        rsi_window = 30
        bb_window = 100
        atr_window = 50
        stochastic_window = 30


    df = yf.Ticker(ticker).history(period=period)
    df.columns = df.columns.str.lower()

    df[f"sma_{sma_window}"] = df["close"].rolling(window=sma_window).mean()
    df[f"ema_{ema_window}"] = df["close"].ewm(span = ema_window, adjust=False).mean()
    df["macd"], df["signal_line"], df["macd_hist"] = macd(df["close"], macd_short, macd_long, macd_signal)
    df["rsi"] = rsi(df["close"], rsi_window)
    df["bb_upper"], df["bb_lower"] = bbands(df["close"], bb_window)
    atr(df, atr_window)
    df["obv"] = obv(df["close"], df["volume"])
    df["%K"], df["%D"] = stochastic_oscillator(df, stochastic_window)

    df.to_csv(output_file)
    print(f"Saved indicators to {output_file} for {ticker} over {period}.")