# ORFEAS AI Studio - System Architecture & Troubleshooting

## How It All Works Together

### 1. GitHub Pages (Frontend Hosting)

- **What runs here:** HTML5 + JavaScript UI
- **Where:** GitHub's servers (Ubuntu)
- **Workflow:** `.github/workflows/pages.yml`
- **Deployment:** Automatic when you push to `main` branch
- **URL:** https://apapadopoulos22.github.io/orfeas-ai-studio
- ✅ **Status:** Working (pages.yml is correct)

### 2. Your Local Backend (Processing)

- **What runs here:** Python Flask API + GPU processing
- **Where:** Your Windows machine (localhost:5000)
- **Process:** `python backend/main.py`
- **CORS:** Enabled and working
- ✅ **Status:** Running (verified working)

### 3. Ngrok Tunnel (Bridge)

- **What does it:** Makes localhost:5000 accessible on the internet
- **Where:** Ngrok's servers
- **URL:** https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev
- **Process:** ngrok.exe (running)
- ✅ **Status:** Active and forwarding

## Complete Data Flow

```
Browser (GitHub Pages)
    ↓
https://apapadopoulos22.github.io/orfeas-ai-studio (Static files)
    ↓
User uploads image
    ↓
JavaScript calls:
    https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev/api/upload-image
    ↓
Ngrok forwards to your machine:
    http://localhost:5000/api/upload-image
    ↓
Flask API processes
    ↓
Returns response
    ↓
Browser shows result
```

## Verification Checklist

### Step 1: Verify All Services Running

- [ ] Python backend: `netstat -ano | findstr :5000` → should show LISTENING
- [ ] Ngrok process: `Get-Process ngrok` → should show running process
- [ ] Ngrok tunnel active: Check http://localhost:4040 in browser

### Step 2: Clear Browser Cache & Refresh

- [ ] Press Ctrl+Shift+Delete (Clear browsing data)
- [ ] Select "All time" and "Cookies and other site data"
- [ ] Hard refresh: Ctrl+Shift+R

### Step 3: Test Upload

- [ ] Open https://apapadopoulos22.github.io/orfeas-ai-studio
- [ ] Press F12 → Console tab
- [ ] Upload an image
- [ ] Look for messages like:
  - `[CONFIG] API_BASE: https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev`
  - `[UPLOAD] Starting upload to: ...`
  - `[UPLOAD] Response received: 200`

### Step 4: Check for Errors

If you see errors, note:

- [ ] Error message (copy exact text)
- [ ] HTTP status code (200, 404, 500, etc.)
- [ ] Whether backend is responding at all

## Common Issues & Solutions

### Issue: "Cannot connect to backend server"

**Causes:**

1. Backend not running
2. Ngrok not running
3. Ngrok tunnel URL changed
4. CORS blocked (check browser console)

**Solutions:**

1. Check `python` process running: `Get-Process python`
2. Check `ngrok` process running: `Get-Process ngrok`
3. Check ngrok URL: `Invoke-RestMethod http://localhost:4040/api/tunnels`
4. Check browser console for CORS errors (F12 → Console)

### Issue: "Mixed Content Warning"

**Cause:** Browser blocks HTTP requests from HTTPS pages
**Solution:** All requests go over HTTPS (ngrok URL is HTTPS) ✓

### Issue: Browser still showing old version

**Cause:** Browser cache or CDN cache
**Solution:**

1. Hard refresh: Ctrl+Shift+Delete → all time → delete
2. Wait 5 minutes (GitHub Pages CDN)
3. Hard refresh again: Ctrl+Shift+R

## GitHub Pages Workflow Explanation

The `.github/workflows/pages.yml` is **correct as-is**. It:

- ✅ Runs on Ubuntu (fine for static files)
- ✅ Deploys to GitHub Pages
- ✅ Doesn't need Python or Windows
- ✅ Triggers automatically on git push

**Why it's NOT running your backend:**

- Backend is NOT supposed to run on GitHub Pages
- Backend runs on YOUR Windows machine
- GitHub Pages just hosts the HTML/JS frontend
- Ngrok bridges the gap to your backend

## Quick Test Commands

```powershell
# Check backend is listening
netstat -ano | findstr :5000

# Check ngrok is running
Get-Process ngrok

# Check ngrok tunnel
Invoke-RestMethod http://localhost:4040/api/tunnels

# Test backend directly
Invoke-RestMethod "http://127.0.0.1:5000/api/models-info" -Headers @{'ngrok-skip-browser-warning'='true'}

# Test ngrok URL from internet
Invoke-RestMethod "https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev/api/models-info" -Headers @{'ngrok-skip-browser-warning'='true'}
```

## Files to Keep Running

1. **Terminal 1: Backend**

   ```powershell
   cd c:\Users\johng\Documents\oscar\backend
   python -u main.py
   ```

2. **Terminal 2: Ngrok**

   ```powershell
   cd c:\Users\johng\Documents\oscar
   .\ngrok http 5000
   ```

Keep both running while using the site. If either stops, connection breaks.

---

**Status: System is configured correctly! The issue is either cache or a specific error visible in browser console.**
