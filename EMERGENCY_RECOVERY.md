# ORFEAS AI STUDIO - EMERGENCY RECOVERY GUIDE

**Date:** October 27, 2025
**Issue:** Mojibake encoding corruption + Backend connection issues
**Status:** DIAGNOSING

## 🔍 DIAGNOSIS

### What Happened

1. **Mojibake Corruption** - UTF-8 encoding errors in Python files (characters like `Ã¢â‚¬` instead of proper text)
2. **Backend logs show corrupted emoji** - LLM initialization shows garbled Unicode
3. **Frontend connection likely broken** - Due to corrupted API response handling

### Root Cause

- File encoding was corrupted (possibly from formatter or bad merge)
- Backend main.py has UTF-8 BOM or mixed encoding
- Special characters in comments/strings were double-encoded

---

## ✅ IMMEDIATE FIXES (Try in Order)

### Fix #1: Restart Backend with Clean Output (2 minutes)

```powershell
# Stop any running Python processes
Stop-Process -Name python -Force -ErrorAction SilentlyContinue

# Wait a moment
Start-Sleep -Seconds 2

# Start backend with fresh logging
cd c:\Users\johng\Documents\oscar\backend
$env:PYTHONIOENCODING="utf-8"
python main.py 2>&1 > backend_clean.log
```

**Expected:** Backend should start with clear logs in `backend_clean.log`

### Fix #2: Check Frontend HTML Encoding (5 minutes)

Open browser console (F12) and run:

```javascript
// Check if API connection works
fetch('http://127.0.0.1:5000/health')
  .then(r => r.json())
  .then(d => console.log('✅ Backend connection OK:', d))
  .catch(e => console.error('❌ Backend error:', e))
```

**Expected:** Should see `✅ Backend connection OK` with JSON data

### Fix #3: Clean UTF-8 Encoding in Python Files (10 minutes)

If backend logs are still corrupted, run this PowerShell script:

```powershell
# Fix encoding on Python files
$files = Get-ChildItem c:\Users\johng\Documents\oscar\backend -Filter "*.py" -Recurse

foreach ($file in $files) {
    # Read file as UTF-8
    $content = Get-Content $file -Encoding UTF8 -Raw

    # Remove BOM if present
    if ($content[0] -eq 0xFEFF) {
        $content = $content.Substring(1)
    }

    # Write back without BOM
    [System.IO.File]::WriteAllText($file.FullName, $content, [System.Text.UTF8Encoding]$false)
    Write-Host "✓ Fixed: $($file.Name)"
}

Write-Host "✅ All Python files cleaned"
```

---

## 🔧 TROUBLESHOOTING STEPS

### Step 1: Verify Backend is Actually Running

```powershell
# Check for Python process
Get-Process python -ErrorAction SilentlyContinue | Select-Object ProcessName, Id

# Expected: Shows python process with ID

# Check if port 5000 is open
netstat -ano | findstr :5000

# Expected: Shows LISTENING on :5000
```

### Step 2: Test Backend Health Manually

```powershell
# Simple health check
$response = Invoke-WebRequest -Uri 'http://127.0.0.1:5000/health' -UseBasicParsing -ErrorAction SilentlyContinue
$response.StatusCode  # Should show: 200

# Check response content
$response.Content     # Should show JSON with status info
```

### Step 3: Check for Encoding Issues in main.py

```powershell
# View first line hex dump to check for UTF-8 BOM
Get-Content c:\Users\johng\Documents\oscar\backend\main.py -Encoding Byte -TotalCount 4 | ForEach-Object { "$_".PadLeft(3, ' ') }

# Expected: EF BB BF (BOM) is FINE, Python handles it
# Any other prefix might indicate corruption
```

---

## 📋 COMMON SYMPTOMS & FIXES

| Symptom | Cause | Fix |
|---------|-------|-----|
| Backend logs show `Ã¢â‚¬` instead of emoji | UTF-8 encoding mismatch | Set `PYTHONIOENCODING=utf-8` env var |
| Frontend says "backend not found" | CORS or connection error | Check health endpoint with curl |
| API returns mojibake in response | Python file encoding corrupted | Run Fix #3 above |
| Models fail to load | Import error from corrupted file | Check `hunyuan_integration.py` encoding |
| WebSocket won't connect | Backend not serving `/socket.io/` | Verify backend is on 127.0.0.1:5000 |

---

## 🚀 QUICK RECOVERY SCRIPT

Save this as `recovery.ps1`:

```powershell
# ORFEAS Emergency Recovery Script
# Fixes encoding and restarts backend

Write-Host "🔧 ORFEAS AI Emergency Recovery Started..." -ForegroundColor Cyan

# 1. Kill all Python processes
Write-Host "Stopping Python processes..." -ForegroundColor Yellow
Stop-Process -Name python -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# 2. Set environment variables
Write-Host "Setting environment..." -ForegroundColor Yellow
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUNBUFFERED = "1"
$env:ORT_TENSORRT_UNAVAILABLE = "1"
$env:XFORMERS_DISABLED = "1"

# 3. Start backend
Write-Host "🚀 Starting backend..." -ForegroundColor Green
cd c:\Users\johng\Documents\oscar\backend
python main.py

# Backend is now running on http://127.0.0.1:5000
```

**To run:**

```powershell
.\recovery.ps1
```

---

## ✨ VERIFICATION CHECKLIST

After running fixes, verify:

- [ ] Backend starts without Python errors
- [ ] Logs show `[ORFEAS]` messages (not corrupted mojibake)
- [ ] Can reach `http://127.0.0.1:5000/health` and get JSON response
- [ ] Frontend HTML loads without CORS errors
- [ ] Browser console shows ✅ health check passing
- [ ] Can upload an image and see progress
- [ ] 3D model generation works

---

## 📞 IF STILL BROKEN

If issues persist, collect these diagnostics:

```powershell
# 1. Backend error log
type c:\Users\johng\Documents\oscar\backend\logs\backend_requests.log | head -100

# 2. Python version
python --version

# 3. Check file encoding on main.py
file c:\Users\johng\Documents\oscar\backend\main.py

# 4. Test import
python -c "import main; print('✅ Import OK')" 2>&1
```

---

## 📖 REFERENCES

- **Backend startup:** `.github/copilot-instructions.md` → "CRITICAL PATTERNS"
- **Environment setup:** `backend/.env.example`
- **Deployment:** `PRODUCTION_DEPLOYMENT_GUIDE.md`

---

**Last Updated:** October 27, 2025
**Next Step:** Run Fix #1 above, then verify using Step 1 checklist
