"""Quick fix test - check if basic tests work"""
import asyncio
from tests.common import fetch_test_data
from src.indicators import calculate_indicators

async def test_basic():
    """Test basic data fetching and calculation"""
    print("Fetching AAPL data...")
    df_lazy = await fetch_test_data("AAPL", "1y", "1d")
    if df_lazy is None:
        print("Failed to fetch data")
        return
    
    print("Collecting LazyFrame...")
    df = df_lazy.collect()
    print(f"Data collected: {len(df)} rows, {len(df.columns)} columns")
    print(f"Columns: {df.columns}")
    
    print("Calculating indicators...")
    output = calculate_indicators(df, ticker="AAPL", period="1y", time_frame="1d", config=None, engine="cpu")
    result_df = output["data"]
    
    print(f"Result: {len(result_df)} rows, {len(result_df.columns)} columns")
    print(f"Result columns: {result_df.columns}")

if __name__ == "__main__":
    asyncio.run(test_basic())
