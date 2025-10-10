# Indicators CLI

[![PyPI version](https://img.shields.io/pypi/v/indicators-cli.svg)](https://pypi.org/project/indicators-cli/)
[![Python Version](https://img.shields.io/pypi/pyversions/indicators-cli.svg)](https://pypi.org/project/indicators-cli/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://opensource.org/licenses/MIT)

A powerful command-line tool for calculating common technical indicators for stock analysis. Fetches historical stock data from Yahoo Finance API and computes a comprehensive set of technical indicators, saving the enriched dataset to various file formats.

## 📋 Table of Contents

- [Features](#features)
- [What's New](#whats-new)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Configuration](#configuration)
- [Templates](#templates)
- [Indicators](#indicators)
- [Output Formats](#output-formats)
- [Advanced Usage](#advanced-usage)
- [Interpretation](#interpretation)
- [Performance](#performance)
- [Troubleshooting](#troubleshooting)
- [Build and Publish](#build-and-publish)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

- **9 Technical Indicators**: Calculate SMA, EMA, MACD, RSI, Bollinger Bands, ATR, OBV, ROC, and Stochastic Oscillator
- **Multiple Data Sources**: Fetch data from Yahoo Finance for any listed security
- **Flexible Time Periods**: Support for YTD, 1Y, 2Y, 5Y, 10Y, and MAX periods
- **Multiple Timeframes**: Daily (1d), Weekly (1wk), Monthly (1mo), and Quarterly (3mo) data
- **Batch Processing**: Process multiple tickers simultaneously
- **Custom Configuration**: Override default indicator parameters with JSON config files
- **Multiple Output Formats**: Export to CSV, Parquet, JSON, XLSX, or AVRO
- **High Performance**: Powered by Polars library for fast, concurrent data processing
- **GPU Support**: Optional GPU acceleration for compute-intensive operations
- **Async Operations**: Asynchronous I/O for efficient data fetching and file operations
- **Lazy Evaluation**: Memory-efficient data processing with lazy computation

## 🆕 What's New

```
    - v1.2.9: Current stable release

    - v1.2.0: Added support for configuration files and downsampling.

    - v1.1.0: Added support for asynchronous handling of I/O bound tasks and downloading
              (done by yfinance backend).
    
    - v1.0.0: Upgrade to polars library to support concurrent data processing,
              lazy computations and support for both CPU and GPU engines. 
```

## 📦 Prerequisites

- **Python**: Version 3.6 or higher
- **pip**: Python package installer
- **Internet Connection**: Required to fetch data from Yahoo Finance API

## 🚀 Installation

Install the package from PyPI using pip:

```bash
pip install indicators-cli
```

To verify installation:

```bash
indicators --version
```


## 🎯 Quick Start

After installation, you can start analyzing stocks immediately:

```bash
# Analyze Apple stock with default settings (5-year period, daily data)
indicators AAPL

# Analyze with custom period and timeframe
indicators AAPL -p 2y -t 1wk

# Analyze multiple stocks at once
indicators AAPL MSFT NVDA GOOGL

# Save to a specific file and directory
indicators AAPL -o my_analysis.csv -d ./output
```

## 📚 Usage

### Basic Command Structure

```bash
indicators TICKER [OPTIONS]
```

### Required Parameters

- **TICKER**: Stock ticker symbol as listed on Yahoo Finance (e.g., AAPL, MSFT, TSLA)
  - Can specify multiple tickers: `indicators AAPL MSFT NVDA`
  - Can use a text file with one ticker per line: `indicators tickers.txt`

### Optional Parameters

| Parameter | Short | Long | Default | Description |
|-----------|-------|------|---------|-------------|
| Period | `-p` | `--period` | `5y` | Time period for data. Options: `ytd`, `1y`, `2y`, `5y`, `10y`, `max` |
| Timeframe | `-t` | `--timeframe` | `1d` | Data granularity. Options: `1d`, `1wk`, `1mo`, `3mo` or JSON file path |
| Output | `-o` | `--output` | Auto-generated | Output file name. Can be TXT file with multiple names |
| Format | `-f` | `--format` | `csv` | Output format. Options: `csv`, `parquet`, `json`, `xlsx`, `avro` |
| Directory | `-d` | `--dir` | Current dir | Directory to save output files |
| Config | `-c` | `--config_json` | None | Path to JSON config file for indicator parameters |
| Engine | `-e` | `--engine` | `cpu` | Computation engine. Options: `cpu`, `gpu` |

### Usage Examples

**Example 1**: Basic usage with default settings
```bash
indicators AAPL
```

**Example 2**: Custom period and timeframe
```bash
indicators AAPL -p 5y -t 1d -f csv -e cpu -o indicators.csv
```

**Example 3**: Multiple stocks with GPU acceleration
```bash
indicators AAPL MSFT NVDA -t 1wk -f parquet -e gpu
```

**Example 4**: Batch processing with configuration files
```bash
indicators tickers.txt -t timeframe.json -c config.json -f json -e gpu -o outputs.txt
```

**Example 5**: Export to Excel format
```bash
indicators TSLA -p 2y -t 1wk -f xlsx -o tesla_analysis.xlsx
```

**Example 6**: High-frequency data analysis
```bash
indicators AAPL -p 1y -t 1d -f parquet -e cpu -d ./analysis/2024
```

### Getting Help

```bash
indicators --help
```

## ⚙️ Configuration

### Custom Indicator Parameters

You can customize indicator parameters using JSON configuration files. This allows you to fine-tune the calculation windows for different periods and timeframes.

### Creating a Configuration File

Create a JSON file (e.g., `my_config.json`) with your custom parameters. Any omitted values will use defaults.

**Example configuration structure:**
```json
{
  "sma_window": {
    "5y": { "1d": 50, "1wk": 25 }
  },
  "rsi_window": {
    "5y": { "1d": 21 }
  }
}
```

**Using the configuration:**
```bash
indicators AAPL -c my_config.json
```

### Timeframe Configuration

For advanced users, you can specify different timeframes for different periods using a JSON file:

**Example `timeframe.json`:**
```json
{
    "ytd": "1d",
    "1y": "1d",
    "2y": "1wk",
    "5y": "1mo",
    "10y": "3mo",
    "max": "3mo"
}
```

**Usage:**
```bash
indicators AAPL -t timeframe.json
```

## 📋 Templates

### 1) Indicators JSON Config

Enter the values you want to override for whichever period you are scraping. Each integer value is a certain number of timeframe periods so if your timeframe is "1wk" for the "ytd" period then entering 20 would mean a 20 weeks window. Entering all values is not necessary. The values omitted will be replaced by default values in this template:
```
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
```

### 2) Timeframe Config

Enter the timeframe you would like to choose for each period. Entering a timeframe for each period you mention is necessary if you pass a JSON configuration.

```json
{
    "ytd": "1d",
    "1y": "1d",
    "2y": "1wk",
    "5y": "1mo",
    "10y": "3mo",
    "max": "3mo"
}
```

## 📊 Indicators

The tool calculates the following 9 technical indicators:

| Indicator | Description | Key Parameters |
|-----------|-------------|----------------|
| **SMA** | Simple Moving Average | Window size varies by period/timeframe |
| **EMA** | Exponential Moving Average | Span varies by period/timeframe |
| **MACD** | Moving Average Convergence Divergence | Short, Long, Signal windows |
| **RSI** | Relative Strength Index | Lookback window (typically 14 periods) |
| **Bollinger Bands** | Upper and Lower Bands | Window size and standard deviations |
| **ATR** | Average True Range | Rolling window for volatility |
| **OBV** | On-Balance Volume | Cumulative volume indicator |
| **ROC** | Rate of Change | Percentage change window |
| **Stochastic** | Stochastic Oscillator | %K and %D calculations |

All indicators are calculated with period-appropriate parameters that automatically adjust based on your chosen timeframe and period.

## 💾 Output Formats

The tool supports multiple output formats to suit your workflow:

| Format | Extension | Use Case |
|--------|-----------|----------|
| **CSV** | `.csv` | Universal compatibility, Excel-friendly |
| **Parquet** | `.parquet` | High performance, columnar storage |
| **JSON** | `.json` | API integration, web applications |
| **XLSX** | `.xlsx` | Native Excel format with formatting |
| **AVRO** | `.avro` | Big data systems, Apache ecosystem |

**Example:**
```bash
# CSV for Excel
indicators AAPL -f csv -o analysis.csv

# Parquet for data pipelines
indicators AAPL -f parquet -o analysis.parquet

# JSON for web apps
indicators AAPL -f json -o analysis.json
```

## 🚀 Advanced Usage

### Batch Processing Multiple Tickers

Create a text file with one ticker per line:

**tickers.txt:**
```
AAPL
MSFT
GOOGL
AMZN
TSLA
```

**Run:**
```bash
indicators tickers.txt -p 2y -t 1wk -f parquet
```

### Using Custom Configurations

**config.json:**
```json
{
  "sma_window": {
    "5y": { "1d": 100 }
  },
  "rsi_window": {
    "5y": { "1d": 21 }
  }
}
```

**Run:**
```bash
indicators AAPL -c config.json -p 5y
```

### GPU-Accelerated Processing

For large datasets or multiple tickers, use GPU acceleration:

```bash
indicators AAPL MSFT NVDA GOOGL AMZN -e gpu -t 1d -p 5y
```

**Note:** Requires compatible GPU and drivers.

## 📖 Interpretation

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

## Build and Publish

The package is automatically built and published to PyPI when a git tag starting with "v" (e.g., v1.1.0) is pushed. This process is managed by the GitHub Actions workflow located at:
    .github/workflows/workflow.yaml

## ⚡ Performance

### Optimization Features

- **Lazy Evaluation**: Polars uses lazy evaluation to optimize query plans before execution
- **Parallel Processing**: Multi-threaded operations for faster computation
- **Memory Efficiency**: Columnar data format reduces memory footprint
- **GPU Acceleration**: Optional GPU support for compute-intensive operations
- **Async I/O**: Non-blocking file operations and data fetching

### Performance Tips

1. **Use Parquet Format**: Faster read/write operations compared to CSV
   ```bash
   indicators AAPL -f parquet
   ```

2. **Enable GPU for Large Datasets**: Significant speedup for multiple tickers
   ```bash
   indicators AAPL MSFT GOOGL AMZN TSLA -e gpu
   ```

3. **Choose Appropriate Timeframes**: Coarser timeframes (1wk, 1mo) process faster
   ```bash
   indicators AAPL -p 10y -t 1mo  # Faster than 1d
   ```

### Benchmarks

Typical processing times on a standard laptop (4-core CPU):
- Single ticker, 5-year daily data: ~2-5 seconds
- 5 tickers, 5-year daily data: ~8-15 seconds
- Single ticker with GPU acceleration: ~1-2 seconds

## 🔧 Troubleshooting

### Common Issues

**Issue**: `ModuleNotFoundError: No module named 'indicators'`
- **Solution**: Ensure you installed the package: `pip install indicators-cli`

**Issue**: `Ticker not found` or `No data available`
- **Solution**: Verify the ticker symbol on Yahoo Finance. Some delisted or international stocks may not be available.

**Issue**: GPU acceleration not working
- **Solution**: 
  1. Verify you have a compatible NVIDIA GPU
  2. Install CUDA toolkit
  3. Install GPU-enabled Polars: `pip install polars-gpu`

**Issue**: Permission denied when saving files
- **Solution**: Ensure you have write permissions in the target directory or specify a different directory with `-d`

**Issue**: Out of memory errors
- **Solution**: 
  1. Use coarser timeframes (1wk instead of 1d)
  2. Process fewer tickers at once
  3. Use Parquet format which is more memory-efficient

### Debug Mode

For detailed error messages, run Python with verbose output:
```bash
python -v -m src.cli AAPL
```

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. **Report Bugs**: Open an issue with detailed information
2. **Suggest Features**: Share your ideas for new indicators or features
3. **Submit Pull Requests**: Fix bugs or add features
4. **Improve Documentation**: Help make the docs better

### Development Setup

```bash
# Clone the repository
git clone https://github.com/ibitec7/indicators-cli.git
cd indicators-cli

# Install dependencies
pip install -r requirements.txt

# Install in development mode
pip install -e .

# Run the tool
indicators AAPL
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance API** (via yfinance) for providing stock data
- **Polars** for high-performance data processing
- **Click** for the intuitive CLI interface

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/ibitec7/indicators-cli/issues)
- **Email**: syed.ibrahim.omer.2@gmail.com
- **PyPI**: [indicators-cli](https://pypi.org/project/indicators-cli/)

## 🌟 Star History

If you find this tool useful, please consider giving it a star on GitHub! ⭐

---

**Made with ❤️ for the trading community**
