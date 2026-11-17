# 🚀 DHAN API Integration - Quick Start

You have your DHAN API access token. Here's exactly how to use it with the STAR Trading Scanner:

---

## ⚡ 3-Step Setup (5 minutes)

### Step 1️⃣: Configure Your API Credentials

```bash
# Open .env file in an editor
notepad .env
```

**Replace these two lines with YOUR credentials:**
```env
DHAN_API_KEY=your_actual_dhan_api_key_here
DHAN_CLIENT_ID=your_actual_dhan_client_id_here
```

**Where to find these:**
- **API Key**: From DHAN dashboard > Settings > API Credentials
- **Client ID**: From DHAN dashboard > Settings > Account Info

### Step 2️⃣: Test API Connection

```bash
# Quick test from command line
python test_api.py
```

**Expected output:**
```
════════════════════════════════════════════════════════
DHAN API - Quick Test & Data Viewer
════════════════════════════════════════════════════════

✅ API Connection: SUCCESS

Sample Futures Data:
Symbol        Close        Volume    OI
RELIANCE      ₹2,750.50    125,000   15,00,000
TCS           ₹3,420.25    85,000    8,50,000
INFY          ₹2,890.75    95,000    9,20,000
```

### Step 3️⃣: View Data in Streamlit

```bash
# Start the interactive dashboard
streamlit run dashboard.py
```

Browser opens at: **http://localhost:8501**

---

## 📊 Using the Dashboard

### Tab 1: **API Test** ← START HERE!
1. Click **"🧪 Test Connection"** button
2. See ✅ if API works, or ❌ if credentials wrong
3. Enter symbol (e.g., `RELIANCE`) and expiry (e.g., `27NOV2026`)
4. Click **"📥 Fetch Futures Candle"** to see live data
5. Click **"📥 Fetch Options"** to see call/put data

### Tab 2: **Market Scanner**
- Shows all NSE F&O stocks ranked by STAR gates
- Filter by direction (UP/DOWN/FLAT)
- Click stock name to view details

### Tab 3: **Stock Detail**
- 5-minute candles table
- Price & volume charts
- Full 8-gate checklist status
- Session accumulation (Gate 8)

### Tab 4: **Logs & Diagnostics**
- API call history
- System health check
- Database size

### Tab 5: **Settings**
- Configure gate thresholds
- API retry settings
- Feature toggles

---

## 🔍 Sample Data Flow

Here's what happens when you fetch data:

```
1. You click "Fetch Futures Candle"
           ↓
2. App sends: GET /v2/marketData/fno/historical/
   With: symbol=RELIANCE27NOV2026FUT, interval=5min
           ↓
3. DHAN API returns JSON:
   {
     "open": 2750.50,
     "high": 2755.00,
     "low": 2745.75,
     "close": 2752.25,
     "volume": 125000,
     "oi": 15000000,
     "timestamp": "2026-11-17T10:30:00"
   }
           ↓
4. App stores in SQLite database
           ↓
5. Dashboard displays in table & charts
```

---

## 🎯 Symbols You Can Test

**Highly Liquid NSE F&O Futures** (guaranteed to have data):
```
RELIANCE    TCS         INFY        HDFC
ICICIBANK   AXISBANK    LT          WIPRO
MARUTI      BAJAJFINSV  SBILIFE     SUNPHARMA
INDIGO      APOLLOHOSP  ONGC        COALINDIA
BHARTIARTL  POWERGRID   JSWSTEEL    TATASTEEL
```

**Expiry Dates** (use next Thursday):
```
27NOV2026   04DEC2026   25DEC2026   30JAN2027
```

**Strike Prices** (for options):
```
RELIANCE:  2750, 2800, 2850, 2900, 2950
TCS:       3300, 3400, 3500, 3600, 3700
INFY:      2800, 2850, 2900, 2950, 3000
```

---

## ✅ Verification Checklist

After setup, verify everything works:

```bash
# 1. Check .env file has credentials
grep -E "DHAN_API_KEY|DHAN_CLIENT_ID" .env

# 2. Install dependencies (if not already done)
pip install -r requirements.txt

# 3. Run quick test
python test_api.py

# 4. Run full test suite (should see 52/52 passing)
pytest tests/ -v

# 5. Start dashboard
streamlit run dashboard.py
```

---

## 🐛 Troubleshooting

### ❌ "API Connection: FAILED"

**Check in this order:**

1. **Credentials typo?**
   ```bash
   # View your .env file
   type .env
   ```

2. **API Key format?**
   - Should be a long alphanumeric string
   - No spaces before/after
   - No quotes around the value

