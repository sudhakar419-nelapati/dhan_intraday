# Deploy STAR Trading Scanner to Streamlit Cloud - Your Custom URL

**Goal:** Get your dashboard a unique public URL like `https://sudhakar419-star-scanner.streamlit.app/`

---

## Your Custom URL Options

Choose one and we'll set it up:

### Option A (Recommended - Use Your GitHub Username)
```
https://sudhakar419-star-scanner.streamlit.app/
```

### Option B (Using Project Name)
```
https://dhan-intraday-scanner.streamlit.app/
```

### Option C (Unique Custom Name)
```
https://[your-custom-name].streamlit.app/
```

---

## Step-by-Step Deployment

### Step 1: Create Streamlit Cloud Account
1. Go to: https://share.streamlit.io/
2. Click "Sign up"
3. Sign in with GitHub account: `sudhakar419-nelapati`
4. Authorize Streamlit to access repositories

### Step 2: Deploy Your App
1. Click **"New app"** button
2. Fill in deployment details:
   - **Repository:** `sudhakar419-nelapati/dhan_intraday`
   - **Branch:** `main`
   - **Main file path:** `dashboard.py`
3. Click **"Deploy"**

### Step 3: Wait & Get Your URL
- Streamlit builds and deploys your app (2-5 minutes)
- You'll see your app URL after deployment
- Default format: `https://[generated-id].streamlit.app/`

### Step 4: Custom URL (Optional but Recommended)
1. Go to your deployed app settings (⚙️ icon top-right)
2. Under "Advanced settings" → "Custom domain"
3. Enter your custom name (e.g., `sudhakar419-star-scanner`)
4. Click "Save"

**Result:** `https://sudhakar419-star-scanner.streamlit.app/`

### Step 5: Configure API Credentials (CRITICAL!)
1. Click the **hamburger menu** (☰) top-right of your deployed app
2. Select **Settings** → **Secrets**
3. Add this content:
```
DHAN_API_KEY=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiJ9.eyJ1c2VyUmVnaW9uIjoiUjEiLCJpc3MiOiJkaGFuIiwicGFydG5lcklkIjoiIiwiZXhwIjoxNzk1MDA2MjU2LCJpYXQiOjE3OTQ5MTk4NTYsInRva2VuQ29uc3VtZXJUeXBlIjoiU0VMRiIsIndlYmhvb2tVcmwiOiIiLCJkaGFuQ2xpZW50SWQiOiIxMTA2NTIzODAwIn0.BEKwhfNBBQe9qekr6p91wGz_VwZQvk1USCrXbpn23M6QpxbLBn5rxfgyybd2KsESKB6K2Oqdibgkwyr4d8RiDg
DHAN_CLIENT_ID=1106523800
```
4. Click **"Save"**
5. App automatically restarts with secrets loaded ✓

---

## Code Changes Already Made ✓

Your `src/config.py` has been updated to support Streamlit Cloud:

```python
# Now supports both local (.env) and cloud (secrets)
try:
    import streamlit as st
    DHAN_API_KEY = st.secrets.get("DHAN_API_KEY", os.getenv("DHAN_API_KEY", ""))
    DHAN_CLIENT_ID = st.secrets.get("DHAN_CLIENT_ID", os.getenv("DHAN_CLIENT_ID", ""))
except:
    DHAN_API_KEY = os.getenv("DHAN_API_KEY", "")
    DHAN_CLIENT_ID = os.getenv("DHAN_CLIENT_ID", "")
```

This means:
- ✓ Works locally with `.env` file
- ✓ Works on Streamlit Cloud with secrets
- ✓ No code changes needed!

---

## Commit & Push Updated Code

```bash
cd C:\Users\ADMIN\IdeaProjects\dhan_intraday

# Commit the config changes
git add src/config.py
git commit -m "Add Streamlit Cloud deployment support

- Updated config.py to support both .env (local) and secrets (cloud)
- Automatically tries st.secrets first, falls back to .env
- No hardcoded credentials in code
- Safe for public deployment"

git push origin main
```

---

