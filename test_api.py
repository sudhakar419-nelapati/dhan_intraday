#!/usr/bin/env python3
"""
DHAN API Quick Test Script
Tests API connectivity and displays live data
"""

import os
import sys
from datetime import datetime
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from src.config import (
    API_TIMEOUT_SECONDS, API_RETRY_COUNT, API_RETRY_DELAY_SECONDS
)
from src.provider import DhanAPIProvider


def test_dhan_connection():
    """Test DHAN API connectivity"""
    print("\n" + "="*60)
    print("DHAN API Connection Test")
    print("="*60)
    
    # Load configuration
    print("\n[*] Configuration loaded")
    print(f"    API Timeout: {API_TIMEOUT_SECONDS}s")
    print(f"    Retry Count: {API_RETRY_COUNT}")
    print(f"    Retry Delay: {API_RETRY_DELAY_SECONDS}s")
    
    # Initialize provider
    provider = DhanAPIProvider()
    print("\n[*] DHAN Provider initialized")
    
    # Test connection
    print("\nTesting connection to DHAN API...")
    try:
        result = provider.test_connection()
        if result:
            print("[OK] API Connection: SUCCESS")
        else:
            print("[FAIL] API Connection: FAILED")
            print("\nPlease check:")
            print("  1. DHAN_API_KEY in .env file")
            print("  2. DHAN_CLIENT_ID in .env file")
            print("  3. Internet connectivity")
            return False
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False
    
    return True


def fetch_sample_data():
    """Fetch sample futures data"""
    print("\n" + "="*60)
    print("Fetching Sample Futures Data")
    print("="*60)
    
    provider = DhanAPIProvider()
    
    # Test with RELIANCE futures
    test_symbols = ["RELIANCE", "TCS", "INFY"]
    expiry = "CUR"  # Current expiry
    
    print(f"\nFetching futures candles...")
    
    results = []
    for symbol in test_symbols:
        try:
            print(f"  {symbol}...", end=" ")
            candle = provider.get_futures_candle(symbol, expiry)
            
            if candle:
                results.append({
                    "Symbol": symbol,
                    "Expiry": expiry,
                    "Open": f"Rs {candle.open_price:.2f}",
                    "High": f"Rs {candle.high_price:.2f}",
                    "Low": f"Rs {candle.low_price:.2f}",
                    "Close": f"Rs {candle.close_price:.2f}",
                    "Volume": f"{candle.volume:,}",
                    "OI": f"{candle.oi:,}",
                    "Time": candle.timestamp.strftime("%H:%M:%S"),
                })
                print("[OK]")
            else:
                print("[NO DATA]")
                
        except Exception as e:
            print(f"[ERROR] {str(e)[:50]}")
    
    if results:
        print("\n" + "-"*60)
        print("Sample Futures Data:")
        print("-"*60)
        df = pd.DataFrame(results)
        print(df.to_string(index=False))
        return True
    else:
        print("\n[FAIL] No data fetched. Check:")
        print("  1. API credentials in .env")
        print("  2. Market is open (09:15 - 15:30 IST, Mon-Fri)")
        print("  3. Symbols are valid NSE F&O stocks")
        return False


def fetch_options_data():
    """Fetch sample options chain data"""
    print("\n" + "="*60)
    print("Fetching Sample Options Chain Data")
    print("="*60)
    
    provider = DhanAPIProvider()
    
    test_symbol = "RELIANCE"
    expiry = "CUR"  # Current expiry
    
    print(f"\nFetching options chain for {test_symbol} {expiry}...")
    
    try:
        print(f"  Fetching chain data...", end=" ")
        chain = provider.get_option_chain(test_symbol, expiry)
        
        if chain:
            print("[OK]")
            print("\n" + "-"*60)
            print("Options Chain Data:")
            print("-"*60)
            
            # Sample 1-2 strikes
            if chain.strikes:
                sample_strikes = sorted(chain.strikes)[:3]
                
                options_data = []
                for strike in sample_strikes:
                    if strike in chain.ce_oi:
                        options_data.append({
                            "Type": "CE",
                            "Strike": f"{strike:.0f}",
                            "Volume": f"{chain.ce_volume.get(strike, 0):,.0f}",
                            "OI": f"{chain.ce_oi.get(strike, 0):,.0f}",
                            "IV": f"{chain.ce_iv.get(strike, 0):.4f}",
                        })
                    if strike in chain.pe_oi:
                        options_data.append({
                            "Type": "PE",
                            "Strike": f"{strike:.0f}",
                            "Volume": f"{chain.pe_volume.get(strike, 0):,.0f}",
                            "OI": f"{chain.pe_oi.get(strike, 0):,.0f}",
                            "IV": f"{chain.pe_iv.get(strike, 0):.4f}",
                        })
                
                if options_data:
                    df = pd.DataFrame(options_data)
                    print(df.to_string(index=False))
                    return True
                else:
                    print("No option data available")
                    return False
        else:
            print("[NO DATA]")
            return False
            
    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("=" * 60)
    print(" DHAN API - Quick Test & Data Viewer ".center(60))
    print("=" * 60)
    
    # Check if .env exists
    if not Path(".env").exists():
        print("\n[FAIL] .env file not found!")
        print("\nTo get started:")
        print("  1. Copy .env.example to .env")
        print("  2. Edit .env and add your DHAN credentials:")
        print("     DHAN_API_KEY=your_actual_api_key")
        print("     DHAN_CLIENT_ID=your_actual_client_id")
        print("  3. Run this script again")
        return
    
    # Test connection
    if not test_dhan_connection():
        print("\n[WARNING] Skipping data fetch due to connection failure")
        return
    
    # Fetch data
    fetch_sample_data()
    fetch_options_data()
    
    print("\n" + "="*60)
    print("Next Steps:")
    print("="*60)
    print("""
  1. [OK] API connection verified
  2. Run the full Streamlit dashboard:
     $ streamlit run dashboard.py
  3. View live market data and scanner results
  4. Run tests to verify everything works:
     $ pytest tests/ -v
""")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()
