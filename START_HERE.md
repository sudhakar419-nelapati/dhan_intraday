# 🚀 START HERE - DHAN API Setup

You have your DHAN API access token. This is your complete setup guide.

---

## ⏱️ Time Required: 5 Minutes

---

## 🎯 Goal
View live NSE F&O market data in your STAR Trading Scanner dashboard using your DHAN API credentials.

---

## 📋 What You'll Do

### **Step 1: Create Configuration File** (1 minute)

```bash
copy .env.example .env
```

This creates a file with all configuration options.

### **Step 2: Add Your Credentials** (1 minute)

**Open `.env` file** (in Notepad or any text editor):
```bash
notepad .env
```

**Find these lines:**
```env
DHAN_API_KEY=your_dhan_api_key_here
DHAN_CLIENT_ID=your_dhan_client_id_here
```

**Replace with YOUR actual credentials:**
```env
DHAN_API_KEY=abc123xyz789...  # Your actual API key from DHAN
DHAN_CLIENT_ID=D123456789...  # Your actual Client ID from DHAN
```

**Save the file** (Ctrl+S, then close)

### **Step 3: Test Connection** (1 minute)

```bash
python test_api.py
```

**Expected output:**
```
✅ API Connection: SUCCESS

Sample Futures Data:
Symbol        Close        Volume    OI
RELIANCE      ₹2,750.50    125,000   15,00,000
TCS           ₹3,420.25    85,000    8,50,000
INFY          ₹2,890.75    95,000    9,20,000
```

If you see ✅, your API is working! Skip to Step 5.

If you see ❌, check:
1. API key spelled correctly (no extra spaces)
2. Client ID spelled correctly
3. Internet is working (`ping google.com`)

### **Step 4: View Data in Dashboard** (2 minutes)

```bash
streamlit run dashboard.py
```

Browser opens at: **http://localhost:8501**

### **Step 5: Test in Browser**

1. Click the **"API Test"** tab (left sidebar)
2. Click **"🧪 Test Connection"** button
3. See ✅ if working, or ❌ if credentials wrong
4. Enter symbol (e.g., `RELIANCE`) and click **"📥 Fetch Futures Candle"**
5. See live data displayed!

---

## 📊 What You Can Do Now

### **In the Dashboard:**

| Tab | What to Do |
|-----|---|
| **API Test** | Test connection, fetch any symbol/strike, see live data |
| **Market Scanner** | View all NSE F&O stocks ranked by STAR gates |
| **Stock Detail** | View 5-minute candles for one stock, see all 8 gates |
| **Logs & Diagnostics** | Monitor API calls and system health |
| **Settings** | Adjust thresholds and retry parameters |

### **Example Test Symbols:**
- **Futures**: RELIANCE, TCS, INFY, HDFC, ICICIBANK
- **Expiry**: 27NOV2026 (or next Thursday)
- **Strikes**: 2900 (sample, adjust per symbol)

---

## 🎓 Understanding What You're Looking At

### **Gate 7: Futures Read** 
Shows what the futures market is doing:
- **UP with rising OI** = Buyers in control (Fresh Long)
- **UP with falling OI** = Shorts covering (Good for SELL)
- **DOWN with rising OI** = Sellers in control (Fresh Short)
- **DOWN with falling OI** = Long unwinding (Good for BUY)

### **Gate 8: Session Accumulation**
Shows who's winning during the session:
- **Bull Lead** = More buyers than sellers → CE opportunity
- **Bear Lead** = More sellers than buyers → PE opportunity
- **Neutral** = Balanced → Wait for setup

### **Readiness Decision**
Based on how many gates pass (out of 8):
- **8/8** = Full position size
- **6-7/8** = Half position size
- **4-5/8** = Wait for setup
- **<4/8** = Stay out of trade

---

## 📂 Reference Documents

**Read these for more details:**

