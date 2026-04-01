"""
Batch processing tests for handling multiple tickers/periods.
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


async def test_batch_single_ticker_multiple_periods():
    """Test processing same ticker across different periods"""
    try:
        ticker = "AAPL"
        periods = ["1y", "2y"]
        results = []
        
        for period in periods:
            df = await fetch_test_data(ticker, period=period, timeframe="1d")
            if df is None:
                continue
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker=ticker,
                period=period,
                time_frame="1d"
            )
            
            results.append((period, result["data"]))
        
        assert len(results) >= 1, "Could not process any periods"
        
        # Verify each result has data
        for period, data in results:
            assert len(data) > 0, f"No data for period {period}"
            assert "sma" in data.columns, f"Missing SMA for period {period}"
        
        return TestResult("Batch Single Ticker Multiple Periods", True)
    except Exception as e:
        return TestResult("Batch Single Ticker Multiple Periods", False, str(e))


async def test_batch_multiple_tickers_same_period():
    """Test processing multiple tickers for same period"""
    try:
        tickers = ["AAPL", "GOOGL", "MSFT"]
        period = "1y"
        results = []
        
        for ticker in tickers:
            df = await fetch_test_data(ticker, period=period, timeframe="1d")
            if df is None:
                print(f"  Warning: Could not fetch {ticker}")
                continue
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker=ticker,
                period=period,
                time_frame="1d"
            )
            
            results.append((ticker, result))
        
        assert len(results) >= 2, "Could not process multiple tickers"
        
        # Verify each ticker has complete data
        for expected_ticker, result in results:
            data = result["data"]
            assert len(data) > 0, f"No data for {expected_ticker}"
            # Check ticker in result matches what we expected
            assert result["ticker"] == expected_ticker, f"Ticker mismatch: expected {expected_ticker}, got {result['ticker']}"
        
        return TestResult("Batch Multiple Tickers Same Period", True)
    except Exception as e:
        return TestResult("Batch Multiple Tickers Same Period", False, str(e))


async def test_batch_processing_sequential():
    """Test sequential batch processing"""
    try:
        ticker_period_pairs = [
            ("AAPL", "1y"),
            ("AAPL", "2y"),
            ("GOOGL", "1y"),
        ]
        
        results = []
        for ticker, period in ticker_period_pairs:
            df = await fetch_test_data(ticker, period=period, timeframe="1d")
            if df is None:
                continue
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker=ticker,
                period=period,
                time_frame="1d"
            )
            
            results.append(result["data"])
        
        assert len(results) >= 2, "Could not process batch"
        
        # Verify all have indicators
        for data in results:
            assert "sma" in data.columns, "Missing SMA in batch result"
            assert len(data) > 0, "Empty result in batch"
        
        return TestResult("Batch Processing Sequential", True)
    except Exception as e:
        return TestResult("Batch Processing Sequential", False, str(e))


async def test_batch_processing_parallel():
    """Test parallel batch processing"""
    try:
        ticker_period_pairs = [
            ("AAPL", "1y"),
            ("GOOGL", "1y"),
            ("MSFT", "1y"),
        ]
        
        async def process_ticker_period(ticker, period):
            df = await fetch_test_data(ticker, period=period, timeframe="1d")
            if df is None:
                return None
            
            df_lazy = df.lazy()
            result = calculate_indicators(
                df_lazy,
                ticker=ticker,
                period=period,
                time_frame="1d"
            )
            return result["data"]
        
        # Process all in parallel
        tasks = [process_ticker_period(ticker, period) 
                for ticker, period in ticker_period_pairs]
        results = await asyncio.gather(*tasks)
        
        # Filter out None results
        results = [r for r in results if r is not None]
        
        assert len(results) >= 2, "Could not process parallel batch"
        
        # Verify all have indicators
        for data in results:
            if data is not None:
                assert "sma" in data.columns, "Missing SMA in parallel batch result"
        
        return TestResult("Batch Processing Parallel", True)
    except Exception as e:
        return TestResult("Batch Processing Parallel", False, str(e))


async def test_batch_error_handling():
    """Test that batch processing handles errors gracefully"""
    try:
        tickers = ["AAPL", "INVALID_TICKER_XYZ", "GOOGL"]
        results = []
        errors = []
        
        for ticker in tickers:
            try:
                df = await fetch_test_data(ticker, period="1y", timeframe="1d")
                if df is None:
                    errors.append(ticker)
                    continue
                
                df_lazy = df.lazy()
                result = calculate_indicators(
                    df_lazy,
                    ticker=ticker,
                    period="1y",
                    time_frame="1d"
                )
                
                results.append(result["data"])
            except Exception as e:
                errors.append((ticker, str(e)))
        
        # Should have some valid results despite one bad ticker
        assert len(results) >= 1, "Batch processing failed with no valid results"
        
        return TestResult("Batch Error Handling", True)
    except Exception as e:
        return TestResult("Batch Error Handling", False, str(e))


async def run_all_tests():
    """Run all batch tests"""
    tests = [
        test_batch_single_ticker_multiple_periods(),
        test_batch_multiple_tickers_same_period(),
        test_batch_processing_sequential(),
        test_batch_processing_parallel(),
        test_batch_error_handling(),
    ]
    
    return await asyncio.gather(*tests)


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    for result in results:
        print(result)
    
    print(f"\n{'='*50}")
    print(f"Batch Tests: {passed}/{total} passed")
    print(f"{'='*50}")
    
    sys.exit(0 if passed == total else 1)
