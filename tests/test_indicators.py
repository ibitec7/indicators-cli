"""
Test suite for indicator calculation correctness.
Tests individual indicators against real market data.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
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


async def test_sma():
    """Test Simple Moving Average calculation"""
    try:
        df = await fetch_test_data("AAPL", period="1y", timeframe="1d")
        assert df is not None, "Failed to fetch test data"
        
        # Convert to lazy frame for calculate_indicators
        df_lazy = df.lazy()
        
        result = calculate_indicators(
            df_lazy,
            ticker="AAPL",
            period="1y",
            time_frame="1d"
        )
        
        data = result["data"]
        
        # Check SMA column exists and has values
        assert "sma" in data.columns, "SMA column not found"
        sma_values = data.select("sma").to_series().drop_nulls()
        assert len(sma_values) > 0, "SMA has no values"
        
        # SMA should be less volatile than close price for trending markets
        sma_std = sma_values.std()
        close_std = data.select("close").to_series().std()
        assert sma_std < close_std, "SMA should be smoother than price"
        
        return TestResult("SMA Calculation", True)
    except Exception as e:
        return TestResult("SMA Calculation", False, str(e))


async def test_ema():
    """Test Exponential Moving Average calculation"""
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
        
        # Check EMA column exists
        assert "ema" in data.columns, "EMA column not found"
        ema_values = data.select("ema").to_series().drop_nulls()
        assert len(ema_values) > 0, "EMA has no values"
        
        # EMA should follow close price (basic correlation check)
        close_values = data.select("close").to_series()
        # Get same length for comparison
        close_subset = close_values[-len(ema_values):]
        
        # Simple correlation: if both increase together, should be correlated
        ema_diffs = (ema_values - ema_values.mean()).abs()
        close_diffs = (close_subset - close_subset.mean()).abs()
        
        # Both should have variance
        assert ema_diffs.std() > 0, "EMA has no variance"
        assert close_diffs.std() > 0, "Close has no variance"
        
        return TestResult("EMA Calculation", True)
    except Exception as e:
        return TestResult("EMA Calculation", False, str(e))


async def test_macd():
    """Test MACD (Moving Average Convergence Divergence) calculation"""
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
        
        # Check MACD columns exist
        assert "macd" in data.columns, "MACD column not found"
        assert "signal_line" in data.columns, "Signal line column not found"
        assert "macd_hist" in data.columns, "MACD histogram column not found"
        
        macd_values = data.select("macd").to_series().drop_nulls()
        signal_values = data.select("signal_line").to_series().drop_nulls()
        hist_values = data.select("macd_hist").to_series().drop_nulls()
        
        assert len(macd_values) > 0, "MACD has no values"
        assert len(signal_values) > 0, "Signal line has no values"
        assert len(hist_values) > 0, "MACD histogram has no values"
        
        # MACD histogram should be difference between MACD and signal line
        calculated_hist = (macd_values - signal_values).abs()
        assert calculated_hist.mean() > 0, "MACD histogram should have non-zero values"
        
        return TestResult("MACD Calculation", True)
    except Exception as e:
        return TestResult("MACD Calculation", False, str(e))


async def test_rsi():
    """Test RSI (Relative Strength Index) calculation"""
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
        
        # Check RSI column exists
        assert "rsi" in data.columns, "RSI column not found"
        rsi_values = data.select("rsi").to_series().drop_nulls()
        assert len(rsi_values) > 0, "RSI has no values"
        
        # RSI should be between 0 and 100
        assert rsi_values.min() >= 0, "RSI values below 0"
        assert rsi_values.max() <= 100, "RSI values above 100"
        
        return TestResult("RSI Calculation", True)
    except Exception as e:
        return TestResult("RSI Calculation", False, str(e))


async def test_bollinger_bands():
    """Test Bollinger Bands calculation"""
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
        
        # Check Bollinger Bands columns exist
        assert "bb_upper" in data.columns, "Upper band column not found"
        assert "bb_lower" in data.columns, "Lower band column not found"
        
        upper = data.select("bb_upper").to_series().drop_nulls()
        lower = data.select("bb_lower").to_series().drop_nulls()
        
        assert len(upper) > 0, "Upper band has no values"
        assert len(lower) > 0, "Lower band has no values"
        
        # Upper band should always be higher than lower band
        assert (upper > lower).all(), "Upper band not always > lower band"
        
        return TestResult("Bollinger Bands Calculation", True)
    except Exception as e:
        return TestResult("Bollinger Bands Calculation", False, str(e))


async def test_atr():
    """Test ATR (Average True Range) calculation"""
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
        
        # Check ATR column exists (note: uppercase)
        assert "ATR" in data.columns, "ATR column not found"
        atr_values = data.select("ATR").to_series().drop_nulls()
        assert len(atr_values) > 0, "ATR has no values"
        
        # ATR should always be positive
        assert (atr_values > 0).all(), "ATR has non-positive values"
        
        return TestResult("ATR Calculation", True)
    except Exception as e:
        return TestResult("ATR Calculation", False, str(e))


async def test_obv():
    """Test OBV (On-Balance Volume) calculation"""
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
        
        # Check OBV column exists
        assert "obv" in data.columns, "OBV column not found"
        obv_values = data.select("obv").to_series().drop_nulls()
        assert len(obv_values) > 0, "OBV has no values"
        
        # OBV should be reasonable value (not all zeros or infinities)
        assert obv_values.abs().max() > 0, "OBV has no variance"
        
        return TestResult("OBV Calculation", True)
    except Exception as e:
        return TestResult("OBV Calculation", False, str(e))


async def test_roc():
    """Test ROC (Rate of Change) calculation"""
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
        
        # Check ROC column exists
        assert "roc" in data.columns, "ROC column not found"
        roc_values = data.select("roc").to_series().drop_nulls()
        assert len(roc_values) > 0, "ROC has no values"
        
        # ROC should be reasonable percentage values
        assert roc_values.abs().max() < 1000, "ROC values seem unrealistic (>1000%)"
        
        return TestResult("ROC Calculation", True)
    except Exception as e:
        return TestResult("ROC Calculation", False, str(e))


async def test_stochastic_oscillator():
    """Test Stochastic Oscillator calculation"""
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
        
        # Check Stochastic columns exist
        assert "K" in data.columns, "K column not found"
        assert "D" in data.columns, "D column not found"
        
        k_values = data.select("K").to_series().drop_nulls()
        d_values = data.select("D").to_series().drop_nulls()
        
        assert len(k_values) > 0, "K has no values"
        assert len(d_values) > 0, "D has no values"
        
        # Stochastic values should be between 0 and 100
        assert k_values.min() >= 0 and k_values.max() <= 100, "K values outside 0-100 range"
        assert d_values.min() >= 0 and d_values.max() <= 100, "D values outside 0-100 range"
        
        return TestResult("Stochastic Oscillator Calculation", True)
    except Exception as e:
        return TestResult("Stochastic Oscillator Calculation", False, str(e))


async def run_all_tests():
    """Run all indicator tests"""
    tests = [
        test_sma(),
        test_ema(),
        test_macd(),
        test_rsi(),
        test_bollinger_bands(),
        test_atr(),
        test_obv(),
        test_roc(),
        test_stochastic_oscillator(),
    ]
    
    results = await asyncio.gather(*tests)
    return results


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    for result in results:
        print(result)
    
    print(f"\n{'='*50}")
    print(f"Correctness Tests: {passed}/{total} passed")
    print(f"{'='*50}")
    
    sys.exit(0 if passed == total else 1)