1. **[DHAN_API_QUICK_START.md](./DHAN_API_QUICK_START.md)** ← Detailed 5-step guide
2. **[QUICK_REFERENCE.md](./QUICK_REFERENCE.md)** ← Cheat sheet (commands, errors, symbols)
3. **[API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md)** ← Complete reference manual
4. **[DHAN_INTEGRATION_DIAGRAM.txt](./DHAN_INTEGRATION_DIAGRAM.txt)** ← Architecture overview

---

## ✅ Verification Checklist

After completing the steps above, verify everything works:

```bash
# 1. Check credentials exist
grep DHAN_API_KEY .env
# Should show: DHAN_API_KEY=your_key_here

# 2. Test API connection
python test_api.py
# Should show: ✅ API Connection: SUCCESS

# 3. Run full test suite
pytest tests/ -v
# Should show: 52 passed

# 4. Launch dashboard
streamlit run dashboard.py
# Should open: http://localhost:8501

# 5. In browser
# - Go to "API Test" tab
# - Click "Test Connection"
# - Should show: ✅ API Connection: SUCCESS
```

---

## 🚨 If Something Goes Wrong

### ❌ "API Connection: FAILED"
```
FIX: Double-check .env file
     1. Open: notepad .env
     2. Find: DHAN_API_KEY=...
     3. Make sure it matches exactly what DHAN gave you
     4. No spaces before/after the value
     5. Save and try again
```

### ❌ "No data returned"
```
This is NORMAL if:
  • Market is closed (Outside 09:15-15:30 IST, Mon-Fri)
  • Symbol is not NSE F&O (e.g., using RELIANCE-EQ instead of RELIANCE)
  • Expiry date doesn't exist

FIX: Test with RELIANCE during market hours (09:15-15:30 IST)
```

### ❌ "Module not found" error
```
FIX: pip install -r requirements.txt
     python -c "import streamlit; print('OK')"
```

### ❌ Streamlit won't open in browser
```
FIX: Try this command:
     streamlit run dashboard.py --server.port=8501
     
     Open browser to: http://localhost:8501
```

---

## 📞 Getting Help

If you're stuck:

1. **Check the logs:**
   ```bash
   type .\logs\scanner.log
   ```

2. **Enable debug mode:**
   - Edit `.env` and change: `LOG_LEVEL=DEBUG`
   - Run: `python test_api.py` again
   - You'll see more detailed error messages

3. **Quick Reference:**
   - See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) for commands and common errors

4. **Full Manual:**
   - See [API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md) for complete reference

5. **DHAN Support:**
   - Verify your API key with DHAN team
   - Confirm your account has API access

---

## 🎯 Next Steps (Optional)

After basic setup works:

1. **Explore Dashboard**
   - Try different symbols
   - View 5-minute candles
   - Check gate calculations

2. **Configure Thresholds** (Settings tab)
   - OI Strength thresholds
   - Volume rank settings
   - API retry parameters

3. **Monitor Scanner**
   - Refresh every 5 minutes during market hours
   - Track stocks with strong setups
   - Build your trading watchlist

4. **Review Documentation**
   - [README.md](./README.md) - Complete technical reference
   - [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) - What's implemented

---

## 💡 Tips

**Speed Up Testing:**
```env
API_TIMEOUT_SECONDS=5           # Faster timeouts
API_RETRY_COUNT=1               # No retries
```

**Use Test Mode (No API):**
```env
PAPER_MODE=true                 # Uses mock data
```

**View Real-Time Logs:**
```bash
# PowerShell
Get-Content .\logs\scanner.log -Wait

# Git Bash/WSL
tail -f ./logs/scanner.log
```

---

## ✨ You're All Set!

Your STAR Trading Scanner is now ready to:
✅ Connect to DHAN API
✅ Fetch live market data
✅ Calculate all 8 STAR gates
✅ Show readiness status for every stock
✅ Display in interactive web dashboard

**Happy trading! 📈**

---

**Questions?** See [QUICK_REFERENCE.md](./QUICK_REFERENCE.md) or [API_SETUP_GUIDE.md](./API_SETUP_GUIDE.md)

**Last Updated**: November 17, 2026
**Status**: Ready to Use ✅
