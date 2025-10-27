# 🚀 HYBRID DEPLOYMENT - Vercel Frontend + Local Backend

**Configuration:** Frontend on Vercel | Backend on Local Machine
**Date:** October 27, 2025
**Status:** ✅ READY FOR HYBRID DEPLOYMENT

---

## 📋 QUICK OVERVIEW

```
LOCAL MACHINE
┌──────────────────────────────────────┐
│  Backend (Python/Flask)              │
│  http://localhost:5000               │
│  - BOB AI v7.1 Knowledge Engine     │
│  - 1,330+ items loaded              │
│  - 8/8 API endpoints                │
│  - WebSocket support                │
└──────────────────────────────────────┘
         ▲
         │ Local Network (HTTPS/CORS)
         │
INTERNET CLOUD
┌──────────────────────────────────────┐
│  Frontend (Vercel CDN)               │
│  https://orfeas-ai-studio.vercel.app│
│  - 6 HTML files                      │
│  - Global distribution               │
│  - Auto-scaling                      │
│  - Free SSL                          │
└──────────────────────────────────────┘
```

---

## ⚡ HYBRID SETUP (30 MINUTES)

### Step 1: Deploy Frontend to Vercel (5 min)

```powershell
.\DEPLOY_TO_VERCEL.ps1
```

**Result:** `https://orfeas-ai-studio.vercel.app` ✅

### Step 2: Start Backend Locally (3 min)

```powershell
cd backend
python main.py
```

**Result:** `http://localhost:5000` ✅

### Step 3: Configure Connection (5 min)

Update frontend HTML files to use your local backend:

```html
<!-- In orfeas-ai-studio.html -->
<script>
  // Configuration
  const BACKEND_URL = 'http://localhost:5000';  // Local backend
  // OR use this for remote access:
  // const BACKEND_URL = 'http://YOUR_LOCAL_IP:5000';

  const API_BASE = BACKEND_URL + '/api';
</script>
```

### Step 4: Test & Verify (2 min)

✅ Frontend loads: <https://orfeas-ai-studio.vercel.app>
✅ Backend responds: <http://localhost:5000/health>
✅ API calls work: Frontend → Backend communication

---

## 🏗️ ARCHITECTURE

### Frontend (Vercel)

- **URL:** <https://orfeas-ai-studio.vercel.app>
- **Location:** Global CDN
- **Auto-deploys:** From GitHub on every push
- **SSL:** Automatic
- **Cost:** Free tier
- **Files:** 6 HTML files + assets

### Backend (Local)

- **URL:** <http://localhost:5000>
- **Location:** Your machine
- **Runs 24/7:** Manual or scheduled startup
- **SSL:** Optional (for remote access, use ngrok)
- **Cost:** Free
- **Knowledge:** 1,330+ items loaded in memory

---

## 🔧 DETAILED SETUP STEPS

### Step 1: Deploy Frontend

**Option A: Using Automation Script**

```powershell
.\DEPLOY_TO_VERCEL.ps1
```

**Option B: Manual Vercel Deployment**

```powershell
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to production
vercel --prod
```

**Save the URL:** You'll need this in Step 3

### Step 2: Start Backend Locally

**Option A: Simple Start**

```powershell
cd C:\Users\johng\Documents\oscar\backend
python main.py
```

**Option B: Run in Background (Keep Window Open)**

```powershell
cd backend
python main.py
# Keep this terminal window open while working
```

**Option C: Run as Service (Windows)**

Create `START_BACKEND_SERVICE.bat`:

```batch
@echo off
cd C:\Users\johng\Documents\oscar\backend
python main.py
pause
```

Then create a scheduled task to run on startup.

**Verify Backend Started:**

```powershell
# Check if port 5000 is listening
netstat -ano | findstr :5000

# Test health endpoint
curl http://localhost:5000/health
```

### Step 3: Update Frontend Configuration

Edit `orfeas-ai-studio.html` and other HTML files:

```html
<script>
  // ============================================================
  // BACKEND CONFIGURATION - HYBRID SETUP
  // ============================================================

  // LOCAL MACHINE BACKEND (for local development)
  const BACKEND_URL = 'http://localhost:5000';

  // If backend needs remote access (ngrok, etc):
  // const BACKEND_URL = 'http://YOUR_NGROK_URL:5000';

  // API endpoints
  const API_BASE = BACKEND_URL + '/api';
  const HEALTH_ENDPOINT = BACKEND_URL + '/health';
  const WS_URL = BACKEND_URL.replace('http', 'ws');

  console.log('Backend URL:', BACKEND_URL);
</script>
```

