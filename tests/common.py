"""
Common utilities and helpers for the test suite.

Provides functions for data fetching, result validation, and test tracking.
Mirrors profiling/common.py structure but adapted for testing purposes.
"""

import asyncio
import json
import os
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import polars as pl
import yfinance as yf

from src.indicators import calculate_indicators, source_data, write_output


def gpu_available() -> bool:
    """Check if GPU is available for computation."""
    try:
        return pl.LazyFrame({"test": [1]}).with_columns(
            pl.col("test").cast(pl.Float32)
        ).collect(streaming=True, gpu=True) is not None
    except Exception:
        return False


def load_test_config() -> Dict[str, Any]:
    """Load test configuration from tests/test_config.json."""
    config_path = Path(__file__).parent / "test_config.json"
    if config_path.exists():
        with open(config_path) as f:
            return json.load(f)
    
    # Default configuration if file doesn't exist
    return {
        "tickers": ["AAPL", "MSFT", "GOOG"],
        "periods": ["1y", "2y"],
        "timeframes": ["1d", "1wk"],
        "formats": ["csv", "parquet", "json", "xlsx", "avro"],
        "batch_tickers": ["AAPL", "MSFT", "GOOG"],
        "timeout": 60,
    }


async def fetch_test_data(
    ticker: str, period: str = "1y", timeframe: str = "1d"
) -> Optional[pl.DataFrame]:
    """
    Fetch real test data from Yahoo Finance.
    
    Args:
        ticker: Stock ticker symbol
        period: Data period (e.g., '1y', '2y', '5y')
        timeframe: Data timeframe (e.g., '1d', '1wk', '1mo')
    
    Returns:
        Polars DataFrame or None if fetch fails
    """
    try:
        yf_data = yf.Ticker(ticker)
        df = yf_data.history(period=period, interval=timeframe)
        
        if df.empty:
            return None
        
        # Reset index to convert it to a regular column
        df = df.reset_index()
        
        # Rename Date column if it exists, otherwise use the first column as Date
        if "Date" not in df.columns:
            df = df.rename(columns={df.columns[0]: "Date"})
        
        # Convert pandas to polars and return as DataFrame (not LazyFrame)
        df_polars = pl.from_pandas(df)
        return df_polars
    except Exception as e:
        print(f"Warning: Failed to fetch data for {ticker}: {e}")
        return None


async def validate_output_file(
    file_path: str, expected_ticker: str, format_type: str
) -> Dict[str, Any]:
    """
    Validate that an output file exists and contains expected data.
    
    Args:
        file_path: Path to output file
        expected_ticker: Expected ticker in the data
        format_type: Output format (csv, parquet, json, xlsx, avro)
    
    Returns:
        Dictionary with validation results: {
            'valid': bool,
            'file_exists': bool,
            'row_count': int,
            'column_count': int,
            'has_ticker': bool,
            'error': Optional[str]
        }
    """
    result = {
        "valid": False,
        "file_exists": False,
        "row_count": 0,
        "column_count": 0,
        "has_ticker": False,
        "error": None,
    }
    
    if not os.path.exists(file_path):
        result["error"] = f"File not found: {file_path}"
        return result
    
    result["file_exists"] = True
    
    try:
        if format_type == "csv":
            df = pl.read_csv(file_path)
        elif format_type == "parquet":
            df = pl.read_parquet(file_path)
        elif format_type == "json":
            df = pl.read_json(file_path)
        elif format_type == "xlsx":
            df = pl.read_excel(file_path)
        elif format_type == "avro":
            df = pl.read_avro(file_path)
        else:
            result["error"] = f"Unknown format: {format_type}"
            return result
        
        result["row_count"] = df.height
        result["column_count"] = df.width
        result["has_ticker"] = len(df) > 0  # Simple check: data exists
        result["valid"] = result["row_count"] > 0 and result["column_count"] > 0
        
    except Exception as e:
        result["error"] = f"Failed to read file: {str(e)}"
    
    return result


