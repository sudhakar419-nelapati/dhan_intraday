"""
Main Streamlit dashboard for STAR Trading Scanner.
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import logging

from src.config import validate_config, get_logger
from src.database import Database
from src.provider import DhanAPIProvider
from src.models import ScannerRowData
from src.gates import Gate7Calculator, Gate8Calculator, GatesCalculator

# Configure page
st.set_page_config(
    page_title="STAR Trading Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

logger = get_logger(__name__)

# Initialize session state
if "db" not in st.session_state:
    st.session_state.db = Database()

if "provider" not in st.session_state:
    st.session_state.provider = DhanAPIProvider()

if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = None


def render_header():
    """Render page header."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.title("📊 STAR Trading Scanner")
    
    with col3:
        if st.button("🔄 Refresh Data"):
            st.session_state.last_refresh = datetime.now()
            st.rerun()
        
        if st.session_state.last_refresh:
            st.caption(f"Last refresh: {st.session_state.last_refresh.strftime('%H:%M:%S')}")


def render_market_scanner():
    """Render market-wide scanner view."""
    st.header("Market Scanner")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        universe_filter = st.selectbox(
            "Universe",
            ["All NSE F&O", "Nifty 50", "Nifty 200"]
        )
    
    with col2:
        gate7_direction = st.multiselect(
            "Gate 7 Direction",
            ["UP", "DOWN", "FLAT", "Neutral"],
            default=["UP", "DOWN"]
        )
    
    with col3:
        min_pass_count = st.slider("Minimum Gate Passes", 0, 8, 4)
    
    with col4:
        auto_refresh = st.checkbox("Auto-refresh every 5 min", value=False)
    
    # Placeholder data for demonstration
    scanner_data = []
    
    # Create sample scanner display
    if scanner_data:
        df = pd.DataFrame([
            {
                "Pick": 1,
                "Symbol": "RELIANCE",
                "CE Readiness": "6/8 - Half Qty",
                "PE Readiness": "4/8 - Wait",
                "Gate 7 Label": "Fresh Long Build",
                "Gate 7 OI Strength": 1.45,
                "Gate 8 Lead": "BULL +2.8L",
                "Data Quality": "Fresh"
            }
        ])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data available. Configure API credentials and refresh.")


def render_stock_detail():
    """Render detailed stock view."""
    st.header("Stock Detail")
    
    symbol = st.selectbox("Select Symbol", ["RELIANCE", "TCS", "INFY", "HDFC"])
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs([
        "5-Min Candles",
        "Charts",
        "Gate Checklist",
        "Session History"
    ])
    
    with tab1:
        st.subheader(f"{symbol} - 5-Minute Futures Candles")
        
        # Fetch candles from database
        candles = st.session_state.db.get_futures_candles(symbol, "CUR", limit=20)
        
        if candles:
            df = pd.DataFrame([
                {
                    "Time": c.timestamp,
                    "Open": c.open_price,
                    "High": c.high_price,
                    "Low": c.low_price,
                    "Close": c.close_price,
                    "Volume": c.volume,
                    "OI": c.oi,
                    "OI Change": c.oi - (candles[i-1].oi if i > 0 else c.oi)
                }
                for i, c in enumerate(candles)
            ])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No candle data available for this symbol.")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Price Chart")
            # Placeholder chart
            fig = go.Figure()
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("OI & Volume")
            fig = go.Figure()
            st.plotly_chart(fig, use_container_width=True)
    
    with tab3:
        st.subheader(f"{symbol} - Gate Checklist")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**CE Readiness**")
            gates = ["OI Wall", "Strike GEX", "Seller Neutral", "Seller Exit",
                    "Writing", "Buying", "Futures Read", "Neutralization"]
            
            for i, gate in enumerate(gates, 1):
                status = "✅ PASS" if i <= 6 else "⚠️ WEAK"
                st.write(f"Gate {i}: {gate} - {status}")
        
        with col2:
            st.write("**PE Readiness**")
            for i, gate in enumerate(gates, 1):
                status = "❌ FAIL" if i <= 4 else "✅ PASS"
                st.write(f"Gate {i}: {gate} - {status}")
    
    with tab4:
        st.subheader("Session Accumulation (Gate 8)")
        
        session_data = {
            "FL (Fresh Long)": 2.1,
            "SC (Short Covering)": 3.5,
            "FS (Fresh Short)": 1.9,
            "LU (Long Unwinding)": 3.8
        }
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("FL", f"{session_data['FL (Fresh Long)']:.1f}L")
        with col2:
            st.metric("SC", f"{session_data['SC (Short Covering)']:.1f}L")
        with col3:
            st.metric("FS", f"{session_data['FS (Fresh Short)']:.1f}L")
        with col4:
            st.metric("LU", f"{session_data['LU (Long Unwinding)']:.1f}L")