### Step 4: Deploy Updated Frontend

```powershell
# Commit changes to GitHub
git add orfeas-ai-studio.html
git commit -m "Configure for hybrid deployment (local backend)"
git push origin main

# Vercel auto-deploys on push
# Wait 30-60 seconds for deployment
```

### Step 5: Test Hybrid Setup

**Test Frontend:**

```
Visit: https://orfeas-ai-studio.vercel.app
Expected: Page loads without errors
```

**Test Backend:**

```powershell
# Check health
curl http://localhost:5000/health

# Test API
curl "http://localhost:5000/api/knowledge/search?query=test"
```

**Test Integration:**

- Open browser console (F12)
- Visit frontend URL
- Check console for API calls
- Verify no CORS errors
- Test search functionality

---

## 🌐 REMOTE ACCESS (Optional)

If you want external access to your local backend, use **ngrok**:

### Install ngrok

```powershell
# Download from: https://ngrok.com/download
# Or via Chocolatey
choco install ngrok
```

### Start ngrok Tunnel

```powershell
ngrok http 5000
```

**Output Example:**

```
Session Status                online
Account                       <your-account>
Version                       3.x.x
Region                        us
Forwarding                    http://abc123.ngrok.io -> http://localhost:5000
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

### Update Frontend for Remote Access

```html
<script>
  // Use ngrok URL for remote access
  const BACKEND_URL = 'https://abc123.ngrok.io';  // Replace with your ngrok URL
  const API_BASE = BACKEND_URL + '/api';
</script>
```

### Deploy & Test

```powershell
# Commit with new URL
git add orfeas-ai-studio.html
git commit -m "Update backend URL to ngrok tunnel"
git push origin main

# Test from anywhere
curl https://abc123.ngrok.io/health
```

---

## 📊 COMPARISON: Local vs Remote Backend

| Feature | Local Only | + ngrok | Full Remote |
|---------|-----------|--------|------------|
| Frontend | Vercel | Vercel | Vercel |
| Backend | Local | Local | Cloud |
| Access | Home network | Anywhere | Anywhere |
| SSL | N/A | ✅ Auto | ✅ Auto |
| Cost | Free | Free | $10-50/mo |
| Uptime | 24/7 (your machine) | 24/7 (your machine) | 99.9% SLA |
| Setup | 5 min | 10 min | 30 min |

---

## 🚨 TROUBLESHOOTING

### Issue: "Cannot GET /api/..."

**Problem:** Frontend can't reach backend
**Causes:**

1. Backend not running on port 5000
2. Wrong URL in frontend config
3. CORS not configured
4. Firewall blocking

**Solution:**

```powershell
# 1. Check backend is running
netstat -ano | findstr :5000

# 2. Verify backend is responsive
curl http://localhost:5000/health

# 3. Check frontend console for CORS errors
# Open: F12 → Console tab

# 4. Enable CORS in backend main.py:
#    CORS(app, resources={r"/api/*": {"origins": "*"}})

# 5. Restart backend
```

### Issue: "Connection refused"

**Problem:** Backend not accessible
**Solution:**

```powershell
# Make sure backend is running
cd backend
python main.py

# If port in use:
lsof -i :5000
# Or on Windows:
netstat -ano | findstr :5000
# Kill the process and restart
```

### Issue: CORS Errors in Console

**Problem:** Browser blocks cross-origin requests
**Solution:**

1. Check backend has CORS enabled
2. Add frontend URL to CORS whitelist:

```python
# In backend main.py
from flask_cors import CORS
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5000",
            "https://orfeas-ai-studio.vercel.app"
        ]
    }
})
```

3. Restart backend
4. Test again

### Issue: WebSocket Connection Failed

**Problem:** Real-time updates not working
**Solution:**

```html
<script>
  // For local backend
  const WS_URL = 'ws://localhost:5000';

  // For ngrok tunnel
  // const WS_URL = 'wss://abc123.ngrok.io';
