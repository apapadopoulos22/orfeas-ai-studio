# 🔧 Troubleshooting Guide: Multi-Process Port Binding Conflicts

**Date Created:** October 19, 2025
**Issue Type:** Backend Routing / Process Management
**Severity:** High (causes 404 errors despite correct code)

---

## 📋 Executive Summary

**Problem:** Flask routes return 404 despite logs showing successful blueprint registration.

**Root Cause:** Multiple Flask development server processes binding to the same port (5000), causing requests to randomly hit old processes without the newly registered routes.

**Solution:** Ensure only one backend process is running before testing route changes.

---

## 🔍 Symptoms

### Primary Symptom

- **404 Not Found** on endpoints that logs confirm are registered
- Example: `GET /api/local-llm/status` returns 404
- Logs show: `[DEBUG] LLM Rule -> /api/local-llm/status :: endpoint=local_llm.llm_status methods=['GET']`

### Secondary Symptoms

- Inconsistent behavior: endpoint works sometimes, fails other times
- Fresh code changes not reflected in HTTP responses
- `app.url_map` shows routes registered, but they don't respond
- Health check endpoint works while new endpoints return 404

---

## 🕵️ Detection & Diagnosis

### Step 1: Check for Multiple Processes

### Windows (PowerShell)

```powershell

## Check all Python processes

Get-Process python -ErrorAction SilentlyContinue

## Filter for backend-specific processes

Get-Process python | Where-Object {$_.Path -like "*oscar*"}

```text

**Expected:** 0-1 processes
**Problem:** 2+ processes

### Step 2: Check Port Listeners

### Windows

```powershell
netstat -ano | findstr :5000

```text

### Example Output (PROBLEM)

```text
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    6156
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    3604  ← Multiple listeners!
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    6656

```text

### Expected Output (GOOD)

```text
TCP    0.0.0.0:5000    0.0.0.0:0    LISTENING    3716  ← Only ONE listener

```text

### Step 3: Verify Process Identity

### Windows

```powershell

## Get detailed process info for PID

Get-Process -Id 6156 | Select-Object Id,ProcessName,Path,StartTime

```text

---

## ✅ Resolution Steps

### Quick Fix (Development)

```powershell

## 1. Stop ALL Python processes

Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

## 2. Wait for cleanup

Start-Sleep -Seconds 2

## 3. Verify no processes remain

Get-Process python -ErrorAction SilentlyContinue

## 4. Start single backend instance

cd c:\Users\johng\Documents\oscar\backend
python main.py

## 5. Verify single listener (in separate terminal)

netstat -ano | findstr :5000

## Should show ONLY ONE listener

## 6. Test endpoint

Invoke-WebRequest -Uri "http://localhost:5000/api/local-llm/status"

```text

### Production-Safe Fix

```powershell

## 1. Identify backend processes specifically

$backendProcesses = Get-Process python | Where-Object {$_.Path -like "*oscar*backend*"}

## 2. Log processes before stopping

$backendProcesses | ForEach-Object {
    Write-Host "Stopping PID $($_.Id): $($_.Path)"
}

## 3. Stop only backend processes

$backendProcesses | Stop-Process -Force

## 4. Verify cleanup

Start-Sleep -Seconds 2
netstat -ano | findstr :5000

## 5. Start clean instance

python main.py

```text

---

## 🧪 Verification Checklist

After applying the fix, verify these conditions:

- [ ] **Only ONE Python process** in task manager/process list
- [ ] **Only ONE listener** on port 5000 from `netstat`
- [ ] **Logs show route registration** with correct endpoints
- [ ] **HTTP 200 response** from test endpoints
- [ ] **Correct JSON payload** returned (not 404 HTML)

### Verification Commands

```powershell

## Process count

(Get-Process python -ErrorAction SilentlyContinue).Count  # Should be 1

## Port listener count

(netstat -ano | findstr :5000 | findstr LISTENING).Count  # Should be 1

## Endpoint test

$response = Invoke-WebRequest -Uri "http://localhost:5000/api/local-llm/status"
$response.StatusCode  # Should be 200

```text

---

## 🎯 Prevention Strategies

### 1. Pre-Start Cleanup Script

Create `START_BACKEND_CLEAN.ps1`:

```powershell

#!/usr/bin/env pwsh

## Clean start script for ORFEAS backend

Write-Host "🧹 Cleaning up old processes..." -ForegroundColor Yellow

## Stop existing backend processes

Get-Process python -ErrorAction SilentlyContinue |
    Where-Object {$_.Path -like "*oscar*"} |
    Stop-Process -Force

Start-Sleep -Seconds 2

## Verify cleanup

$remaining = Get-Process python -ErrorAction SilentlyContinue
if ($remaining) {
    Write-Host "⚠️ Warning: $($remaining.Count) Python processes still running" -ForegroundColor Red
    exit 1
}

Write-Host "✅ All processes stopped" -ForegroundColor Green

## Start fresh backend

Write-Host "🚀 Starting backend..." -ForegroundColor Cyan
cd backend
python main.py

```text

### 2. Add Process Check to Startup

Add to `backend/main.py` startup sequence:

```python
import psutil
import sys

def check_existing_processes(port=5000):
    """Check for existing processes on the port"""
    for conn in psutil.net_connections():
        if conn.laddr.port == port and conn.status == 'LISTEN':
            try:
                process = psutil.Process(conn.pid)
                logger.warning(f"[STARTUP] Existing process on port {port}: PID {conn.pid} ({process.name()})")

                # Option 1: Fail fast

                # logger.error(f"[STARTUP] Port {port} already in use - aborting")

                # sys.exit(1)

                # Option 2: Auto-kill (development only)

                if os.getenv('AUTO_KILL_EXISTING', 'false').lower() == 'true':
                    logger.warning(f"[STARTUP] AUTO_KILL_EXISTING=true - terminating PID {conn.pid}")
                    process.terminate()
                    time.sleep(1)
            except psutil.NoSuchProcess:
                pass

## Call during initialization

check_existing_processes(port=5000)

```text

