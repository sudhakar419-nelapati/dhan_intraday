# 📋 DHAN API - Quick Reference Card

Print this page or bookmark it!

---

## ⚡ 3-Step Setup (5 Minutes)

| Step | Command | What It Does |
|------|---------|---|
| 1️⃣ | `copy .env.example .env` | Create config file |
| 2️⃣ | Edit `.env` with your API key & ID | Add your DHAN credentials |
| 3️⃣ | `python test_api.py` | Test connection |

---

## 🎯 Launch Commands

```bash
# Test API connection (command line)
python test_api.py

# Launch interactive dashboard (opens browser)
streamlit run dashboard.py

# Run all tests (verify everything works)
pytest tests/ -v

# View logs
type .\logs\scanner.log

# Enable debug mode
# (Edit .env: LOG_LEVEL=DEBUG)
```

---

## 📊 Dashboard Tabs

| Tab | Purpose | Key Action |
|-----|---------|---|
| **API Test** | Verify & fetch data | Click "Test Connection" button |
| **Market Scanner** | View all stocks | Shows STAR gate ranks |
| **Stock Detail** | Analyze one stock | View 5-min candles & gates |
| **Logs & Diagnostics** | Monitor health | Check API calls & errors |
| **Settings** | Configure parameters | Adjust thresholds |

---

## 🔧 Configuration Quick Reference

### **Required** (.env)
```env
DHAN_API_KEY=your_actual_key_here
DHAN_CLIENT_ID=your_actual_id_here
```

### **Common Options** (.env)
```env
# API settings
API_TIMEOUT_SECONDS=10          # Timeout per request
API_RETRY_COUNT=3               # Retries on failure

# Market hours (IST)
SESSION_START_TIME=09:15
SESSION_END_TIME=15:30

# Gate thresholds
OI_STRENGTH_STRONG=1.4          # OI > 1.4x baseline = strong
VOLUME_RANK_WARNING=300         # > 300 candles = weak volume

# Features
LOG_LEVEL=INFO                  # Set to DEBUG for troubleshooting
PAPER_MODE=false                # Set true to test without API
```

---

## 🧪 Testing Checklist

After setup, verify in this order:

```bash
# 1. Check credentials exist
grep DHAN_API_KEY .env

# 2. Install dependencies
pip install -r requirements.txt

# 3. Quick API test
python test_api.py              # Should show ✅ Connected

# 4. Run full tests
pytest tests/ -v                # Should show 52/52 passed

# 5. Start dashboard
streamlit run dashboard.py      # Opens http://localhost:8501

# 6. Test in browser
# - Go to "API Test" tab
# - Click "Test Connection"
# - Should show ✅
```

---

## 📡 Sample Symbols & Strikes

**Futures** (Always have data during market hours):
```
RELIANCE    TCS         INFY        HDFC
ICICIBANK   AXISBANK    LT          WIPRO
```

**Expiry** (Next Thursday, e.g.):
```
27NOV2026   04DEC2026   25DEC2026   30JAN2027
```

**Strikes** (Examples):
```
RELIANCE:  2700, 2750, 2800, 2850, 2900
TCS:       3300, 3400, 3500, 3600
INFY:      2800, 2850, 2900, 2950
```

---

## 🚨 Common Errors & Fixes

### Error: "API Connection: FAILED"
```
CHECK: .env file has DHAN_API_KEY and DHAN_CLIENT_ID
CHECK: No spaces before/after values
CHECK: Internet is working (ping google.com)
FIX:   double-check credentials with DHAN account
```

### Error: "No data returned"
```
CHECK: Market is open (09:15-15:30 IST, Mon-Fri)
CHECK: Symbol is NSE F&O (e.g., RELIANCE, not RELIANCE-EQ)
CHECK: Expiry date is correct (use next Thursday)
FIX:   Test during market hours with RELIANCE
```

### Error: "Module not found"
```
FIX: pip install -r requirements.txt
     python -c "import streamlit; print('OK')"
```

### Streamlit won't start
```
FIX: streamlit run dashboard.py --server.port=8501
     Open browser: http://localhost:8501
```

---

## 📊 Data You'll See