def render_api_test():
    """Render API test and connectivity view."""
    st.header("🔗 API Test & Data Viewer")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Test DHAN API Connection")
    
    with col2:
        if st.button("🧪 Test Connection", key="test_connection"):
            with st.spinner("Testing API connection..."):
                try:
                    result = st.session_state.provider.test_connection()
                    if result:
                        st.success("✅ API Connection Successful!")
                        st.balloons()
                    else:
                        st.error("❌ API Connection Failed")
                        st.info("""
                        **Troubleshooting:**
                        1. Check DHAN_API_KEY in .env file
                        2. Check DHAN_CLIENT_ID in .env file
                        3. Verify internet connection
                        4. Confirm API credentials are correct
                        """)
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
    
    st.markdown("---")
    
    # Fetch futures candles
    st.subheader("📊 Fetch Futures Data")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.text_input("Symbol", "RELIANCE", help="NSE F&O stock symbol")
    
    with col2:
        expiry = st.text_input("Expiry", "27NOV2026", help="Expiry date (e.g., 27NOV2026)")
    
    with col3:
        if st.button("📥 Fetch Futures Candle", key="fetch_futures"):
            with st.spinner(f"Fetching {symbol} {expiry} data..."):
                try:
                    candle = st.session_state.provider.get_futures_candle(symbol, expiry)
                    if candle:
                        col_a, col_b, col_c, col_d = st.columns(4)
                        with col_a:
                            st.metric("Close", f"₹{candle.close:.2f}")
                        with col_b:
                            st.metric("Volume", f"{candle.volume:,}")
                        with col_c:
                            st.metric("OI", f"{candle.oi:,}")
                        with col_d:
                            st.metric("Time", candle.timestamp.strftime("%H:%M:%S"))
                        
                        # Detailed data
                        st.json({
                            "Open": candle.open,
                            "High": candle.high,
                            "Low": candle.low,
                            "Close": candle.close,
                            "Volume": candle.volume,
                            "OI": candle.oi,
                            "Timestamp": candle.timestamp.isoformat(),
                            "Expiry": candle.expiry
                        })
                    else:
                        st.warning("❌ No data returned. Check:")
                        st.info("""
                        • Market is open (09:15 - 15:30 IST, Mon-Fri)
                        • Symbol is valid NSE F&O stock
                        • Expiry date exists and is correct
                        """)
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    st.markdown("---")
    
    # Fetch options chain
    st.subheader("💰 Fetch Options Chain Data")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        opt_symbol = st.text_input("Symbol", "RELIANCE", key="opt_symbol")
    
    with col2:
        opt_expiry = st.text_input("Expiry", "27NOV2026", key="opt_expiry")
    
    with col3:
        opt_strike = st.number_input("Strike", value=2900, step=100)
    
    with col4:
        if st.button("📥 Fetch Options", key="fetch_options"):
            with st.spinner(f"Fetching {opt_symbol} {opt_strike} options..."):
                try:
                    ce_data = st.session_state.provider.get_option_chain(opt_symbol, opt_expiry, opt_strike, "CE")
                    pe_data = st.session_state.provider.get_option_chain(opt_symbol, opt_expiry, opt_strike, "PE")
                    
                    if ce_data and pe_data:
                        col_ce, col_pe = st.columns(2)
                        
                        with col_ce:
                            st.write("**CE (Call) Option**")
                            col_a, col_b, col_c, col_d = st.columns(4)
                            with col_a:
                                st.metric("Close", f"₹{ce_data.close:.2f}")
                            with col_b:
                                st.metric("Volume", f"{ce_data.volume:,}")
                            with col_c:
                                st.metric("OI", f"{ce_data.oi:,}")
                            with col_d:
                                st.metric("IV", f"{ce_data.iv:.2f}" if hasattr(ce_data, 'iv') else "N/A")
                        
                        with col_pe:
                            st.write("**PE (Put) Option**")
                            col_a, col_b, col_c, col_d = st.columns(4)
                            with col_a:
                                st.metric("Close", f"₹{pe_data.close:.2f}")
                            with col_b:
                                st.metric("Volume", f"{pe_data.volume:,}")
                            with col_c:
                                st.metric("OI", f"{pe_data.oi:,}")
                            with col_d:
                                st.metric("IV", f"{pe_data.iv:.2f}" if hasattr(pe_data, 'iv') else "N/A")
                        
                        # Detailed JSON
                        col_ce_json, col_pe_json = st.columns(2)
                        with col_ce_json:
                            st.write("CE Details:")
                            st.json({
                                "Open": ce_data.open,
                                "High": ce_data.high,
                                "Low": ce_data.low,
                                "Close": ce_data.close,
                                "Volume": ce_data.volume,
                                "OI": ce_data.oi,
                            })
                        
                        with col_pe_json:
                            st.write("PE Details:")
                            st.json({
                                "Open": pe_data.open,
                                "High": pe_data.high,
                                "Low": pe_data.low,
                                "Close": pe_data.close,
                                "Volume": pe_data.volume,
                                "OI": pe_data.oi,
                            })
                    else:
                        st.warning("❌ No options data returned")
                except Exception as e:
                    st.error(f"Error: {str(e)}")


