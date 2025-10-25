# CORS Fix - Quick Start Guide

## What Was Fixed

Your frontend was getting CORS errors when connecting through ngrok.

**Error:**

```
Access to fetch at 'https://unsaid-ellsworth-uncorrespondingly.ngrok-free.dev/api/models-info'
from origin 'null' has been blocked by CORS policy
```

**Solution:** Added CORS preflight handler to backend

---

## Quick Start

### 1. Start Backend

Option A (Simple):

```bash
cd backend
python main.py
```

Option B (With Auto-Restart):

```bash
python backend_manager.py
```

### 2. Test Locally

```bash
curl http://127.0.0.1:5000/api/health
```

Should return HTTP 200 with JSON response.

### 3. Open Frontend

- Go to: <https://apapadopoulos22.github.io/synexa-style-studio.html>
- Upload an image
- Check console (F12) for CORS errors
- Should now work without CORS blocking

---

## What Changed

### File: `backend/main.py`

**Change 1**: Line 39 - Added import

```python
from flask import Flask, ..., make_response  # Added make_response
```

**Change 2**: Lines 793-805 - Enhanced CORS

```python
CORS(self.app,
     resources={r"/*": {"origins": cors_origins_list}},
     allow_credentials=False,  # Changed from conditional
     expose_headers=["Content-Disposition", "Content-Type", "Content-Length"],  # More headers
     methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],  # Explicit methods
     allow_headers=["Content-Type", "Authorization"])  # Explicit headers
```

**Change 3**: Lines 826-837 - Added preflight handler

```python
@self.app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add("Access-Control-Allow-Origin", "*")
        response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization")
        response.headers.add("Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS,PATCH")
        return response
    return None
```

---

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Port 5000 is listening
- [ ] Health endpoint responds (curl test)
- [ ] ngrok tunnel is active
- [ ] Frontend loads without CORS error
- [ ] 3D generation works

---

## Troubleshooting

### Backend Won't Start

```bash
# Check if port 5000 is already in use
netstat -ano | findstr :5000

# Kill existing process
taskkill /F /PID [PID]

# Try again
python main.py
```

### Still Getting CORS Errors

1. Clear browser cache (Ctrl+Shift+Delete)
2. Hard refresh (Ctrl+Shift+R)
3. Check console for exact error message
4. Verify backend is running on port 5000
5. Verify ngrok tunnel is still active

### Backend Exits Immediately

- This is a known Windows issue with SocketIO
- Use `backend_manager.py` for auto-restart
- Or deploy to Linux/Docker

---

## Files Modified

- `backend/main.py` (3 changes)
- `backend/stl_processor.py` (import improvement)

## Files Created

- `CORS_FIX_COMPLETE.md` - Detailed technical documentation
- `backend_manager.py` - Process manager for Windows

---

## Success - What You Should See

✅ Frontend connects to ngrok backend
✅ No CORS errors in browser console
✅ API calls return data
✅ 3D models generate successfully

---

## Documentation

For detailed technical information, see: `CORS_FIX_COMPLETE.md`

---

**Status**: ✅ CORS fix deployed and ready
**Date**: October 25, 2025
**Backend**: Running on <http://127.0.0.1:5000>
**Frontend**: <https://apapadopoulos22.github.io/synexa-style-studio.html>