</script>
```

---

## 📝 KEEPING BACKEND RUNNING

### Option 1: Manual (Simple)

- Keep terminal window open with `python main.py` running
- Stop by pressing Ctrl+C

### Option 2: Scheduled Task (Windows)

Create task to start backend on boot:

```powershell
# Create scheduled task
$taskName = "Start ORFEAS Backend"
$taskPath = "C:\Users\johng\Documents\oscar\backend\main.py"
$pythonExe = "python"

# PowerShell script to run backend
$scriptPath = "C:\Users\johng\Documents\oscar\start_backend.ps1"

# Create script content
$scriptContent = @"
cd C:\Users\johng\Documents\oscar\backend
python main.py
"@

# Save script
$scriptContent | Out-File $scriptPath

# Create scheduled task
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath`""
$trigger = New-ScheduledTaskTrigger -AtStartup
Register-ScheduledTask -TaskName $taskName -Action $action -Trigger $trigger -Force
```

### Option 3: Run as Background Service

Use `nssm` (Non-Sucking Service Manager):

```powershell
# Install nssm
choco install nssm

# Install Python as service
nssm install ORFEASBackend python C:\Users\johng\Documents\oscar\backend\main.py

# Start service
nssm start ORFEASBackend

# Check status
nssm status ORFEASBackend
```

---

## 🔄 WORKFLOW

### Daily Development

1. **Start your machine**
   - Backend auto-starts (if scheduled)
   - Or manually: `cd backend && python main.py`

2. **Make changes to frontend**
   - Edit HTML/CSS/JS locally
   - Test on `https://orfeas-ai-studio.vercel.app`

3. **Test with backend**
   - Verify `http://localhost:5000/health` responds
   - Test API calls in browser console
   - Check WebSocket connections

4. **Commit & push**
   - `git add .`
   - `git commit -m "description"`
   - `git push origin main`

5. **Vercel auto-deploys**
   - Website updates instantly
   - No manual deployment needed

6. **Keep backend running**
   - Leave terminal open
   - Or keep scheduled task active

---

## 🎯 SUMMARY

### What You Get

✅ **Frontend:**

- Hosted globally on Vercel CDN
- Auto-deploys from GitHub
- Free SSL/TLS
- Fast loading worldwide
- URL: <https://orfeas-ai-studio.vercel.app>

✅ **Backend:**

- Running on your local machine
- Full control and debugging
- No cloud costs
- All 1,330+ knowledge items in memory
- URL: <http://localhost:5000>

✅ **Hybrid Benefits:**

- **Development:** Test everything locally before production
- **Cost:** Free tier only (Vercel frontend)
- **Control:** Backend on your machine
- **Easy Testing:** Quick iteration cycle
- **Scalable:** Switch to cloud backend anytime

### Cost Breakdown

| Item | Cost |
|------|------|
| Vercel (Frontend) | $0 (free tier) |
| Local Backend | $0 |
| Domain (Optional) | $1-5/year |
| **TOTAL** | **$0** |

---

## 📞 SUPPORT

**Need help?**

1. Check troubleshooting section above
2. Verify both services running:
   - Frontend: <https://orfeas-ai-studio.vercel.app>
   - Backend: <http://localhost:5000/health>

3. Check browser console (F12)
4. Check backend terminal for errors

**Resources:**

- Vercel Docs: <https://vercel.com/docs>
- Flask Docs: <https://flask.palletsprojects.com>
- ngrok Docs: <https://ngrok.com/docs>

---

## ✅ VERIFICATION CHECKLIST

- [ ] Vercel CLI installed
- [ ] Frontend deployed to Vercel
- [ ] Backend running on localhost:5000
- [ ] Frontend URL notes: `_________________`
- [ ] Backend responding to health checks
- [ ] Frontend HTML updated with backend URL
- [ ] Frontend re-deployed on Vercel
- [ ] API calls working (check browser console)
- [ ] WebSocket connections established
- [ ] Search functionality working
- [ ] Real-time updates showing
- [ ] No CORS errors in console

---

**Status:** ✅ HYBRID DEPLOYMENT READY
**Next Step:** Run `.\DEPLOY_TO_VERCEL.ps1` then start backend locally
**Time to Live:** 15 minutes total
**Cost:** $0

🚀 **Your hybrid system is ready to deploy!**