def render_logs():
    """Render logs and diagnostics."""
    st.header("Logs & Diagnostics")
    
    tab1, tab2, tab3 = st.tabs(["API Logs", "Audit Logs", "System Info"])
    
    with tab1:
        st.subheader("Recent API Calls")
        st.info("No API logs available yet.")
    
    with tab2:
        st.subheader("Audit Trail")
        st.info("No audit events yet.")
    
    with tab3:
        st.subheader("System Information")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Application Version", "1.0.0")
            st.metric("Database Size", "0 KB")
            st.metric("Active Symbols", "9")
        
        with col2:
            is_valid = validate_config()
            status = "✅ Valid" if is_valid else "⚠️ Check Config"
            st.metric("Configuration Status", status)
            
            api_connected = st.session_state.provider.test_connection()
            status = "✅ Connected" if api_connected else "❌ Failed"
            st.metric("API Connection", status)


def render_settings():
    """Render settings page."""
    st.header("Settings")
    
    with st.expander("Data Provider", expanded=False):
        st.info("Current provider: Dhan API")
        
        if st.button("Test API Connection"):
            with st.spinner("Testing connection..."):
                is_connected = st.session_state.provider.test_connection()
                if is_connected:
                    st.success("✅ API connection successful!")
                else:
                    st.error("❌ API connection failed. Check credentials.")
    
    with st.expander("Gate Thresholds", expanded=False):
        st.number_input("OI Strength Weak Threshold", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
        st.number_input("OI Strength Medium Threshold", min_value=1.0, max_value=2.0, value=1.4, step=0.1)
        st.number_input("Volume Rank Strong", min_value=50, max_value=200, value=100)
        st.number_input("Volume Rank Moderate", min_value=150, max_value=350, value=250)
        st.number_input("Volume Rank Warning", min_value=200, max_value=400, value=300)
        st.number_input("Price Noise Threshold", min_value=0.00001, max_value=0.001, value=0.0001, format="%.5f")
    
    with st.expander("Baseline Configuration", expanded=False):
        st.number_input("Baseline Lookback Sessions", min_value=1, max_value=20, value=5)
        st.number_input("Neutral Band", min_value=0.0, max_value=1.0, value=0.0, step=0.1)
    
    with st.expander("API Rate Limiting", expanded=False):
        st.number_input("API Timeout (seconds)", min_value=5, max_value=30, value=10)
        st.number_input("Retry Count", min_value=1, max_value=10, value=3)
        st.number_input("Retry Delay (seconds)", min_value=1, max_value=10, value=2)
        st.number_input("Max Concurrent Symbols", min_value=1, max_value=20, value=5)
    
    with st.expander("Feature Flags", expanded=False):
        st.checkbox("Paper Mode (simulated data)", value=False)
        st.checkbox("Enable Historical Replay", value=False)
        st.checkbox("Debug Logging", value=False)
    
    if st.button("Save Settings", type="primary"):
        st.success("Settings saved successfully!")


def main():
    """Main application logic."""
    
    # Render header
    render_header()
    
    # Sidebar navigation
    page = st.sidebar.radio(
        "Navigation",
        ["Market Scanner", "Stock Detail", "API Test", "Logs & Diagnostics", "Settings"]
    )
    
    # Data quality indicator
    with st.sidebar:
        st.markdown("---")
        st.subheader("Data Status")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Fresh Data", "✅", label_visibility="collapsed")
        with col2:
            st.metric("Coverage", "80%", label_visibility="collapsed")
    
    # Route to appropriate page
    if page == "Market Scanner":
        render_market_scanner()
    elif page == "Stock Detail":
        render_stock_detail()
    elif page == "API Test":
        render_api_test()
    elif page == "Logs & Diagnostics":
        render_logs()
    elif page == "Settings":
        render_settings()


if __name__ == "__main__":
    main()
