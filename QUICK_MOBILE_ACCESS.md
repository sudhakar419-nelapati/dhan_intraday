# 📱 Quick Reference - IntelliJ & Mobile Access

## 🚀 TL;DR - Quick Start

### **Run from IntelliJ (3 steps)**
```bash
# 1. Open Terminal in IntelliJ (Alt+F12)
# 2. Install dependencies (first time only):
pip install -r requirements.txt

# 3. Run dashboard:
streamlit run dashboard.py
```

**URL:** `http://localhost:8501` (opens in browser automatically)

---

## 🌐 URLs & Access

### **Local Computer Only**
```
http://localhost:8501
```

### **Same WiFi Network (Phone + Computer)**
```
1. Find your computer IP:
   ipconfig  (look for IPv4 Address)
   
2. Run with network access:
   streamlit run dashboard.py --server.address 0.0.0.0

3. Mobile access:
   http://192.168.1.100:8501
   (Replace 192.168.1.100 with your IP)
```

### **Outside Network (Mobile Data / Different WiFi) - RECOMMENDED**
```
1. Terminal 1 - Start dashboard:
   streamlit run dashboard.py --server.port 8501

2. Terminal 2 - Start ngrok tunnel:
   ngrok http 8501

3. Mobile access:
   https://abc123def-ngrok.io
   (Use the URL from ngrok output)
```

---

## 📋 Step-by-Step: IntelliJ Setup

### **1️⃣ Open Project**
- File → Open → Select: `C:\Users\ADMIN\IdeaProjects\dhan_intraday`

### **2️⃣ Set Python**
- File → Settings → Python Interpreter → Add existing Python

### **3️⃣ Install Packages**
- Terminal (Alt+F12) → `pip install -r requirements.txt`

### **4️⃣ Configure API**
- Open `.env` file → Add: `DHAN_API_KEY=...` and `DHAN_CLIENT_ID=...`

### **5️⃣ Run Dashboard**
- Terminal → `streamlit run dashboard.py`

### **6️⃣ Open Browser**
- Automatic: http://localhost:8501
- Or click the URL in terminal

---

## 📱 Mobile Access - 3 Ways

### **Method 1: Same WiFi (Easiest)**
```bash
# Computer Terminal:
streamlit run dashboard.py --server.address 0.0.0.0

# Mobile Browser:
http://192.168.1.X:8501
```
⏱️ Setup: 1 minute  
🌐 Access: WiFi only  
💰 Cost: Free

---

### **Method 2: ngrok (Best) ⭐ RECOMMENDED**
```bash
# Download: https://ngrok.com/download
# Terminal 1:
streamlit run dashboard.py --server.port 8501

# Terminal 2:
ngrok http 8501

# Mobile Browser:
https://abc123def-ngrok.io
```
⏱️ Setup: 5 minutes  
🌐 Access: Anywhere (4G/5G/WiFi)  
💰 Cost: Free

---

### **Method 3: Port Forwarding (Advanced)**
```
1. Router → Port Forward 8501
2. Find public IP: whatismyip.com
3. Mobile: http://203.0.113.42:8501
```
⏱️ Setup: 15 minutes  
🌐 Access: Anywhere (permanent)  
💰 Cost: Free (if static IP)  
⚠️ Note: Requires router access

---

## ⚡ Common Commands Reference

### **In IntelliJ Terminal**

| Command | Purpose |
|---------|---------|
| `pip install -r requirements.txt` | Install dependencies |
| `streamlit run dashboard.py` | Run dashboard locally |
| `streamlit run dashboard.py --server.address 0.0.0.0` | Run on network |
| `python test_api.py` | Test API connection |
| `pytest tests/ -v` | Run all tests |
| `ngrok http 8501` | Create public URL |

---

## 🔍 Find Your Computer IP

### **Windows**
```bash
# Method 1: Terminal
ipconfig
# Look for: IPv4 Address (usually 192.168.X.X)

# Method 2: GUI
# Settings → Network & internet → WiFi → Properties
# Look for: IPv4 address
```

### **Example Output**
```
IPv4 Address. . . . . . . . . . : 192.168.1.100
Subnet Mask . . . . . . . . . . : 255.255.255.0
Default Gateway . . . . . . . . : 192.168.1.1
```

**Use this in mobile URL:** `http://192.168.1.100:8501`

---

## 🌐 URLs Cheat Sheet

```
Local Computer:        http://localhost:8501
Same WiFi Phone:       http://192.168.1.100:8501
ngrok Tunnel:          https://abc123-ngrok.io
Port Forwarded:        http://203.0.113.42:8501
Cloud Deployed:        https://myapp.herokuapp.com
```

