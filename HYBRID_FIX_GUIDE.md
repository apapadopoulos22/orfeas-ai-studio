# Hybrid Deployment - CORS Fix Guide

## Problem Summary

Your frontend (running on Vercel) was trying to connect to `http://127.0.0.1:5000` (localhost), but Vercel is a different origin (`https://orfeas-ai-studio.vercel.app`). This triggered a CORS (Cross-Origin Resource Sharing) error.

**Error Message:**

```
Access to fetch at 'http://127.0.0.1:5000/api/models-info' from origin
'https://orfeas-ai-studio.vercel.app' has been blocked by CORS policy
```

## Solution Applied

### Files Updated (6 total)

1. **synexa-style-studio.html**
   - Changed: `http://127.0.0.1:5000` → ngrok URL
   - Also added `BACKEND_URL` variable support

2. **orfeas-ai-studio.html**
   - Changed: `http://127.0.0.1:5000` → ngrok URL
   - Added `BACKEND_URL` variable support

3. **batch-studio.html**
   - Changed: `http://127.0.0.1:5000` → ngrok URL
   - Supports external `BACKEND_URL` configuration

4. **bob-ai-chat.html**
   - Changed: `http://localhost:5000` → ngrok URL
   - Dynamic backend URL support

5. **orfeas-studio-responsive.html**
   - Changed: `http://localhost:5000` → ngrok URL
   - Uses `BACKEND_BASE` variable

6. **orfeas-studio.html** (Complex update)
   - Updated Content-Security-Policy (CSP) headers
   - Added ngrok domain to allowed resources
   - Updated preconnect links
   - Added dynamic `BACKEND_URL` initialization

### Backend URL Configuration

All files now use this configuration pattern:

```javascript
const BACKEND_URL =
  (typeof window.BACKEND_URL !== "undefined" && window.BACKEND_URL) ||
  "https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev";

const API_BASE = BACKEND_URL + "/api";
const WS_URL = BACKEND_URL.replace("https://", "wss://").replace("http://", "ws://");
```

This allows:

- External configuration via `window.BACKEND_URL` (set by external scripts)
- Fallback to ngrok URL if not configured
- Automatic WebSocket URL generation (https → wss://, http → ws://)

## What You Need to Do

### 1. **Keep ngrok Running**

Open a terminal and run:

```bash
ngrok http 5000
```

This will:

- Expose your local backend on the internet
- Provide the URL: `https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev`
- Keep your backend accessible from Vercel

**Important:** Keep this terminal open while testing. If ngrok closes, the URL stops working.

### 2. **Start Your Backend**

In a new terminal:

```bash
cd backend
python main.py
```

**Requirements:**

- Python 3.11+ running
- All dependencies installed
- Backend listening on `http://localhost:5000`

### 3. **Wait for Vercel Deployment**

After pushing to GitHub, Vercel will:

1. Detect the changes
2. Rebuild your site (2-5 minutes)
3. Deploy to CDN (global)
4. Your changes will be live

**Check Deployment Status:**

- Visit: <https://vercel.com/apapadopoulos22/orfeas-ai-studio>
- Watch for "Production Deployment Complete"

### 4. **Test the Connection**

Once Vercel has deployed:

1. **Visit the frontend:**

   ```
   https://orfeas-ai-studio.vercel.app
   ```

2. **Open browser console (F12):**
   - Look for messages like:

   ```
   [CONFIG] BACKEND_URL: https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev
   [CONFIG] API_BASE: https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev/api
   [HEALTH] Checking backend health at: https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev
   ```

3. **Check for errors:**
   - Look for CORS errors (should be gone now)
   - Look for connection refused errors (means backend isn't running)
   - Look for ngrok page errors (means ngrok URL changed)

## Troubleshooting

### Problem 1: Still Getting CORS Errors

**Cause:** Vercel deployment hasn't finished or old files are cached

**Solution:**

1. Force refresh: `Ctrl+Shift+Delete` (or `Cmd+Shift+Delete` on Mac)
2. Clear browser cache
3. Wait 2-3 minutes for Vercel to fully deploy
4. Try again

### Problem 2: "Failed to fetch" / "Connection refused"

**Cause:** Backend isn't running or ngrok tunnel is closed

**Solution:**

1. Check ngrok is running:

   ```
   # In terminal where ngrok is running, you should see:
   # forwarding https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev
   ```

2. Check backend is running:

   ```
   cd backend
   python main.py
   # Should see: "Running on http://127.0.0.1:5000"
   ```

3. If either is closed, restart them

### Problem 3: ngrok URL Changed

ngrok Free tier sessions expire after 2 hours. When you restart ngrok, you get a new URL.

**Solution:**

1. If this happens, you need to update the HTML files with the new ngrok URL
2. Then push to GitHub
3. Vercel will redeploy

**To make this easier:**

- Consider setting up an environment variable in GitHub
- Or use ngrok's paid tier for a static URL
- Or configure the URL via external config script

### Problem 4: Backend Timeout Errors

**Cause:** 3D generation takes time (60+ seconds)

**Solution:**

1. Check backend logs for actual errors
2. Increase timeout in code if needed
3. Check GPU/VRAM is available

### Problem 5: Empty Console - No Messages

**Cause:** Vercel deployed old cached version

**Solution:**

1. Hard refresh: `Ctrl+Shift+R` (Windows) or `Cmd+Shift+R` (Mac)
2. Wait 2 minutes, then try again
3. Check Vercel deployment status

## Verification Checklist

- [ ] ngrok is running (`ngrok http 5000`)
- [ ] ngrok shows: `forwarding https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev`
- [ ] Backend is running (`python main.py` in backend/)
- [ ] Backend console shows: `Running on http://127.0.0.1:5000`
- [ ] Changes pushed to GitHub (git push origin main)
- [ ] Vercel deployment completed (check Vercel dashboard)
- [ ] Hard refresh frontend (Ctrl+Shift+R)
- [ ] Browser console shows backend URL configuration messages
- [ ] No CORS errors in console
- [ ] API calls appear in Network tab
- [ ] Backend health check passes

## Advanced: Custom Backend URL

If you need to use a different backend URL, you can set it globally:

```html
<script>
  // Set before any ORFEAS scripts load
  window.BACKEND_URL = 'https://your-custom-ngrok-url';
  window.API_BASE = window.BACKEND_URL + '/api';
</script>
```

Add this to the `<head>` section before other scripts.

## Files Changed Summary

```
6 files changed, 788 insertions(+), 715 deletions(-)

Updated:
- synexa-style-studio.html (configured for ngrok)
- orfeas-ai-studio.html (configured for ngrok)
- batch-studio.html (configured for ngrok)
- bob-ai-chat.html (configured for ngrok)
- orfeas-studio-responsive.html (configured for ngrok)
- orfeas-studio.html (CSP headers + config)
```

## Next Steps

1. ✅ HTML files updated (already done)
2. ✅ Pushed to GitHub (already done)
3. ⏳ Waiting for Vercel deployment (1-2 minutes)
4. 🚀 Keep ngrok running
5. 🚀 Keep backend running
6. 🧪 Test when Vercel shows "Production Deployment Complete"

---

**Status:** Ready for Testing
**Last Updated:** October 27, 2025
**Configuration:** Hybrid (Vercel Frontend + Local Backend via ngrok)
