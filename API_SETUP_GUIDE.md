# DHAN API Setup & Testing Guide

## 🚀 Quick Start (5 minutes)

### Step 1: Configure Your API Credentials

```bash
# Copy the example config
copy .env.example .env
```

**Edit `.env` file and add your DHAN API credentials:**

```env
# Replace these with YOUR actual DHAN credentials
DHAN_API_KEY=your_actual_dhan_api_key_here
DHAN_CLIENT_ID=your_actual_dhan_client_id_here
```

### Step 2: Test API Connection

Run the quick test script to verify your credentials work:

```bash
python test_api.py
```

**Expected output:**
```
════════════════════════════════════════════════════════
DHAN API Connection Test
════════════════════════════════════════════════════════

✓ Configuration loaded
  API Timeout: 10s
  Retry Count: 3
  Retry Delay: 2s

✓ DHAN Provider initialized

Testing connection to DHAN API...
✅ API Connection: SUCCESS
```

### Step 3: View Data in Streamlit

Once the API test passes, run the interactive dashboard:

```bash
streamlit run dashboard.py
```

This opens a web browser at **http://localhost:8501** with:
- 📊 **Market Scanner** - Live stock rankings with STAR gates
- 📈 **Stock Detail** - 5-minute candles, charts, full checklist
- 🔍 **API Test** - Test API connectivity and fetch live data
- 📝 **Logs & Diagnostics** - API call history and system health
- ⚙️ **Settings** - Configure thresholds and test parameters

---

## 🔧 Configuration Details

### Required Settings

| Parameter | Description | Example |
|-----------|-------------|---------|
| `DHAN_API_KEY` | Your DHAN API authentication key | `abc123xyz789` |
| `DHAN_CLIENT_ID` | Your DHAN client/account ID | `D123456789` |

### Optional Settings (Defaults shown)

```env
# Data Location
DB_PATH=./data/scanner.db

# Market Hours (IST)
SESSION_START_TIME=09:15
SESSION_END_TIME=15:30

# Gate Thresholds
PRICE_NOISE_THRESHOLD=0.0001        # Min price change to avoid false signals
VOLUME_RANK_STRONG=100              # Top 100 candles = strong volume
VOLUME_RANK_WARNING=300             # > 300 = weak volume
OI_STRENGTH_STRONG=1.4              # OI > 1.4x baseline = strong
BASELINE_LOOKBACK_SESSIONS=5        # Compare against last 5 sessions

# API Settings
API_TIMEOUT_SECONDS=10              # Timeout per request
API_RETRY_COUNT=3                   # Retries on failure
API_RETRY_DELAY_SECONDS=2           # Wait between retries

# Features
PAPER_MODE=false                    # Set true for testing without live API
LOG_LEVEL=INFO                      # INFO, DEBUG, WARNING
```

---

## 📊 Testing API Data

### Option 1: Quick Test Script (Command Line)

```bash
python test_api.py
```

Shows:
- ✅ API connection status
- 📈 Sample futures data (RELIANCE, TCS, INFY)
- 💰 Sample options chain data (CE & PE)
- 🔍 Data quality checks

### Option 2: Interactive Streamlit Dashboard

```bash
streamlit run dashboard.py
```

Navigate to **API Test** tab to:
- 🔗 Test connection with one click
- 📥 Fetch live data for any symbol
- 📊 View results in tables and charts
- 📝 Check API logs and diagnostics

### Option 3: Manual Python Script

```python
from src.config import Config
from src.provider import DhanProvider

config = Config()
provider = DhanProvider(config)

# Test connection
if provider.test_connection():
    print("✅ Connected!")
    
# Fetch futures candle
candle = provider.get_futures_candle("RELIANCE", "27NOV2026")
print(f"Close: ₹{candle.close}, OI: {candle.oi}, Volume: {candle.volume}")

# Fetch options chain
ce = provider.get_option_chain("RELIANCE", "27NOV2026", 2900, "CE")
pe = provider.get_option_chain("RELIANCE", "27NOV2026", 2900, "PE")
print(f"CE: {ce.close}, PE: {pe.close}")
```

---

## 🐛 Troubleshooting

### ❌ "API Connection: FAILED"

**Check these in order:**

1. **Credentials are correct:**
   ```bash
   # View your .env file
   type .env
   ```
   - Ensure `DHAN_API_KEY` matches exactly what DHAN provided
   - Ensure `DHAN_CLIENT_ID` matches exactly

2. **Dependencies installed:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Internet connectivity:**
   ```bash
   ping google.com
   ```

4. **DHAN API is reachable:**
   ```bash
   curl -X GET https://api.dhan.co/v1/health
   ```

### ❌ "No data returned"

This is **normal** if:
- Market is **closed** (Outside 09:15 - 15:30 IST, Mon-Fri)
- Symbol is **not NSE F&O** (Check on NSE website)
- Expiry date is **incorrect** (Use next Thursday date)

**Solution:** Test during market hours with valid NSE F&O symbols:
- Liquid futures: `RELIANCE`, `TCS`, `INFY`, `HDFC`, `ICICIBANK`
- Check expiry: `27NOV2026` (or next Thursday)

### ❌ "Module not found" error

```bash
# Install dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; import pandas; print('✓ All imports OK')"
```

### ❌ Streamlit not opening in browser

```bash
# Try explicitly setting the port
streamlit run dashboard.py --server.port=8501 --logger.level=debug
```

---

## 📡 API Endpoints Reference

The application uses these DHAN API endpoints:

### Futures Candles
```
GET /v2/marketData/fno/historical/
  Parameters:
    - securityId: "RELIANCE27NOV2026FUT"
    - interval: "5min"
    - fromDate: "2026-11-17"
    - toDate: "2026-11-17"
```

### Options Chain
```
GET /v2/marketData/fno/historical/
  Parameters:
    - securityId: "RELIANCE27NOV2026CE2900"  (for CE)
    - securityId: "RELIANCE27NOV2026PE2900"  (for PE)
    - interval: "5min"
```

### Real-time Market Data
```
GET /v1/marketData/
  Parameters:
    - securityId: "RELIANCE27NOV2026FUT"
```

---

## 🎯 Next Steps

### 1. Verify Setup Works
```bash
# Should see ✅ Connection successful
python test_api.py
```

### 2. Run Full Test Suite
```bash
# Should see 52/52 tests passing
pytest tests/ -v
```

### 3. Launch Dashboard
```bash
# Open http://localhost:8501 in browser
streamlit run dashboard.py
```

### 4. Monitor Scanner
- Refresh Market Scanner every 5 minutes
- Select stocks to view detailed candles & gates
- Check API Logs tab for any errors

---

## 📞 Support

If you encounter issues:

1. **Check logs:** 
   ```bash
   tail -f ./logs/scanner.log
   ```

2. **Enable debug mode:**
   ```env
   LOG_LEVEL=DEBUG
   ```

3. **Verify DHAN API status:**
   - Visit DHAN website for API documentation
   - Contact DHAN support with your API key

4. **Check market hours:**
   - NSE F&O operates: 09:15 - 15:30 IST
   - Monday through Friday (except holidays)

---

## 💡 Tips

- **Paper Mode Testing:** Set `PAPER_MODE=true` in `.env` to use mock data
- **Multiple Symbols:** Use comma-separated list in `UNIVERSE_SYMBOLS`
- **Fast Testing:** Use `API_TIMEOUT_SECONDS=5` during testing
- **Debug Output:** Use `streamlit run dashboard.py --logger.level=debug`

---

**Happy testing! 🚀**