3. **Internet working?**
   ```bash
   ping google.com
   ```

4. **DHAN API status?**
   - Visit https://dhan.co to check if API is up
   - Try accessing from DHAN documentation page

### ❌ "No data returned"

This is **normal** if:
- **Market closed**: Outside 09:15 - 15:30 IST, Mon-Fri
- **Wrong symbol**: Not a NSE F&O stock (check NSE website)
- **Wrong expiry**: Date doesn't exist (use next Thursday)

**Solution**: Test during market hours (Mon-Fri, 09:15-15:30 IST)

### ❌ "Module not found" error

```bash
# Install missing dependencies
pip install -r requirements.txt

# Verify installation
python -c "import streamlit; print('✓ OK')"
```

### ❌ Streamlit won't open in browser

```bash
# Try explicit port and debug
streamlit run dashboard.py --server.port=8501 --logger.level=debug

# Should see: http://localhost:8501
```

---

## 📡 Data You'll See

### Futures Candle Data
```json
{
  "open": 2750.50,
  "high": 2755.00,
  "low": 2745.75,
  "close": 2752.25,
  "volume": 125000,
  "oi": 15000000,
  "timestamp": "2026-11-17T10:30:00",
  "expiry": "27NOV2026"
}
```

### Options Chain Data
```json
{
  "CE_close": 85.50,
  "CE_volume": 50000,
  "CE_oi": 2500000,
  "PE_close": 42.25,
  "PE_volume": 45000,
  "PE_oi": 2300000
}
```

### Gate Calculations
```
Gate 1: OI Wall           → ✅ PASS / ❌ FAIL
Gate 2: Strike GEX        → ✅ PASS / ❌ FAIL
Gate 3: Seller Neutral    → ✅ PASS / ❌ FAIL
Gate 4: Seller Exit       → ✅ PASS / ❌ FAIL
Gate 5: Writing Activity  → ✅ PASS / ❌ FAIL
Gate 6: Buying Activity   → ✅ PASS / ❌ FAIL
Gate 7: Futures Read      → UP/DOWN/FLAT + Strength
Gate 8: Neutralization    → BULL/BEAR/NEUTRAL + Lead
```

---

## 🎓 Understanding the Gates

The STAR scanner uses **8 gates** to decide if a stock is ready to trade:

| Gate | What It Checks | Good Sign |
|------|---|---|
| **1-6** | Options chain structure | ATM calls/puts have volume & OI |
| **7** | Futures direction & strength | UP move with rising OI & volume |
| **8** | Session accumulation | Bull lead (more buying than selling) |

**Readiness Decision:**
- **8/8 gates pass** → Full position quantity
- **6-7 gates pass** → Half position quantity
- **4-5 gates pass** → Wait for setup
- **<4 gates pass** → Stay out (no trade)

---

## 💡 Tips & Tricks

### Speed Up Testing
```env
API_TIMEOUT_SECONDS=5           # Faster timeouts
API_RETRY_COUNT=1               # No retries (faster)
MAX_CONCURRENT_SYMBOLS=10       # Fetch more at once
```

### Debug Problems
```env
LOG_LEVEL=DEBUG                 # More detailed logs
PAPER_MODE=true                 # Use mock data (no API)
```

### Paper Mode (Test without API)
```env
PAPER_MODE=true
```
Then run:
```bash
streamlit run dashboard.py
```
Now you can test UI without needing live API data!

### View Application Logs
```bash
# Real-time log monitoring
tail -f ./logs/scanner.log

# Or on Windows PowerShell
Get-Content ./logs/scanner.log -Wait
```

---

## 📞 Getting Help

If you're stuck:

1. **Check logs:**
   ```bash
   type .\logs\scanner.log
   ```

2. **Run diagnostic:**
   ```bash
   python test_api.py
   ```

3. **Enable debug mode:**
   ```env
   LOG_LEVEL=DEBUG
   ```
   Then run: `python test_api.py` again

4. **Contact DHAN support:**
   - Verify API key with DHAN team
   - Confirm API endpoints and rates
   - Check if account has historical data access

---

## 🚀 Next Steps

1. ✅ Configure `.env` with your API credentials
2. ✅ Run `python test_api.py` to verify connection
3. ✅ Run `streamlit run dashboard.py` to see data
4. ✅ Click **API Test** tab to fetch live data
5. ✅ Monitor **Stock Detail** to see gate calculations
6. ✅ Check **Market Scanner** for all stocks

---

**Happy trading! 📈**

Questions? See full documentation in [API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md)
