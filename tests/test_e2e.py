"""
End-to-end integration tests for the full indicators pipeline.
Tests multiple tickers and configurations.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.indicators import calculate_indicators
from tests.common import fetch_test_data
import polars as pl


class TestResult:
    def __init__(self, name, passed, error=None):
        self.name = name
        self.passed = passed
        self.error = error

    def __repr__(self):
        status = "✓ PASS" if self.passed else "✗ FAIL"
        msg = f"{status}: {self.name}"
        if self.error:
            msg += f"\n  Error: {self.error}"
        return msg


async def test_multiple_tickers():
    """Test indicator calculation for multiple tickers"""
    try:
        tickers = ["AAPL", "GOOGL", "MSFT"]
        results = []
        
        for ticker in tickers:
            df = await fetch_test_data(ticker, period="1y", timeframe="1d")
            if df is None:
                print(f"  Warning: Could not fetch data for {ticker}")
                continue
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker=ticker,
                period="1y",
                time_frame="1d"
            )
            
            data = result["data"]
            assert len(data) > 0, f"No data returned for {ticker}"
            results.append((ticker, data))
        
        assert len(results) >= 2, "Could not get data for multiple tickers"
        return TestResult("Multiple Tickers", True)
    except Exception as e:
        return TestResult("Multiple Tickers", False, str(e))


async def test_different_periods():
    """Test with different time periods"""
    try:
        periods = ["1y", "2y"]
        
        for period in periods:
            df = await fetch_test_data("AAPL", period=period, timeframe="1d")
            if df is None:
                continue
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker="AAPL",
                period=period,
                time_frame="1d"
            )
            
            data = result["data"]
            assert len(data) > 0, f"No data for period {period}"
            assert "sma" in data.columns, f"Missing indicators for period {period}"
        
        return TestResult("Different Periods", True)
    except Exception as e:
        return TestResult("Different Periods", False, str(e))


async def test_output_structure():
    """Test that output has expected structure"""
    try:
        df = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        assert df is not None, "Failed to fetch test data"
        
        df_lazy = df.lazy()
        result = calculate_indicators(
            df_lazy,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        # Check result structure
        assert isinstance(result, dict), "Result should be a dictionary"
        assert "data" in result, "Result missing 'data' key"
        assert "ticker" in result, "Result missing 'ticker' key"
        assert "period" in result, "Result missing 'period' key"
        
        data = result["data"]
        assert isinstance(data, pl.DataFrame), "Data should be a Polars DataFrame"
        
        # Check required columns
        required_cols = ["date", "open", "high", "low", "close", "volume"]
        for col in required_cols:
            assert col.lower() in [c.lower() for c in data.columns], f"Missing column {col}"
        
        return TestResult("Output Structure", True)
    except Exception as e:
        return TestResult("Output Structure", False, str(e))


async def test_all_indicators_present():
    """Test that all indicators are calculated"""
    try:
        df = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        assert df is not None, "Failed to fetch test data"
        
        df_lazy = df.lazy()
        result = calculate_indicators(
            df_lazy,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        data = result["data"]
        
        # Check all indicator columns are present
        expected_indicators = ["sma", "ema", "macd", "signal_line", "macd_hist", 
                              "rsi", "bb_upper", "bb_lower", "roc", "ATR", "obv", "K", "D"]
        
        missing = []
        for indicator in expected_indicators:
            if indicator not in data.columns:
                missing.append(indicator)
        
        assert len(missing) == 0, f"Missing indicators: {missing}"
        return TestResult("All Indicators Present", True)
    except Exception as e:
        return TestResult("All Indicators Present", False, str(e))


async def test_data_consistency():
    """Test that calculated data is consistent across runs"""
    try:
        # First run
        df1 = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        assert df1 is not None, "Failed to fetch test data"
        
        df_lazy1 = df1.lazy()
        result1 = calculate_indicators(
            df_lazy1,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        # Second run
        df2 = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        df_lazy2 = df2.lazy()
        result2 = calculate_indicators(
            df_lazy2,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        data1 = result1["data"]
        data2 = result2["data"]
        
        # Should have same number of rows
        assert len(data1) == len(data2), "Data length inconsistent across runs"
        
        # SMA values should be very similar (allowing for small floating point differences)
        sma1 = data1.select("sma").to_series().drop_nulls()
        sma2 = data2.select("sma").to_series().drop_nulls()
        
        diff = (sma1 - sma2).abs().max()
        assert diff < 0.01, f"SMA values differ too much: {diff}"
        
        return TestResult("Data Consistency", True)
    except Exception as e:
        return TestResult("Data Consistency", False, str(e))


async def test_no_null_indicators():
    """Test that indicators don't have excessive nulls"""
    try:
        df = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        assert df is not None, "Failed to fetch test data"
        
        df_lazy = df.lazy()
        result = calculate_indicators(
            df_lazy,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        data = result["data"]
        
        # Check null counts for indicators (some nulls are expected at start due to window size)
        indicator_cols = ["sma", "ema", "macd", "rsi", "bb_upper", "bb_lower", "roc", "ATR", "obv", "K", "D"]
        
        total_rows = len(data)
        for col in indicator_cols:
            if col in data.columns:
                non_null = data.select(col).to_series().drop_nulls()
                null_pct = 1.0 - (len(non_null) / total_rows)
                # Allow up to 10% nulls due to window size
                assert null_pct < 0.1, f"Column {col} has {null_pct*100:.1f}% nulls"
        
        return TestResult("No Excessive Nulls", True)
    except Exception as e:
        return TestResult("No Excessive Nulls", False, str(e))


async def run_all_tests():
    """Run all E2E tests"""
    tests = [
        test_multiple_tickers(),
        test_different_periods(),
        test_output_structure(),
        test_all_indicators_present(),
        test_data_consistency(),
        test_no_null_indicators(),
    ]
    
    return await asyncio.gather(*tests)


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    for result in results:
        print(result)
    
    print(f"\n{'='*50}")
    print(f"Integration Tests: {passed}/{total} passed")
    print(f"{'='*50}")
    
    sys.exit(0 if passed == total else 1)