### 3. Deployment Checklist

Add to deployment procedures:

```text

## Backend Deployment Checklist

- [ ] Stop all existing backend processes
- [ ] Verify port 5000 is free (`netstat -ano | findstr :5000`)
- [ ] Clear Python bytecode cache (`rm -rf __pycache__`)
- [ ] Start single backend instance
- [ ] Verify single process listening on port 5000
- [ ] Test health endpoint: `GET /api/health`
- [ ] Test critical endpoints
- [ ] Monitor logs for errors

```text

---

## 🐛 Why This Happens

### Flask Development Server Behavior

The Flask development server (Werkzeug) **allows multiple processes** to bind to the same port in certain conditions:

1. **Different bind addresses:** `0.0.0.0:5000` vs `127.0.0.1:5000`

2. **SO_REUSEADDR socket option:** Allows quick restart after crashes

3. **TIME_WAIT state:** Old connections in cleanup allow new bindings

### Load Balancing Effect

When multiple processes listen:

- OS may round-robin requests across processes
- Requests randomly hit old instances without new routes
- Creates intermittent 404 behavior
- Logs from one process don't reflect state of others

### Development vs Production

- **Development:** Flask's built-in server allows this
- **Production:** WSGI servers (gunicorn, uwsgi) have proper process management
- **Docker:** Single container = single process (problem doesn't occur)

---

## 📚 Related Issues

### Similar Symptoms, Different Causes

1. **Blueprint not imported:** Import error silently caught

   - Check: `from llm_routes import llm_bp` succeeds
   - Verify: `llm_bp` is defined in llm_routes.py

2. **Environment variable not set:** Routes conditionally registered

   - Check: `ENABLE_LOCAL_LLMS=true` in `.env`
   - Verify: `os.getenv('ENABLE_LOCAL_LLMS')` returns 'true'

3. **Wrong url_prefix:** Route registered at different path

   - Check: `url_prefix='/api/local-llm'` in register_blueprint
   - Verify: `app.url_map` shows correct paths

4. **Cached bytecode:** Old .pyc files loaded
   - Fix: `rm -rf __pycache__` or `python -B main.py`

---

## 🔬 Advanced Debugging

### Log Analysis

Add comprehensive startup logging:

```python
def setup_routes(self):
    logger.info("[ROUTE-DEBUG] setup_routes() STARTED")
    logger.info(f"[ROUTE-DEBUG] main module path: {__file__}")

    from llm_routes import llm_bp
    if os.getenv('ENABLE_LOCAL_LLMS', 'false').lower() == 'true':
        self.app.register_blueprint(llm_bp, url_prefix='/api/local-llm')
        logger.info("[LLM] Local LLM routes enabled at /api/local-llm")

        # Dump registered routes

        llm_rules = []
        for rule in self.app.url_map.iter_rules():
            if 'llm' in str(rule).lower():
                llm_rules.append({
                    'endpoint': rule.endpoint,
                    'methods': sorted(rule.methods - {'HEAD', 'OPTIONS'}),
                    'rule': str(rule)
                })

        logger.info(f"[DEBUG] Startup LLM URL rules count: {len(llm_rules)}")
        for r in llm_rules:
            logger.info(f"[DEBUG] LLM Rule -> {r['rule']} :: endpoint={r['endpoint']} methods={r['methods']}")

    total_rules = len(list(self.app.url_map.iter_rules()))
    logger.info(f"[ROUTE-DEBUG] setup_routes() COMPLETED with {total_rules} url rules registered")

```text

### Process Monitoring Script

```python

## check_backend_processes.py

import psutil
import sys

def check_backend_health():
    python_processes = [p for p in psutil.process_iter(['pid', 'name', 'cmdline'])
                       if p.info['name'] == 'python.exe']

    backend_processes = [p for p in python_processes
                        if any('main.py' in str(cmd) for cmd in (p.info['cmdline'] or []))]

    print(f"Total Python processes: {len(python_processes)}")
    print(f"Backend processes: {len(backend_processes)}")

    if len(backend_processes) > 1:
        print("\n⚠️  WARNING: Multiple backend processes detected!")
        for p in backend_processes:
            print(f"  PID {p.info['pid']}: {' '.join(p.info['cmdline'])}")
        return False
    elif len(backend_processes) == 1:
        print(f"\n✅ Single backend process: PID {backend_processes[0].info['pid']}")
        return True
    else:
        print("\n❌ No backend process found")
        return False

if __name__ == "__main__":
    healthy = check_backend_health()
    sys.exit(0 if healthy else 1)

```text

---

## 📖 Key Takeaways

1. **Always verify process count** before testing route changes

2. **Use `netstat` to confirm single listener** on expected port

3. **Flask development server allows multi-binding** - production servers don't

4. **Logs from one process don't reflect state of others**
5. **Kill all backend processes before restart** to ensure clean state
6. **Add process checks to deployment procedures**
7. **Consider auto-kill logic for development environments**

---

## 🔗 References

- **Flask Blueprint Documentation:** https://flask.palletsprojects.com/blueprints/
- **Werkzeug Development Server:** https://werkzeug.palletsprojects.com/server/
- **Socket SO_REUSEADDR:** https://docs.python.org/3/library/socket.html
- **Production WSGI Servers:** gunicorn, uwsgi, mod_wsgi

---

**Last Updated:** October 19, 2025
**Author:** ORFEAS Development Team
**Status:** Active Troubleshooting Guide