### Futures Candle
- **Close**: Price (e.g., ₹2,752.25)
- **Volume**: Trading quantity (e.g., 125,000)
- **OI**: Open Interest (e.g., 15,00,000)
- **Time**: Candle timestamp

### Options Chain
- **CE (Call)**: Close price, Volume, OI
- **PE (Put)**: Close price, Volume, OI

### Gate Results
```
Gate 1-6: OI Wall, Strike GEX, Sellers, Buying/Writing
          → Each shows ✅ PASS or ❌ FAIL

Gate 7:   Futures Read (UP/DOWN/FLAT + Strength)
          → Shows: Fresh Long, Short Covering, etc.

Gate 8:   Session Accumulation (BULL/BEAR/NEUTRAL)
          → Shows: Bull +2.8L, Bear +1.5L, Neutral
```

### Readiness Decision
```
8/8 passes  → Full position
6-7 passes  → Half position
4-5 passes  → Wait
<4 passes   → Stay out
```

---

## 💡 Pro Tips

**Speed Up Testing**:
```env
API_TIMEOUT_SECONDS=5           # Faster timeouts
API_RETRY_COUNT=1               # No retries
MAX_CONCURRENT_SYMBOLS=10       # Fetch more at once
```

**Debug Problems**:
```env
LOG_LEVEL=DEBUG                 # More detailed output
PAPER_MODE=true                 # Use mock data
```

**View Real-Time Logs**:
```bash
# Windows PowerShell
Get-Content .\logs\scanner.log -Wait

# Git Bash/WSL
tail -f ./logs/scanner.log
```

**Test Specific Symbol**:
```bash
# Edit test_api.py, change:
# test_symbols = ["RELIANCE", "TCS", "INFY"]
# Then run:
python test_api.py
```

---

## 🎓 Understanding Gate 7 & 8

**Gate 7: Futures Read** (What is price doing?)
```
UP with rising OI & volume   → Fresh Long Build (BUY)
UP with falling OI            → Short Covering (SELL)
DOWN with rising OI & volume → Fresh Short Build (SELL)
DOWN with falling OI          → Long Unwinding (BUY)
```

**Gate 8: Session Accumulation** (Who is winning?)
```
Bull Lead (FL+SC > FS+LU)     → Buyers winning → CE trade
Bear Lead (FS+LU > FL+SC)     → Sellers winning → PE trade
Within Band                   → Neutral → Wait
```

**Combined Decision**:
```
Gate 7 = UP + Gate 8 = BULL   → Strong CE opportunity
Gate 7 = DOWN + Gate 8 = BEAR → Strong PE opportunity
Gate 7 UP + Gate 8 BEAR       → Conflicting signals → Caution
```

---

## 📍 File Locations

| File | Purpose |
|------|---------|
| `.env` | Your API credentials (EDIT THIS FIRST!) |
| `test_api.py` | Quick connection test |
| `dashboard.py` | Interactive web dashboard |
| `src/provider.py` | DHAN API adapter |
| `src/gates.py` | Gate calculations |
| `logs/scanner.log` | Application logs |
| `data/scanner.db` | SQLite database |

---

## 🌐 URLs & Endpoints

**Dashboard**: http://localhost:8501
**DHAN API Docs**: https://dhan.co/api-docs
**NSE Symbols**: https://www.nseindia.com

---

## 📞 Support Checklist

Having issues? Do this:

- [ ] Check `.env` file has credentials
- [ ] Run `python test_api.py`
- [ ] Check logs: `type .\logs\scanner.log`
- [ ] Enable DEBUG: Edit `.env` → `LOG_LEVEL=DEBUG`
- [ ] Verify market is open (09:15-15:30 IST, Mon-Fri)
- [ ] Test with RELIANCE (most liquid)
- [ ] Contact DHAN support with API key issue

---

## 🚀 Next Steps

1. **Setup**: `copy .env.example .env` → Edit with credentials
2. **Test**: `python test_api.py` → Should see ✅ Connected
3. **Dashboard**: `streamlit run dashboard.py` → Opens browser
4. **Verify**: Click "API Test" tab → Click "Test Connection"
5. **Monitor**: Watch Market Scanner for live stock data

---

**Last Updated**: November 17, 2026
**Version**: 1.0
**Status**: Production Ready ✅
