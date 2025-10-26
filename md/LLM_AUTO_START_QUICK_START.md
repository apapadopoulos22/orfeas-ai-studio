# LLM Auto-Start Quick Start

Get ORFEAS AI Studio with automatic Ollama startup in 3 commands

---

## One-Line Start

```powershell
cd c:\Users\johng\Documents\oscar\backend ; python main.py
```

That's it! Ollama will auto-start.

---

## What Happens

1. Server starts
2. Ollama **automatically starts** (no manual work needed)
3. Model **automatically downloads** if missing (first time)
4. Text-to-Image ready to use
5. Visit: `http://localhost:5000/studio`

---

## Expected Output

```text
[ORFEAS] Local LLM initialized successfully!
   Endpoint: http://localhost:11434
   Model: mistral
```

✅ LLM is ready!

---

## Configuration

### Disable LLM (Optional)

```bash
set LOCAL_LLM_ENABLED=false
python backend/main.py
```

### Change Model (Optional)

```bash
set LOCAL_LLM_MODEL=neural-chat
python backend/main.py
```

### Increase Timeout (Slow Hardware)

```bash
set LOCAL_LLM_STARTUP_TIMEOUT=120
python backend/main.py
```

---

## Browser Usage

1. Open `http://localhost:5000/studio`
2. Click **Image** → **Text to Image (Bob AI)**
3. Enter prompt: _"A beautiful sunset over mountains"_
4. Click **Generate**
5. Image appears instantly (powered by auto-started Ollama)

---

## Troubleshooting

### Not Starting

```bash
# Check if Ollama installed
where ollama

# Manual start test
ollama serve
```

### Port 11434 Already in Use

```bash
# Stop old Ollama
taskkill /IM ollama.exe /F

# Restart server
python backend/main.py
```

### Slow First Run

That's normal! Model downloads on first start (~2-5 min). Subsequent starts are instant.

---

## Files Modified

| File | Change | Lines |
|------|--------|-------|
| `main.py` | Added LLM import | 76 |
| `main.py` | Added initialization | 5938 |
| `main.py` | Added shutdown handler | 1227 |
| `llm_local_integration.py` | Created (NEW) | 1-370 |

---

## Implementation Summary

✅ **Automated Ollama Startup** - No manual commands needed
✅ **Cross-Platform** - Windows/Linux/macOS supported
✅ **Graceful Shutdown** - Clean exit on server stop
✅ **Error Handling** - Comprehensive logging and fallbacks
✅ **Model Auto-Download** - Pulls missing models automatically
✅ **Health Checks** - Validates LLM readiness before use

---

For full details, see: [LLM_AUTO_START_GUIDE.md](LLM_AUTO_START_GUIDE.md)
