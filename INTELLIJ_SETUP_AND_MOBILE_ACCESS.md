# 🚀 Running STAR Scanner from IntelliJ & Accessing from Mobile

This guide shows you how to run the application from IntelliJ IDEA and access it from your mobile phone or outside your network.

---

## Part 1: Running from IntelliJ IDEA

### Step 1: Open Project in IntelliJ

```
1. Open IntelliJ IDEA
2. Click: File → Open
3. Navigate to: C:\Users\ADMIN\IdeaProjects\dhan_intraday
4. Click: "Open as Project"
5. Wait for indexing to complete
```

### Step 2: Configure Python Interpreter

```
1. Click: File → Settings
2. Go to: Project: dhan_intraday → Python Interpreter
3. Click: "Add Interpreter" → "Add Local Interpreter"
4. Select: "Existing Environment"
5. Choose: Python interpreter (usually: C:\Users\XXX\AppData\Local\Programs\Python\Python3.x\python.exe)
6. Click: OK
```

**Or if you don't have Python interpreter:**
```
File → Settings → Python Interpreter → Install → Select python version
```

### Step 3: Install Dependencies

```
1. Open: Terminal (at bottom of IntelliJ)
2. Run: pip install -r requirements.txt
3. Wait for all packages to install
```

### Step 4: Setup Configuration

```
1. In Terminal, run:
   copy .env.example .env

2. Open: .env file (in IntelliJ editor)

3. Find and replace:
   DHAN_API_KEY=your_actual_key_here
   DHAN_CLIENT_ID=your_actual_id_here

4. Save file (Ctrl+S)
```

### Step 5: Run from IntelliJ - Option A: Dashboard (Streamlit)

```
Method 1 - Using Terminal:
1. Open Terminal in IntelliJ (Alt+F12)
2. Run: streamlit run dashboard.py
3. It will show: Local URL: http://localhost:8501
4. Click the URL or open browser to that address
5. Dashboard opens in browser (Streamlit handles UI)

Method 2 - Using Run Configuration:
1. Click: Run → Edit Configurations
2. Click: + (Add new)
3. Select: Python
4. Configure:
   Name: Dashboard
   Script path: C:\...\dhan_intraday\dashboard.py
   Parameters: 
   Working directory: C:\Users\ADMIN\IdeaProjects\dhan_intraday
5. Click: OK
6. Click: Run (or press Shift+F10)
7. See output in Run console
8. Browser opens automatically to http://localhost:8501
```

### Step 6: Run from IntelliJ - Option B: API Tester

```
1. Open Terminal in IntelliJ
2. Run: python test_api.py
3. See output: ✅ API Connection: SUCCESS
4. And sample market data
```

### Step 7: Run from IntelliJ - Option C: Tests

```
1. Open Terminal in IntelliJ
2. Run: pytest tests/ -v
3. See: 52 passed
4. Or right-click on tests/ folder → Run All Tests
```

### Step 8: View Logs in IntelliJ

```
1. Terminal → Find: logs/ folder in project
2. Double-click: scanner.log
3. IntelliJ opens it in editor
4. See: Real-time logs as app runs
```

---

## Part 2: Accessing from Mobile & Outside Network

### 🔗 **URL & Local Access**

**When Running on Your Computer:**
```
Local URL (same computer):
http://localhost:8501

Local Network URL (from other devices on same WiFi):
http://192.168.X.X:8501
(Replace X.X with your computer's IP address)
```

**Find Your Computer's IP Address:**

**On Windows:**
```bash
# In Terminal/PowerShell, run:
ipconfig

Look for: IPv4 Address (usually 192.168.1.X or 192.168.0.X)
```

**Example:**
- Your IP: 192.168.1.100
- Access from mobile: http://192.168.1.100:8501

---

## Part 3: Access from Mobile on Same WiFi Network

### **Step 1: Find Your Computer's IP**

**Windows:**
```bash
# Open Terminal and run:
ipconfig

# Look for: IPv4 Address
# Example output:
IPv4 Address. . . . . . . . . . : 192.168.1.100
```

### **Step 2: Ensure Firewall Allows Access**

**Windows Firewall:**
```
1. Settings → Privacy & Security → Windows Defender Firewall
2. Click: Allow an app through firewall
3. Look for: Python
4. Check both: Private and Public
5. Click: OK
```

### **Step 3: Start Streamlit Dashboard**

**On Your Computer:**
```bash
# Terminal in IntelliJ, run:
streamlit run dashboard.py --server.address 0.0.0.0 --server.port 8501
```

**Output:**
```
Local URL: http://localhost:8501
Network URL: http://192.168.1.100:8501
External URL: http://XXX.XXX.XXX.XXX:8501
```

### **Step 4: Access from Mobile on Same WiFi**

