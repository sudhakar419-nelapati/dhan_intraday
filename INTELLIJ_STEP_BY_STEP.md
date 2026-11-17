# 🎯 Step-by-Step: IntelliJ + Mobile Access

## Part 1: Run from IntelliJ IDEA

### **STEP 1: Open IntelliJ**
```
1. Click: Start Menu
2. Type: IntelliJ IDEA
3. Click: Open
```

### **STEP 2: Open Your Project**
```
1. File → Open
2. Navigate to: C:\Users\ADMIN\IdeaProjects
3. Select: dhan_intraday folder
4. Click: Open as Project
5. Wait for indexing (bottom of screen)
```

### **STEP 3: Set Python Interpreter**
```
1. File → Settings (or Ctrl+Alt+S)
2. Left panel: Project: dhan_intraday
3. Click: Python Interpreter
4. Click: Add Interpreter → Add Local Interpreter
5. Select: Existing Environment
6. Browse to: C:\Users\ADMIN\AppData\Local\Programs\Python\Python3.10\python.exe
   (Or wherever your Python is installed)
7. Click: OK
```

### **STEP 4: Install Dependencies**
```
1. Bottom of IntelliJ: Click on "Terminal" tab
2. Run this command:
   
   pip install -r requirements.txt
   
3. Wait for all packages to install (1-2 minutes)
4. When done, you'll see: Successfully installed ...
```

### **STEP 5: Configure DHAN Credentials**
```
1. Left panel: Click on .env file (or search for it)
2. It opens in editor
3. Find these lines:
   DHAN_API_KEY=your_dhan_api_key_here
   DHAN_CLIENT_ID=your_dhan_client_id_here

4. Replace with your actual credentials:
   DHAN_API_KEY=abc123xyz789...
   DHAN_CLIENT_ID=D123456789...

5. Save: Ctrl+S
```

### **STEP 6: Run the Dashboard**
```
1. Terminal: Alt+F12 (opens at bottom of IntelliJ)
2. Type:
   streamlit run dashboard.py

3. Wait for output:
   Local URL: http://localhost:8501
   Network URL: http://192.168.1.100:8501
   External URL: http://XXX.XXX.XXX.XXX:8501

4. Browser automatically opens to http://localhost:8501
```

### **STEP 7: See Dashboard in Browser**
```
You should see:
✅ STAR Trading Scanner title
✅ Left sidebar with 5 tabs:
   • Market Scanner
   • Stock Detail
   • API Test (NEW!)
   • Logs & Diagnostics
   • Settings

✅ Click "API Test" tab to test connection
✅ Click "Test Connection" button
```

---

## Part 2: Access from Mobile on Same WiFi

### **STEP 1: Find Your Computer's IP Address**

**On Your Computer (Windows):**
```
1. Terminal (Alt+F12 in IntelliJ)
2. Type: ipconfig
3. Look for: IPv4 Address
4. Example: 192.168.1.100
5. Remember this IP!
```

### **STEP 2: Enable Network Access**

**On Your Computer:**
```
1. Terminal (you can stop previous command with Ctrl+C)
2. Run:
   streamlit run dashboard.py --server.address 0.0.0.0

3. Output shows:
   Local URL: http://localhost:8501
   Network URL: http://192.168.1.100:8501 ← THIS ONE!
```

### **STEP 3: Connect Mobile to Same WiFi**

**On Your Mobile Phone:**
```
1. Settings → WiFi
2. Connect to same WiFi as your computer
3. Make sure it's connected (you'll see checkmark)
```

### **STEP 4: Access Dashboard on Mobile**

**On Your Mobile Phone:**
```
1. Open Browser (Chrome, Safari, etc.)
2. In address bar, type:
   http://192.168.1.100:8501
   
   (Replace 192.168.1.100 with YOUR computer's IP from Step 1)

3. Press Enter/Go
4. You should see the same dashboard!
```

**What You'll See:**
```
✅ STAR Trading Scanner interface
✅ All tabs work
✅ Can click buttons
✅ Can interact with dashboard
✅ Works on mobile screen
```

---

## Part 3: Access from Mobile Outside Network (Best Method)

### **This allows access from anywhere: 4G, 5G, different WiFi, etc.**

### **STEP 1: Download ngrok (One-time setup)**

**On Your Computer:**
```
1. Go to: https://ngrok.com/download
2. Download Windows version
3. Extract to: C:\ngrok
   (Or any folder you remember)
```

### **STEP 2: Create ngrok Account (One-time setup)**

**On Your Computer:**
```
1. Go to: https://ngrok.com/signup
2. Sign up with email (Free)
3. Verify email
4. Login to dashboard
5. Find: Auth Token
6. Copy it
```

### **STEP 3: Authorize ngrok (One-time setup)**

**On Your Computer Terminal:**
```
1. Open Terminal (new one)
2. Run:
   ngrok config add-authtoken YOUR_AUTH_TOKEN_HERE
   
   (Replace YOUR_AUTH_TOKEN_HERE with token from Step 2)

3. Press Enter
4. If successful: "Authtoken saved to config file"
```

### **STEP 4: Start Dashboard**

**On Your Computer - Terminal 1:**
```
1. Terminal 1 (or use existing one):
   streamlit run dashboard.py --server.port 8501

2. Keep this running
```

### **STEP 5: Create Public Tunnel**