---

## 🧪 Quick Test Checklist

### **On Your Computer**
- [ ] IntelliJ opened with project
- [ ] Python interpreter configured
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file has DHAN credentials
- [ ] Dashboard running: `streamlit run dashboard.py`
- [ ] Browser shows: http://localhost:8501

### **On Your Mobile (Same WiFi)**
- [ ] Connected to same WiFi as computer
- [ ] Know computer IP: `ipconfig`
- [ ] Mobile URL: http://192.168.1.100:8501
- [ ] Dashboard loads in mobile browser

### **On Your Mobile (Outside Network)**
- [ ] ngrok installed on computer
- [ ] ngrok tunnel running: `ngrok http 8501`
- [ ] Have ngrok public URL
- [ ] Mobile on 4G/5G (not WiFi)
- [ ] Mobile URL: https://abc-ngrok.io
- [ ] Dashboard loads in mobile browser

---

## 🚨 Troubleshooting

### ❌ "Port 8501 already in use"
```bash
# Use different port:
streamlit run dashboard.py --server.port 9000
# Mobile: http://192.168.1.100:9000
```

### ❌ "Cannot access from mobile on same WiFi"
```bash
# 1. Check firewall (allow Python)
# 2. Run with network binding:
   streamlit run dashboard.py --server.address 0.0.0.0
# 3. Verify same WiFi on both devices
# 4. Check mobile IP configuration
```

### ❌ "ngrok connection refused"
```bash
# 1. Make sure dashboard running first:
   streamlit run dashboard.py --server.port 8501
# 2. Then start ngrok in separate terminal:
   ngrok http 8501
# 3. Wait 5 seconds for connection
```

### ❌ "DHAN API key not working"
```bash
# 1. Check .env file has correct key (no spaces)
# 2. Run test: python test_api.py
# 3. Enable debug: LOG_LEVEL=DEBUG in .env
```

---

## 📲 Mobile Browser Tips

**iOS Safari:**
- Works best with Streamlit
- Zoom in/out with pinch
- Landscape mode for wider view

**Android Chrome:**
- Best overall experience
- Responsive design works well
- Hardware back button (careful!)

**All Browsers:**
- Reload if page doesn't load: Ctrl+R (or Cmd+R)
- Clear cache if changes don't show
- Check WiFi connection
- Try private/incognito mode

---

## 🎯 Recommended Setup for Mobile Testing

### **Best Practice (Easiest & Most Reliable)**

```bash
# Terminal 1 - Start dashboard:
streamlit run dashboard.py --server.port 8501

# Terminal 2 - Create public tunnel:
ngrok http 8501

# Mobile Browser:
# Open: https://abc123def-ngrok.io
```

**Why ngrok?**
- ✅ No router configuration needed
- ✅ Works with mobile data
- ✅ Automatic HTTPS (secure)
- ✅ Temporary public URL
- ✅ Free for testing
- ✅ Setup takes 5 minutes

---

## 📊 Summary Table

| Scenario | Command | URL | Setup |
|----------|---------|-----|-------|
| **Local Computer** | `streamlit run dashboard.py` | `http://localhost:8501` | 1 min |
| **Same WiFi Phone** | `streamlit run dashboard.py --server.address 0.0.0.0` | `http://192.168.1.X:8501` | 1 min |
| **Mobile Data (ngrok)** | `ngrok http 8501` | `https://abc-ngrok.io` | 5 min |
| **Router Port Forward** | Manual router setup | `http://203.0.X.X:8501` | 15 min |
| **Production Deploy** | Cloud platform | `https://myapp.com` | 30 min |

---

## 🔗 Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **ngrok Setup**: https://ngrok.com/download
- **ngrok Auth**: https://dashboard.ngrok.com
- **IntelliJ Setup**: https://www.jetbrains.com/help/idea/
- **Find IP**: `ipconfig` (Windows) or `ifconfig` (Mac/Linux)
- **Check Public IP**: https://www.whatismyip.com

---

## ✨ Success Indicators

### **Dashboard Working Locally**
- ✅ Browser shows Streamlit interface
- ✅ "API Test" tab visible in sidebar
- ✅ Can click "Test Connection" button
- ✅ Shows ✅ or ❌ connection status

### **Mobile Access Working**
- ✅ Mobile browser shows same dashboard
- ✅ All tabs and buttons work
- ✅ Can fetch live market data
- ✅ Performance acceptable (< 2 sec load)

---

**Ready to access from mobile?** Start with ngrok! 🚀