## Your Deployment Checklist

Before you deploy, verify:

- [x] Code is on GitHub (`sudhakar419-nelapati/dhan_intraday`)
- [x] `.env` file is NOT in git (uses .gitignore)
- [x] No hardcoded API keys in code
- [x] `dashboard.py` exists and is main file
- [x] All dependencies in `requirements.txt`
- [x] `src/config.py` updated for cloud

---

## After Deployment - What You Get

| Feature | Details |
|---------|---------|
| **Public URL** | `https://sudhakar419-star-scanner.streamlit.app/` |
| **Access** | Anyone can visit with just the URL |
| **Mobile** | Works perfectly on phones & tablets |
| **Live Data** | Fetches market data 09:15-15:30 IST |
| **Hosting** | Free (Streamlit Community Cloud) |
| **Storage** | 3 GB per account |
| **Uptime** | 24/7 (Streamlit maintains servers) |

---

## Share Your Dashboard

Once deployed, you can share:

```
Check out my STAR Trading Scanner:
https://sudhakar419-star-scanner.streamlit.app/

Features:
✓ Real-time NSE F&O analysis
✓ 8-gate STAR calculations
✓ Live signal recommendations
✓ Mobile & desktop compatible
```

---

## Troubleshooting During Deployment

### "API Connection FAILED"
- Check secrets are saved correctly in Streamlit Cloud
- Go to: App settings → Secrets
- Verify both DHAN_API_KEY and DHAN_CLIENT_ID are present
- Wait 1-2 minutes for app to restart

### "Module not found" error
- Ensure `src/__init__.py` exists
- Verify all imports in `dashboard.py` start with `from src.`
- Check `requirements.txt` has all dependencies

### "Database locked" error
- Cloud database is ephemeral (resets on restart)
- This is normal - data doesn't persist across deployments
- For persistent data, we can add cloud database later

### App timeout
- If calculations are slow, increase server resources
- Or optimize gate calculations
- Contact Streamlit support for larger instances

---

## Optional: Add Custom Branding

Add this to `dashboard.py` near the top:

```python
st.set_page_config(
    page_title="STAR Trading Scanner",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom title
st.markdown("""
    # 📊 STAR Trading Scanner
    *Real-time NSE F&O Analysis*
    
    Developed by: sudhakar419-nelapati
""")
```

---

## Quick Reference URLs

| Use Case | URL |
|----------|-----|
| Local Development | http://localhost:8501 |
| Same WiFi | http://192.168.1.100:8501 |
| ngrok Tunnel | https://abc123def-ngrok.io |
| **Streamlit Cloud** | **https://sudhakar419-star-scanner.streamlit.app/** |

---

## Next Steps (In Order)

1. **Push code to GitHub**
   ```bash
   git push origin main
   ```

2. **Go to Streamlit Cloud**
   https://share.streamlit.io/

3. **Click "New app"**
   - Repository: sudhakar419-nelapati/dhan_intraday
   - Branch: main
   - File: dashboard.py

4. **Wait for deployment** (2-5 minutes)

5. **Set custom domain** (optional)
   - Settings → Custom domain
   - Enter: `sudhakar419-star-scanner`

6. **Add secrets** (CRITICAL!)
   - Settings → Secrets
   - Add DHAN_API_KEY and DHAN_CLIENT_ID

7. **Share your URL!**
   ```
   https://sudhakar419-star-scanner.streamlit.app/
   ```

---

## Support

- **Streamlit Docs:** https://docs.streamlit.io/streamlit-cloud/get-started
- **Secrets Setup:** https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/connect-to-data-sources/secrets-management
- **Custom Domains:** https://docs.streamlit.io/streamlit-cloud/get-started/deploy-an-app/custom-domain-quick-start

---

## 🚀 Ready to Deploy?

Your code is ready! Just follow the 7 steps above and your dashboard will be live in 5-10 minutes with a unique URL that's yours alone.

**Your unique URL will be:**
```
https://sudhakar419-star-scanner.streamlit.app/
```

Go ahead and deploy! 🎯
