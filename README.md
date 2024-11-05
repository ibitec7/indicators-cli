A CLI tool to calculate common technical indicators for stock price
Here are the explanations and interpretations of each of the technical indicators added

1. Moving Averages (MA)

    Simple Moving Average (sma): This is the average of the stock’s closing prices over a specific period (e.g., 20 days). It smoothens out price data to help identify the direction of the trend. A higher SMA generally indicates a longer-term trend.

    Exponential Moving Average (ema): This is similar to SMA but gives more weight to recent prices, making it more responsive to recent price changes. EMAs are useful for identifying short-term trends and can be combined with SMAs to detect trend reversals.

Interpretation:

    When a short-term MA (like a 20-day EMA) crosses above a long-term MA (like a 50-day SMA), it’s often a bullish signal, indicating an upward trend.
    Conversely, when a short-term MA crosses below a long-term MA, it’s considered bearish.

2. Moving Average Convergence Divergence (macd)

    MACD is the difference between a short-term EMA (usually 12-day) and a long-term EMA (usually 26-day). It’s accompanied by a signal line (9-day EMA of the MACD), and their crossover points are used to identify buy or sell signals.
    MACD Histogram: The difference between the MACD line and the signal line, showing the strength of the trend.

Interpretation:

    When the MACD line crosses above the signal line, it’s a bullish signal (suggesting a potential buy).
    When the MACD line crosses below the signal line, it’s a bearish signal (suggesting a potential sell).
    A growing MACD histogram indicates increasing momentum, while a shrinking histogram suggests weakening momentum.

3. Relative Strength Index (rsi)

    RSI is a momentum oscillator that measures the speed and change of price movements on a scale from 0 to 100.
    Typically, values above 70 suggest the stock is overbought (price may decline), while values below 30 indicate the stock is oversold (price may increase).

Interpretation:

    RSI helps identify overbought and oversold conditions. If RSI goes above 70, the stock might be overvalued, which can signal a pullback. Below 30, the stock might be undervalued, signaling a potential buying opportunity.
    RSI divergences (when price moves in the opposite direction of RSI) can indicate a trend reversal.

4. Bollinger Bands (bb_upper/bb_lower)

    Bollinger Bands consist of a middle band (usually a 20-day SMA) and two outer bands, set at two standard deviations above and below the SMA. The bands expand and contract based on price volatility.

Interpretation:

    When prices touch or move outside the bands, they indicate high volatility and potential trend continuation or reversal. For example, if the price touches the upper band, it could be overbought, and if it touches the lower band, it could be oversold.
    Squeeze: When the bands contract significantly, it indicates low volatility and often precedes a sharp price move in either direction.

5. Average True Range (atr)

    ATR measures volatility by calculating the average range between high and low prices over a given period. Higher ATR values indicate higher volatility.

Interpretation:

    ATR does not indicate trend direction but rather the strength of price movements. High ATR values suggest high volatility and potential trend changes, while low ATR values indicate a stable trend or consolidation phase.
    ATR can be used as a trailing stop-loss: if a stock’s ATR is high, setting a wider stop-loss might be necessary to avoid premature exits.

6. Volume

    Volume is the number of shares traded over a certain period. Volume can validate trends: for example, a price move accompanied by high volume is generally more significant and likely to continue than a move with low volume.

Interpretation:

    High volume often accompanies strong moves, such as breakouts or breakdowns, and indicates increased trader interest.
    Low volume can indicate a lack of conviction in a price move, potentially signaling a reversal or a period of consolidation.

7. On-Balance Volume (obv)

    OBV accumulates volume based on the price movement: it adds volume on up days and subtracts volume on down days. This helps measure buying and selling pressure.

Interpretation:

    Rising OBV indicates accumulation (more buying pressure), which often supports upward price moves.
    Falling OBV suggests distribution (more selling pressure), supporting potential downward price moves.
    Divergences between OBV and price can indicate potential reversals.

8. Rate of Change (roc)

    ROC calculates the percentage change in price over a given time period. It’s used to measure the momentum of a stock’s price movement.

Interpretation:

    Positive ROC indicates upward momentum, while negative ROC shows downward momentum.
    Extreme high or low ROC values could indicate overbought or oversold conditions, respectively.
    ROC is also useful for identifying trend reversals when it diverges from the stock price.

9. Stochastic Oscillator (%K and %D)

    This indicator compares the current price to its range over a set period (typically 14 days). It has two lines, %K and %D, and fluctuates between 0 and 100.

Interpretation:

    Like RSI, a value above 80 suggests overbought conditions, while a value below 20 suggests oversold conditions.
    When the %K line crosses above the %D line in the oversold region (below 20), it’s a potential buy signal. Conversely, when it crosses below the %D line in the overbought region (above 80), it’s a potential sell signal.
    Divergences between price and the Stochastic Oscillator can indicate potential trend reversals.