class TestResult:
    """Represents the result of a single test."""
    
    def __init__(self, test_name: str, test_type: str):
        self.test_name = test_name
        self.test_type = test_type  # 'correctness', 'integration', 'format', 'batch'
        self.status = "pending"  # pending, passed, failed, error
        self.elapsed_seconds = 0.0
        self.error_message = ""
        self.details = {}
        self.start_time = None
    
    def start(self):
        """Mark test as started."""
        self.start_time = time.time()
    
    def pass_test(self, details: Dict[str, Any] = None):
        """Mark test as passed."""
        self.status = "passed"
        self.elapsed_seconds = time.time() - self.start_time
        if details:
            self.details = details
    
    def fail_test(self, error_message: str, details: Dict[str, Any] = None):
        """Mark test as failed."""
        self.status = "failed"
        self.error_message = error_message
        self.elapsed_seconds = time.time() - self.start_time
        if details:
            self.details = details
    
    def error_test(self, error_message: str, details: Dict[str, Any] = None):
        """Mark test as error."""
        self.status = "error"
        self.error_message = error_message
        self.elapsed_seconds = time.time() - self.start_time
        if details:
            self.details = details
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            "test_name": self.test_name,
            "test_type": self.test_type,
            "status": self.status,
            "elapsed_seconds": round(self.elapsed_seconds, 3),
            "error_message": self.error_message,
            "details": self.details,
        }


class TestSuite:
    """Container for test results and summary statistics."""
    
    def __init__(self, suite_name: str):
        self.suite_name = suite_name
        self.results: List[TestResult] = []
        self.start_time = datetime.now().isoformat()
        self.end_time = None
    
    def add_result(self, result: TestResult):
        """Add a test result."""
        self.results.append(result)
    
    def finalize(self):
        """Mark suite as complete."""
        self.end_time = datetime.now().isoformat()
    
    def summary(self) -> Dict[str, Any]:
        """Get suite summary statistics."""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.status == "passed")
        failed = sum(1 for r in self.results if r.status == "failed")
        errors = sum(1 for r in self.results if r.status == "error")
        total_time = sum(r.elapsed_seconds for r in self.results)
        
        return {
            "suite_name": self.suite_name,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "total_tests": total,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "total_seconds": round(total_time, 3),
            "success_rate": round((passed / total * 100) if total > 0 else 0, 1),
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert suite to dictionary."""
        return {
            "summary": self.summary(),
            "results": [r.to_dict() for r in self.results],
        }


def save_test_results(results: Dict[str, Any], output_dir: str = "tests/results"):
    """
    Save test results to JSON and generate summary.
    
    Args:
        results: Dictionary with test suite results
        output_dir: Directory to save results
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Save full results
    results_path = Path(output_dir) / "latest.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nTest results saved to {results_path}")


def validate_indicator_correctness(
    df: pl.DataFrame, 
    indicator_name: str,
    ticker: str,
) -> Dict[str, Any]:
    """
    Validate that indicator calculations are correct.
    
    Args:
        df: DataFrame with calculated indicators
        indicator_name: Name of indicator to validate
        ticker: Ticker symbol
    
    Returns:
        Dictionary with validation results
    """
    validation = {
        "indicator": indicator_name,
        "ticker": ticker,
        "valid": True,
        "errors": [],
    }
    
    # Validate that columns exist
    expected_columns = {
        "SMA": ["SMA"],
        "EMA": ["EMA"],
        "MACD": ["MACD", "MACD_Signal", "MACD_Histogram"],
        "RSI": ["RSI"],
        "BB": ["BB_Upper", "BB_Lower", "BB_Middle"],
        "ATR": ["ATR"],
        "OBV": ["OBV"],
        "ROC": ["ROC"],
        "Stochastic": ["Stochastic_K", "Stochastic_D"],
    }
    
    if indicator_name in expected_columns:
        cols = expected_columns[indicator_name]
        missing = [c for c in cols if c not in df.columns]
        if missing:
            validation["valid"] = False
            validation["errors"].append(f"Missing columns: {missing}")
    
    # Validate specific indicator constraints
    if indicator_name == "RSI" and "RSI" in df.columns:
        rsi_values = df["RSI"].drop_nulls()
        if len(rsi_values) > 0:
            min_val = rsi_values.min()
            max_val = rsi_values.max()
            if min_val < 0 or max_val > 100:
                validation["valid"] = False
                validation["errors"].append(
                    f"RSI out of range [0-100]: min={min_val}, max={max_val}"
                )
    
    # Validate no unexpected NaNs in core data
    if len(df) > 0:
        non_null_rows = df.select(
            [c for c in df.columns if c not in ["Date", "Open", "High", "Low", "Close", "Volume"]]
        ).select(pl.all().is_not_null().all())
        
        if not all(non_null_rows.row(0)):
            validation["valid"] = False
            validation["errors"].append("Unexpected NaN values in calculated indicators")
    
    return validation
