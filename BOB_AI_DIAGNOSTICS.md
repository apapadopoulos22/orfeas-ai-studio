# Bob AI Text-to-Image Diagnostics

## Current Issue: Generation Failure

When Bob AI button is clicked and image generation fails, use this guide to diagnose.

### Architecture

```text
Frontend (Browser)
    ↓ [Enhanced prompt text]
Ollama/Mistral API (/api/local-llm/generate)
    ↓ [Enhanced prompt]
Backend (/api/text-to-image)
    ↓ [Creates job_id, returns immediately]
    → Background Thread
        ↓ [Job created in both dictionaries]
        ↓ [Calls ultimate_engine.generate_ultimate()]
            ↓ Tries HuggingFace providers
            ↓ Tries Stability API
            ↓ Tries Pollinations API
            ↓ Tries AUTOMATIC1111 (local)
            ↓ Falls back to placeholder image
        ↓ [Saves image to /uploads/]
        ↓ [Updates job status to "completed"]
Frontend (polling /api/job-status)
    ↓ [Gets "completed" status]
    ↓ [Displays image]
```

## Troubleshooting Steps

### Step 1: Check Backend is Running

```powershell
# Check if backend is responsive
curl http://localhost:5000/api/models-info
# OR for NGROK deployment
curl https://YOUR_NGROK_URL/api/models-info
```

Expected response: JSON with device info and models

### Step 2: Check Ollama/Mistral is Running

```powershell
# Test prompt enhancement
curl -X POST http://localhost:11434/api/generate `
  -H "Content-Type: application/json" `
  -d '{"model":"mistral","prompt":"test","stream":false}'
```

Expected response: JSON with `response` field

### Step 3: Monitor Backend Logs

```powershell
# In a separate terminal, watch backend logs
cd c:\Users\johng\Documents\oscar
python backend/main.py 2>&1 | Tee-Object -FilePath debug.log
```

Look for these patterns when Bob AI button is clicked:

```text
[ART] Text-to-image request:                    ← Step 1: Request received
[ORFEAS] Calling ultimate_engine.generate_ultimate   ← Step 2: Engine called
[ORFEAS] ultimate_engine returned:              ← Step 3: Engine response
[OK] Image saved successfully:                  ← Step 4: Image saved
[OK] Text-to-image completed:                   ← Step 5: Complete
```

### Step 4: Check Error Messages

If you see `[FAIL]` messages, they indicate:

- **`[FAIL] HuggingFace error`** - HuggingFace API call failed
- **`[FAIL] Pollinations error`** - Pollinations API down
- **`[FAIL] AUTOMATIC1111 connection error`** - Local AUTOMATIC1111 not running
- **`[FAIL] Ultimate engine returned: None`** - All providers failed, fallback failed

### Step 5: Check Image Directory

```powershell
# List generated images
Get-ChildItem c:\Users\johng\Documents\oscar\uploads\
```

Should contain `{job_id}_generated.png` files

### Step 6: Test Text-to-Image API Directly

```powershell
$body = @{
    prompt = "a beautiful sunset over mountains"
    style = "realistic"
    width = 512
    height = 512
    steps = 50
    guidance_scale = 7.0
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://localhost:5000/api/text-to-image" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

Expected response:

```json
{
  "job_id": "uuid-here",
  "status": "processing",
  "message": "Image generation started"
}
```

Then poll job status:

```powershell
# Wait 2 seconds for processing
Start-Sleep -Seconds 2

# Poll status (replace JOB_ID)
Invoke-RestMethod -Uri "http://localhost:5000/api/job-status/JOB_ID"
```

Should eventually return:

```json
{
  "status": "completed",
  "progress": 100,
  "message": "Image generated successfully!",
  "filename": "uuid_generated.png",
  "preview_url": "/api/preview/uuid_generated.png"
}
```

## Error Response Format

When generation fails, you'll see:

```json
{
  "status": "failed",
  "progress": 0,
  "message": "Image generation failed: [error description]",
  "error_type": "TimeoutError|ConnectionError|Exception",
  "error_details": "[full error message]"
}
```

The frontend will show:

```text
❌ Image generation failed:

[ErrorType] error message

Details: Full error details here

Check backend logs for details.
```

## Common Failures and Solutions

### All Providers Fail (Falls Back to Placeholder)

**Symptom:** Image shows warning text, no actual generated image

**Causes:**

- HuggingFace API key invalid or quota exceeded
- All provider APIs unreachable
- Network connectivity issues

**Fix:**

```powershell
# Check provider availability
python -c "
from backend.ultimate_text_to_image import get_ultimate_engine
engine = get_ultimate_engine()
print(engine.get_provider_stats())
"
```

### Timeout Errors

**Symptom:** "Timeout: connection or read exceeded limits"

**Causes:**

- Provider API is slow
- Network is slow
- Model is taking too long to load

**Fix:** Increase timeout in `backend/ultimate_text_to_image.py`:

```python
TIMEOUTS = {
    'slow': (10, 300),  # Increase from 120 to 300
}
```

### Connection Errors

**Symptom:** "Connection error (network unreachable)"

**Causes:**

- Firewall blocking API calls
- VPN not connected
- Provider API is down

**Fix:**

- Check firewall rules
- Verify network connectivity: `ping 8.8.8.8`
- Check provider status page

## Logging Configuration

To increase logging detail:

```python
# In backend/main.py, before app.run():
import logging
logging.basicConfig(level=logging.DEBUG)
logger.setLevel(logging.DEBUG)
```

## Performance Optimization

If generation is too slow:

1. Use "fast" mode:

   ```python
   quality_mode='fast'  # Instead of 'best'
   ```

2. Reduce image size:

   ```python
   width=512, height=512  # Instead of 1024x1024
   ```

3. Reduce steps:

   ```python
   steps=30  # Instead of 50
   ```

## Network Debugging

If behind corporate firewall/VPN:

```powershell
# Test specific provider connectivity
Test-NetConnection "huggingface.co" -Port 443
Test-NetConnection "api.stability.ai" -Port 443
Test-NetConnection "pollinations.ai" -Port 443

# Check DNS resolution
Resolve-DnsName huggingface.co
```

## Recent Fixes (Commit History)

- **2f0f59d** - Fixed race condition: Job created in both dictionaries BEFORE thread starts
- **0a474f8** - Enhanced error diagnostics with traceback logging and detailed error messages
- **788db16** - Fixed job status 404 by checking both dictionaries
- **d619117** - Added comprehensive error handling for JSON parsing and CORS

---

**Next Step:** When you see an error message in the browser, share the error details from:

1. Browser console (F12)
2. Backend logs (terminal where main.py runs)
3. The error alert message text

This will help identify the exact provider/issue.
