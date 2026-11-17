#!/usr/bin/env python3
"""
DHAN API Quick Test Script
Tests API connectivity and displays live data
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from config import Config
from provider import DhanProvider
import pandas as pd


def test_dhan_connection():
    """Test DHAN API connectivity"""
    print("\n" + "="*60)
    print("DHAN API Connection Test")
    print("="*60)
    
    # Load configuration
    config = Config()
    print(f"\n✓ Configuration loaded")
    print(f"  API Timeout: {config.api_timeout_seconds}s")
    print(f"  Retry Count: {config.api_retry_count}")
    print(f"  Retry Delay: {config.api_retry_delay_seconds}s")
    
    # Initialize provider
    provider = DhanProvider(config)
    print(f"\n✓ DHAN Provider initialized")
    
    # Test connection
    print(f"\nTesting connection to DHAN API...")
    try:
        result = provider.test_connection()
        if result:
            print(f"✅ API Connection: SUCCESS")
        else:
            print(f"❌ API Connection: FAILED")
            print(f"\nPlease check:")
            print(f"  1. DHAN_API_KEY in .env file")
            print(f"  2. DHAN_CLIENT_ID in .env file")
            print(f"  3. Internet connectivity")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True


def fetch_sample_data():
    """Fetch sample futures data"""
    print("\n" + "="*60)
    print("Fetching Sample Futures Data")
    print("="*60)
    
    config = Config()
    provider = DhanProvider(config)
    
    # Test with RELIANCE futures
    test_symbols = ["RELIANCE", "TCS", "INFY"]
    expiry = "27NOV2026"  # Update based on current market
    
    print(f"\nFetching 5-minute candles for {expiry}...")
    
    results = []
    for symbol in test_symbols:
        try:
            print(f"\n  {symbol}...", end=" ")
            candle = provider.get_futures_candle(symbol, expiry)
            
            if candle:
                results.append({
                    "Symbol": symbol,
                    "Expiry": expiry,
                    "Open": f"₹{candle.open:.2f}",
                    "High": f"₹{candle.high:.2f}",
                    "Low": f"₹{candle.low:.2f}",
                    "Close": f"₹{candle.close:.2f}",
                    "Volume": f"{candle.volume:,}",
                    "OI": f"{candle.oi:,}",
                    "Time": candle.timestamp.strftime("%H:%M:%S"),
                })
                print("✓")
            else:
                print("✗ (No data)")
                
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
    
    if results:
        print("\n" + "-"*60)
        print("Sample Futures Data:")
        print("-"*60)
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        return True
    else:
        print("\n❌ No data fetched. Check:")
        print("  1. API credentials in .env")
        print("  2. Market is open (09:15 - 15:30 IST, Mon-Fri)")
        print("  3. Symbols are valid NSE F&O stocks")
        return False


def fetch_options_data():
    """Fetch sample options chain data"""
    print("\n" + "="*60)
    print("Fetching Sample Options Chain Data")
    print("="*60)
    
    config = Config()
    provider = DhanProvider(config)
    
    test_symbol = "RELIANCE"
    expiry = "27NOV2026"  # Update based on current market
    strike = 2900  # Sample strike
    
    print(f"\nFetching options chain for {test_symbol} {expiry}...")
    
    try:
        print(f"\n  CE (Call) {strike}...", end=" ")
        ce_option = provider.get_option_chain(test_symbol, expiry, strike, "CE")
        
        print(f"\n  PE (Put) {strike}...", end=" ")
        pe_option = provider.get_option_chain(test_symbol, expiry, strike, "PE")
        
        if ce_option and pe_option:
            print("\n\n" + "-"*60)
            print("Options Chain Data:")
            print("-"*60)
            
            options_data = [
                {
                    "Type": "CE (Call)",
                    "Strike": strike,
                    "Open": f"₹{ce_option.open:.2f}",
                    "High": f"₹{ce_option.high:.2f}",
                    "Low": f"₹{ce_option.low:.2f}",
                    "Close": f"₹{ce_option.close:.2f}",
                    "Volume": f"{ce_option.volume:,}",
                    "OI": f"{ce_option.oi:,}",
                },
                {
                    "Type": "PE (Put)",
                    "Strike": strike,
                    "Open": f"₹{pe_option.open:.2f}",
                    "High": f"₹{pe_option.high:.2f}",
                    "Low": f"₹{pe_option.low:.2f}",
                    "Close": f"₹{pe_option.close:.2f}",
                    "Volume": f"{pe_option.volume:,}",
                    "OI": f"{pe_option.oi:,}",
                }
            ]
            df = pd.DataFrame(options_data)
            print(df.to_string(index=False))
            return True
        else:
            print("✗ (No data)")
            return False
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═"*58 + "╗")
    print("║" + " DHAN API - Quick Test & Data Viewer ".center(58) + "║")
    print("╚" + "═"*58 + "╝")
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n❌ ERROR: .env file not found!")
        print("\nTo get started:")
        print("  1. Copy .env.example to .env")
        print("     $ copy .env.example .env")
        print("\n  2. Edit .env and add your DHAN credentials:")
        print("     DHAN_API_KEY=your_actual_api_key")
        print("     DHAN_CLIENT_ID=your_actual_client_id")
        print("\n  3. Run this script again")
        return
    
    # Test connection
    if not test_dhan_connection():
        print("\n⚠️  Skipping data fetch due to connection failure")
        return
    
    # Fetch data
    fetch_sample_data()
    fetch_options_data()
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("""
  1. ✓ API connection verified
  2. Run the full Streamlit dashboard:
     $ streamlit run dashboard.py
  3. View live market data and scanner results
  4. Run tests to verify everything works:
     $ pytest tests/ -v
""")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