**On Your Computer - Terminal 2:**
```
1. Open NEW terminal (or new tab in existing)
2. Run:
   ngrok http 8501

3. Output shows:
   Forwarding    https://abc123def456-78.ngrok.io -> http://localhost:8501
   
   Copy this URL! ← USE THIS URL
```

### **STEP 6: Access from Mobile Anywhere**

**On Your Mobile Phone (Any network):**
```
1. Open Browser
2. Type:
   https://abc123def456-78.ngrok.io
   
   (Use the URL from Step 5)

3. Press Enter/Go
4. Dashboard loads!
5. Works on 4G/5G or any WiFi!
```

**To Share with Others:**
```
You can share the URL with friends/colleagues
They can access from their phones too!
(URL changes every time you restart ngrok)
```

---

## 🎯 Quick Reference - Copy/Paste Commands

### **In IntelliJ Terminal:**

**First time only:**
```
pip install -r requirements.txt
```

**To run locally:**
```
streamlit run dashboard.py
```

**To run on network:**
```
streamlit run dashboard.py --server.address 0.0.0.0
```

**To run for ngrok:**
```
streamlit run dashboard.py --server.port 8501
```

### **In Separate Terminal (for ngrok):**

**Setup (first time only):**
```
ngrok config add-authtoken YOUR_TOKEN
```

**To create public tunnel:**
```
ngrok http 8501
```

---

## 📊 URL Reference

| Where You Are | URL | How to Get |
|---------------|-----|-----------|
| **Same Computer** | `http://localhost:8501` | Automatic in terminal |
| **Same WiFi Phone** | `http://192.168.1.100:8501` | ipconfig on computer |
| **Mobile Data / Different WiFi** | `https://abc-ngrok.io` | ngrok command output |

---

## ✅ Verification Checklist

### **Dashboard Running Locally**
- [ ] IntelliJ opened
- [ ] Project loaded
- [ ] Python interpreter set
- [ ] Dependencies installed
- [ ] `.env` file has credentials
- [ ] Terminal shows: "streamlit run dashboard.py"
- [ ] Browser opens to http://localhost:8501
- [ ] Dashboard visible with all tabs

### **Mobile Access - Same WiFi**
- [ ] Computer IP found: ipconfig
- [ ] Dashboard running with --server.address 0.0.0.0
- [ ] Mobile connected to same WiFi
- [ ] Mobile URL typed: http://192.168.1.100:8501
- [ ] Dashboard visible on mobile
- [ ] Can click buttons and interact

### **Mobile Access - ngrok (Outside Network)**
- [ ] ngrok downloaded and extracted
- [ ] ngrok account created
- [ ] ngrok auth token configured
- [ ] Dashboard running on port 8501
- [ ] ngrok tunnel running: `ngrok http 8501`
- [ ] ngrok URL copied
- [ ] Mobile URL typed in browser
- [ ] Dashboard accessible from anywhere

---

## 🚨 If Something Goes Wrong

### **"Streamlit port 8501 is already in use"**
```
1. Use different port:
   streamlit run dashboard.py --server.port 9000

2. Access: http://localhost:9000
3. ngrok: ngrok http 9000
```

### **"Cannot access from mobile on same WiFi"**
```
1. Check firewall allows Python
   Settings → Firewall → Allow app → Check Python

2. Make sure both on same WiFi (verify in WiFi settings)

3. Use correct IP:
   ipconfig (shows your computer IP)

4. Try: ping 192.168.1.100 from mobile
   (to test network connectivity)
```

### **"ngrok says 'No internet connection'"**
```
1. Make sure computer has internet (browser works)
2. Check firewall allows ngrok
3. Try: ngrok http 8501 --log=stdout (for debug)
```

### **"Dashboard doesn't show API Test tab"**
```
1. Make sure you have latest code from GitHub
2. Run: git pull origin main
3. Restart dashboard: Ctrl+C then streamlit run dashboard.py
```

---

## 📱 Mobile Browser Tips

**Best Browsers:**
- iOS: Safari (native, works best)
- Android: Chrome (most reliable)

**If Dashboard Looks Wrong:**
- Zoom out: Pinch with two fingers
- Rotate phone: Landscape mode
- Clear cache: Browser settings → Clear data
- Refresh: Pull down or Ctrl+R

---

## 🎓 Summary

### **Quick Path (5 minutes)**
```
1. IntelliJ → Open Project
2. Terminal → pip install -r requirements.txt
3. .env → Add DHAN credentials
4. Terminal → streamlit run dashboard.py
5. Browser → http://localhost:8501
✅ Done! Testing locally
```

### **Mobile Same WiFi (3 minutes extra)**
```
1. Terminal → ipconfig (note IP)
2. Terminal → streamlit run dashboard.py --server.address 0.0.0.0
3. Mobile → http://192.168.1.X:8501
✅ Done! Mobile access on same network
```

### **Mobile Outside Network (5 minutes extra)**
```
1. Download & setup ngrok (one-time)
2. Terminal 1 → streamlit run dashboard.py --server.port 8501
3. Terminal 2 → ngrok http 8501
4. Mobile → https://abc-ngrok.io
✅ Done! Mobile access from anywhere!
```

---

## 🚀 Next Steps

1. ✅ Follow Part 1 to run from IntelliJ
2. ✅ Test locally: http://localhost:8501
3. ✅ Click "API Test" tab → "Test Connection"
4. ✅ Fetch live market data
5. ✅ Follow Part 2 for mobile same WiFi
6. ✅ Follow Part 3 for mobile outside network

---

**You're all set!** 🎉