**On Your Mobile Phone:**
```
1. Connect to same WiFi as computer
2. Open any browser (Chrome, Safari, etc.)
3. Go to: http://192.168.1.100:8501
   (Replace 192.168.1.100 with your computer's IP)
4. You should see the STAR Scanner dashboard!
```

---

## Part 4: Access from Outside Network (Mobile Data / Different Network)

### **Option 1: Use ngrok (Easiest - Recommended)**

#### **What is ngrok?**
- Free service that creates a public URL to your local app
- Anyone can access with the URL
- No port forwarding needed
- Works with mobile data

#### **Setup ngrok:**

**Step 1: Download ngrok**
```
1. Go to: https://ngrok.com/download
2. Download for Windows
3. Extract to: C:\ngrok
4. Or add to PATH
```

**Step 2: Get ngrok Auth Token**
```
1. Sign up free: https://ngrok.com/signup
2. Login to dashboard
3. Copy: Auth Token
4. Run in Terminal:
   ngrok config add-authtoken YOUR_AUTH_TOKEN
```

**Step 3: Run Dashboard with ngrok**

**Method 1 - Using ngrok directly:**
```bash
# Terminal 1: Start dashboard
streamlit run dashboard.py --server.port 8501

# Terminal 2: Create ngrok tunnel
ngrok http 8501

# Output:
# Forwarding    https://abc123def456-78.ngrok.io -> http://localhost:8501
```

**Method 2 - Best Practice:**
```bash
# Create a batch file: start_with_ngrok.bat
# Content:
start cmd /k streamlit run dashboard.py --server.port 8501
start cmd /k ngrok http 8501
```

**Then run the batch file from IntelliJ Terminal:**
```bash
start_with_ngrok.bat
```

**Step 4: Access from Mobile Anywhere**
```
1. Open mobile browser
2. Go to: https://abc123def456-78.ngrok.io
   (Use the URL from ngrok output)
3. Access your dashboard from anywhere!
```

---

### **Option 2: Port Forwarding (If You Have Router Access)**

#### **Setup Router Port Forwarding:**

**Step 1: Find Your Router IP**
```bash
# Windows Terminal:
ipconfig /all

# Look for: Default Gateway
# Example: 192.168.1.1
```

**Step 2: Access Router Settings**
```
1. Open browser
2. Go to: http://192.168.1.1
3. Login with router credentials
4. Find: Port Forwarding section
```

**Step 3: Configure Port Forwarding**
```
External Port: 8501
Internal Port: 8501
Internal IP: 192.168.1.100 (your computer IP)
Protocol: TCP
```

**Step 4: Find Your Public IP**
```
1. Go to: https://www.whatismyip.com
2. Note your Public IP (e.g., 203.0.113.42)
```

**Step 5: Access from Mobile Anywhere**
```
1. Mobile browser
2. Go to: http://203.0.113.42:8501
3. Can access from anywhere
```

**⚠️ Note:** Public IP can change. Use dynamic DNS for permanent access.

---

### **Option 3: Cloud Deployment (Advanced)**

For permanent, production-grade access:

**Recommended Services:**
- **Heroku** - Easy deployment of Streamlit apps
- **AWS EC2** - More control
- **Azure** - Enterprise option
- **Render** - Similar to Heroku

---

## 📱 Mobile Access Comparison

| Method | Setup Time | Public Access | Cost | Use Case |
|--------|-----------|---------------|------|----------|
| **Same WiFi** | 1 min | ❌ No | Free | Quick testing at home |
| **ngrok** | 5 min | ✅ Yes | Free | Mobile testing outside |
| **Port Forward** | 15 min | ✅ Yes | Free | Permanent (if IP static) |
| **Cloud Deploy** | 30 min | ✅ Yes | $5-50/mo | Production deployment |

---

## 🎯 Quick Reference - Different Scenarios

### **Scenario 1: Test Locally on Your Computer**
```bash
# In IntelliJ Terminal:
streamlit run dashboard.py

# Open: http://localhost:8501
```

### **Scenario 2: Test from Mobile on Same WiFi**
```bash
# Find your IP:
ipconfig

# In IntelliJ Terminal:
streamlit run dashboard.py --server.address 0.0.0.0

# On mobile:
# Open: http://192.168.1.100:8501
```

### **Scenario 3: Test from Mobile Outside Network (Recommended)**
```bash
# Terminal 1 - Start dashboard:
streamlit run dashboard.py --server.port 8501

# Terminal 2 - Start ngrok tunnel:
ngrok http 8501

# On mobile:
# Open: https://abc123-ngrok.io (from ngrok output)
```

### **Scenario 4: Production Access (Permanent URL)**
```bash
# Deploy to cloud (Heroku, AWS, etc.)
# Get: https://myapp.herokuapp.com
# Access from anywhere with permanent URL
```

---

## 🔐 Security Considerations

### **If Using Port Forwarding or Public Access:**

