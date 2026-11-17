"""Streamlit dashboard for STAR Trading Scanner (run from the project root: streamlit run dashboard.py)."""
import os
from datetime import datetime

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="STAR Trading Scanner", page_icon="📊", layout="wide",
                   initial_sidebar_state="expanded")

# Cloud secrets -> environment (before config is read)
try:
    for k in ("DHAN_CLIENT_ID", "DHAN_ACCESS_TOKEN"):
        if k in st.secrets:
            os.environ[k] = str(st.secrets[k])
except Exception:
    pass

from src.baselines import BaselineCalculator
from src.config import UNIVERSE_SYMBOLS, get_client_id, get_token
from src.gates import Gate7Calculator, Gate8Calculator, GatesCalculator
from src.provider import DhanAPIProvider


@st.cache_resource
def provider() -> DhanAPIProvider:
    return DhanAPIProvider()


@st.cache_data(ttl=60, show_spinner=False)
def load_candles(symbol: str, token_tag: str):
    """Candles for the last ~7 days. token_tag only forces a reload when the token changes."""
    return provider().get_historical_candles(symbol, days_back=7)


def analyse(symbol: str, candles, volume_rank: int):
    """Gate 7 (last candle) and Gate 8 (today) for one symbol, plus CE/PE checklists."""
    if len(candles) < 2:
        return None
    today = candles[-1].timestamp.date()
    session = [c for c in candles if c.timestamp.date() == today]
    vol_base, _ = BaselineCalculator.calculate_volume_baseline(candles)
    oi_base, _ = BaselineCalculator.calculate_oi_strength_baseline(candles)
    prev = session[-2] if len(session) >= 2 else None
    g7 = Gate7Calculator.calculate(candles[-1], prev, vol_base, oi_base, volume_rank)
    g8 = Gate8Calculator.accumulate_session(session)
    ce = GatesCalculator.evaluate_all_gates(g7, g8, None, "CE")
    pe = GatesCalculator.evaluate_all_gates(g7, g8, None, "PE")
    return g7, g8, ce, pe, len(session)


def scanner_page(symbols):
    st.header("Market Scanner")
    c1, c2 = st.columns([3, 1])
    min_pass = c1.slider("Show only symbols where at least one side passes this many built gates", 0, 2, 1)
    if c2.button("🔄 Refresh"):
        st.cache_data.clear()
    if not (get_token() and get_client_id()):
        st.warning("Add your Dhan client id and access token in the sidebar first.")
        return

    tag, rows, vols, data = get_token()[-6:], [], {}, {}
    bar = st.progress(0.0, text="Loading candles...")
    for i, sym in enumerate(symbols):
        data[sym] = load_candles(sym, tag)
        if data[sym]:
            vols[sym] = data[sym][-1].volume
        bar.progress((i + 1) / len(symbols), text=f"Loaded {sym}")
    bar.empty()
    ranked = sorted(vols, key=vols.get, reverse=True)

    problems = [s for s in symbols if not data[s]]
    for sym in symbols:
        res = analyse(sym, data[sym], ranked.index(sym) + 1 if sym in ranked else 999) if data[sym] else None
        if not res:
            continue
        g7, g8, ce, pe, n = res
        best = max(ce.pass_count, pe.pass_count)
        if best < min_pass:
            continue
        rows.append({
            "Symbol": sym, "Candle": g7.candle_timestamp.strftime("%H:%M"),
            "Gate 7": g7.direction_label, "Chg %": g7.price_change_percent,
            "OI x": g7.oi_strength, "Vol x": g7.volume_strength, "Vol rank": g7.volume_rank,
            "Gate 8": f"{g8.lead_label} ({g8.net_lead:+,.0f})",
            "CE": f"{ce.pass_count}/2 {ce.readiness_status}",
            "PE": f"{pe.pass_count}/2 {pe.readiness_status}",
            "Candles": n,
        })
    if rows:
        st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    else:
        st.info("No symbol meets the filter right now.")
    if problems:
        st.error(f"No data for: {', '.join(problems)}. Last API error: {provider().last_error}")
    st.caption("Only Gates 7 and 8 (from futures candles) are built. Gates 1-6 need option-chain logic "
               "and are shown as not built, not as passed. 'Vol x' and 'OI x' compare with the same "
               "5-minute slot over the previous sessions; 'Vol rank' is among the symbols listed here.")


def detail_page(symbols):
    st.header("Stock Detail")
    sym = st.selectbox("Symbol", symbols)
    candles = load_candles(sym, get_token()[-6:]) if get_token() else []
    if not candles:
        st.info(f"No candle data. {provider().last_error or ''}")
        return
    today = candles[-1].timestamp.date()
    df = pd.DataFrame([{"Time": c.timestamp, "Open": c.open_price, "High": c.high_price,
                        "Low": c.low_price, "Close": c.close_price, "Volume": c.volume, "OI": c.oi}
                       for c in candles if c.timestamp.date() == today])
    df["OI change"] = df["OI"].diff()
    fig = go.Figure(go.Candlestick(x=df["Time"], open=df["Open"], high=df["High"],
                                   low=df["Low"], close=df["Close"]))
    fig.update_layout(height=380, xaxis_rangeslider_visible=False, margin=dict(t=10, b=10))
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(df.iloc[::-1], use_container_width=True, hide_index=True)


def api_page(symbols):
    st.header("API Test")
    if st.button("Test connection"):
        ok = provider().test_connection()
        st.success("Connected") if ok else st.error(f"Failed: {provider().last_error}")
    sym = st.selectbox("Symbol", symbols, key="t_sym")
    if st.button("Fetch latest futures candle"):
        c = provider().get_futures_candle(sym)
        if c:
            st.json({"time": str(c.timestamp), "open": c.open_price, "high": c.high_price,
                     "low": c.low_price, "close": c.close_price, "volume": c.volume, "oi": c.oi})
        else:
            st.warning(f"No data. {provider().last_error or ''}")
    if st.button("Fetch option chain"):
        ch = provider().get_option_chain(sym)
        if ch:
            st.write(f"{len(ch.strikes)} strikes, spot {ch.underlying_price}")
        else:
            st.warning(f"No data. {provider().last_error or ''}")


def main():
    with st.sidebar:
        st.subheader("Dhan credentials")
        cid = st.text_input("Client id", value=get_client_id())
        tok = st.text_input("Access token", type="password", value="")
        if cid:
            os.environ["DHAN_CLIENT_ID"] = cid
        if tok:
            os.environ["DHAN_ACCESS_TOKEN"] = tok
        st.caption("Token loaded" if get_token() else "No token yet")
        st.markdown("---")
        page = st.radio("Navigation", ["Market Scanner", "Stock Detail", "API Test"])
        raw = st.text_area("Symbols (comma separated)", ",".join(UNIVERSE_SYMBOLS))
    symbols = [s.strip().upper() for s in raw.split(",") if s.strip()]
    st.title("📊 STAR Trading Scanner")
    {"Market Scanner": scanner_page, "Stock Detail": detail_page, "API Test": api_page}[page](symbols)


main()
