"""
Format validation tests for output in different formats.
"""

import asyncio
import sys
import tempfile
import os
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


async def test_csv_format():
    """Test CSV output format"""
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
        
        # Write to CSV
        with tempfile.TemporaryDirectory() as tmpdir:
            csv_path = os.path.join(tmpdir, "test.csv")
            data.write_csv(csv_path)
            
            # Verify file exists and has content
            assert os.path.exists(csv_path), "CSV file not created"
            assert os.path.getsize(csv_path) > 0, "CSV file is empty"
            
            # Read back and verify structure
            df_read = pl.read_csv(csv_path)
            assert len(df_read) == len(data), "CSV row count mismatch"
            assert len(df_read.columns) == len(data.columns), "CSV column count mismatch"
        
        return TestResult("CSV Format", True)
    except Exception as e:
        return TestResult("CSV Format", False, str(e))


async def test_parquet_format():
    """Test Parquet output format"""
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
        
        # Write to Parquet
        with tempfile.TemporaryDirectory() as tmpdir:
            parquet_path = os.path.join(tmpdir, "test.parquet")
            data.write_parquet(parquet_path)
            
            # Verify file exists and has content
            assert os.path.exists(parquet_path), "Parquet file not created"
            assert os.path.getsize(parquet_path) > 0, "Parquet file is empty"
            
            # Read back and verify structure
            df_read = pl.read_parquet(parquet_path)
            assert len(df_read) == len(data), "Parquet row count mismatch"
            assert len(df_read.columns) == len(data.columns), "Parquet column count mismatch"
        
        return TestResult("Parquet Format", True)
    except Exception as e:
        return TestResult("Parquet Format", False, str(e))


async def test_json_format():
    """Test JSON output format"""
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
        
        # Write to JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            json_path = os.path.join(tmpdir, "test.json")
            data.write_json(json_path)
            
            # Verify file exists and has content
            assert os.path.exists(json_path), "JSON file not created"
            assert os.path.getsize(json_path) > 0, "JSON file is empty"
            
            # Read back and verify structure
            df_read = pl.read_json(json_path)
            assert len(df_read) == len(data), "JSON row count mismatch"
            assert len(df_read.columns) == len(data.columns), "JSON column count mismatch"
        
        return TestResult("JSON Format", True)
    except Exception as e:
        return TestResult("JSON Format", False, str(e))


async def test_ndjson_format():
    """Test NDJSON output format"""
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
        
        # Write to NDJSON
        with tempfile.TemporaryDirectory() as tmpdir:
            ndjson_path = os.path.join(tmpdir, "test.ndjson")
            data.write_ndjson(ndjson_path)
            
            # Verify file exists and has content
            assert os.path.exists(ndjson_path), "NDJSON file not created"
            assert os.path.getsize(ndjson_path) > 0, "NDJSON file is empty"
            
            # Read back and verify structure
            df_read = pl.read_ndjson(ndjson_path)
            assert len(df_read) == len(data), "NDJSON row count mismatch"
            assert len(df_read.columns) == len(data.columns), "NDJSON column count mismatch"
        
        return TestResult("NDJSON Format", True)
    except Exception as e:
        return TestResult("NDJSON Format", False, str(e))


async def test_excel_format():
    """Test Excel output format"""
    try:
        # Check if openpyxl is available
        try:
            import openpyxl
        except ImportError:
            return TestResult("Excel Format", True, "openpyxl not installed (skipped)")
        
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
        
        # Remove timezone info from datetime columns (Excel doesn't support timezones)
        data_for_excel = data
        for col in data_for_excel.columns:
            if data_for_excel[col].dtype == pl.Datetime:
                # Convert to string without timezone
                data_for_excel = data_for_excel.with_columns(
                    pl.col(col).dt.replace_time_zone(None).alias(col)
                )
        
        # Write to Excel
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_path = os.path.join(tmpdir, "test.xlsx")
            data_for_excel.write_excel(excel_path)
            
            # Verify file exists and has content
            assert os.path.exists(excel_path), "Excel file not created"
            assert os.path.getsize(excel_path) > 0, "Excel file is empty"
        
        return TestResult("Excel Format", True)
    except Exception as e:
        return TestResult("Excel Format", False, str(e))


async def run_all_tests():
    """Run all format tests"""
    tests = [
        test_csv_format(),
        test_parquet_format(),
        test_json_format(),
        test_ndjson_format(),
        test_excel_format(),
    ]
    
    return await asyncio.gather(*tests)


if __name__ == "__main__":
    results = asyncio.run(run_all_tests())
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    
    for result in results:
        print(result)
    
    print(f"\n{'='*50}")
    print(f"Format Tests: {passed}/{total} passed")
    print(f"{'='*50}")
    
    sys.exit(0 if passed == total else 1)