```bash
# 1. Add authentication in .env:
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ENABLE_CORS=false

# 2. Change default port:
streamlit run dashboard.py --server.port 9000

# 3. Use HTTPS (ngrok does this automatically)

# 4. Restrict access:
# - Only share URL with trusted users
# - Change URL periodically
# - Don't expose API credentials in URL
```

### **Never Do This:**
```
❌ Share .env file with credentials
❌ Expose DHAN_API_KEY in public
❌ Run on 0.0.0.0 without authentication
❌ Use simple passwords for port forwarding
```

---

## 🧪 Testing Guide

### **Test 1: Access on Same Computer**
```bash
streamlit run dashboard.py
# Open: http://localhost:8501
# Expected: Dashboard loads ✅
```

### **Test 2: Access from Mobile on Same WiFi**
```bash
streamlit run dashboard.py --server.address 0.0.0.0
# On mobile: http://192.168.1.100:8501
# Expected: Dashboard loads ✅
```

### **Test 3: Access from Mobile Outside Network**
```bash
# Terminal 1:
streamlit run dashboard.py --server.port 8501

# Terminal 2:
ngrok http 8501

# On mobile (using 4G/LTE):
# Go to: https://abc-ngrok.io (from ngrok output)
# Expected: Dashboard loads ✅
```

### **Test 4: Verify API Test Tab Works**
```
1. Open dashboard in browser/mobile
2. Click: "API Test" tab
3. Click: "Test Connection" button
4. Expected: ✅ API Connection Successful!
```

---

## 📊 URL Reference

| Scenario | URL | Accessible From |
|----------|-----|-----------------|
| Local computer | http://localhost:8501 | Same computer only |
| Same WiFi | http://192.168.1.100:8501 | Same WiFi network |
| ngrok tunnel | https://abc-ngrok.io | Anywhere (temporary) |
| Public IP | http://203.0.113.42:8501 | Anywhere (permanent) |
| Cloud deployed | https://myapp.herokuapp.com | Anywhere (permanent) |

---

## 🛠️ IntelliJ Tips & Tricks

### **Run Multiple Things at Once**

**Terminal Windows:**
```
1. Terminal at bottom of IntelliJ
2. Click: + (new terminal tab)
3. Terminal 1: streamlit run dashboard.py
4. Terminal 2: ngrok http 8501
5. Both run simultaneously!
```

### **Create Run Configuration for Streamlit**

```
1. Run → Edit Configurations
2. +  → Python
3. Settings:
   Name: Streamlit Dashboard
   Script path: dashboard.py
   Parameters: --server.address 0.0.0.0
   Working directory: (your project folder)
4. Apply → OK
5. Run via: Run → Run 'Streamlit Dashboard'
```

### **View Application Logs**

```
1. Run → View Logs
2. See: dashboard.log
3. Or open: logs/scanner.log in editor
```

### **Debug Mode**

```
If something wrong:
1. Terminal: streamlit run dashboard.py --logger.level=debug
2. See: Detailed debug output
3. Check: logs/scanner.log
```

---

## 📱 Mobile Browser Tips

### **Best Mobile Browsers for Testing**
```
iOS:
✅ Safari (works best)
✅ Chrome

Android:
✅ Chrome (best)
✅ Firefox
✅ Samsung Internet
```

### **Desktop Browser Zoom on Mobile**
```
If dashboard doesn't fit:
1. Pinch to zoom out
2. Or try landscape mode
3. Or use responsive view
```

---

## 🚀 Summary

### **To Run from IntelliJ:**
1. Open project in IntelliJ
2. Set Python interpreter
3. Install dependencies: `pip install -r requirements.txt`
4. Configure `.env` with DHAN credentials
5. Run: `streamlit run dashboard.py`
6. Access: `http://localhost:8501`

### **To Access from Mobile:**

**Same WiFi (Easiest):**
```bash
streamlit run dashboard.py --server.address 0.0.0.0
# Then: http://192.168.1.100:8501 on mobile
```

**Outside Network (Recommended):**
```bash
# Terminal 1: streamlit run dashboard.py --server.port 8501
# Terminal 2: ngrok http 8501
# Then: https://abc-ngrok.io on mobile
```

---

## 🎯 Next Steps

1. ✅ Open project in IntelliJ
2. ✅ Install dependencies
3. ✅ Configure `.env` with DHAN credentials
4. ✅ Run: `streamlit run dashboard.py`
5. ✅ Access on computer: http://localhost:8501
6. ✅ For mobile: Use ngrok (easiest)
7. ✅ Test API Test tab
8. ✅ Fetch live market data

---

**Happy developing!** 🚀

---

**Questions?**
- Streamlit Docs: https://docs.streamlit.io
- ngrok Docs: https://ngrok.com/docs
- IntelliJ Docs: https://www.jetbrains.com/help/idea/
