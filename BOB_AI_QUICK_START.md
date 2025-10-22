# Bob AI Quick Start Guide

## What's New

✨ **Bob AI is now your local AI assistant!**

All 4 user requirements have been implemented:

1. ✅ **Enabled by Default** - No configuration needed, Bob AI is ready to go

2. ✅ **Named "Bob AI"** - Professional branding throughout the system

3. ✅ **Chat Notifications** - Visual feedback when Bob AI responds

4. ✅ **Model Dropdown** - Easy model selection in the chat interface

## Quick Start (3 Steps)

### Step 1: Start Ollama

```bash
ollama serve

```text

*Ollama will start on `http://localhost:11434`*

### Step 2: Start Backend

```bash
cd c:\Users\johng\Documents\oscar
python backend/main.py

```text

*Backend will start on `http://localhost:5000` with Bob AI enabled automatically*

### Step 3: Open Chat Interface

```text
Open in browser: bob-ai-chat.html
(Or navigate to: http://localhost:5000/bob-ai-chat.html)

```text

## What You'll See

### Chat Interface

```text
┌─────────────────────────────────────┐
│ 🟢 Bob AI - Local AI Assistant      │
│                                     │
│ 🤖 AI Model: ▼ Bob AI (Local)      │
├─────────────────────────────────────┤
│                                     │
│ 👋 Hello! I'm Bob AI, your local AI │
│    assistant. I run privately on    │
│    your machine using Ollama and    │
│    Mistral. Ask me anything!        │
│                                     │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ Type your message here...        │ │
│ └─────────────────────────────────┘ │
│                        [Send 🚀]    │
└─────────────────────────────────────┘

```text

## Features

### 🎯 Model Selection

- **Bob AI (Local - Fast & Private)** - Selected by default
- GPT-4 - Coming Soon (placeholder)
- Claude - Coming Soon (placeholder)

### 💬 Real-Time Chat

- Type messages and press Enter
- Bob AI responds with typing indicator
- See response time in console

### ✨ Visual Notifications

When Bob AI is processing:

```text
✨ Bob AI is responding from your local machine...

```text

(Auto-dismisses after 3 seconds)

### 🏷️ Model Badge

Each response shows the model name:

```text
Bob AI - Local Assistant
"Your response here..."

```text

## API Endpoints

### Check Status

```bash
curl http://localhost:5000/api/local-llm/status

```text

Response:

```json
{
    "enabled": true,
    "available": true,
    "model": "Bob AI",
    "internal_model": "mistral"
}

```text

### Send Message

```bash
curl -X POST http://localhost:5000/api/local-llm/generate \

  -H "Content-Type: application/json" \
  -d '{"prompt": "What is 2+2?", "max_tokens": 2048}'

```text

Response:

```json
{
    "response": "2 + 2 = 4",
    "model": "Bob AI",
    "source": "local",
    "latency_ms": 1234
}

```text

## Troubleshooting

### ❌ "Bob AI is not available"

**Problem**: Status shows `"available": false`

**Solution**:

1. Check Ollama is running: `ollama list`

2. Install Mistral: `ollama pull mistral`

3. Verify port 11434 is open

4. Check logs for errors

### ❌ "Cannot connect to server"

**Problem**: Chat interface shows connection error

**Solution**:

1. Verify backend is running on port 5000

2. Clear browser cache and reload

3. Check firewall settings

4. Verify `http://localhost:5000/health` responds

### ❌ "Bob AI is responding but very slowly"

**Problem**: Responses take more than 10 seconds

**Solution**:

1. Check system resources (CPU, RAM, GPU)

2. Verify Ollama is not processing other requests

3. Try shorter prompts

4. Reduce `max_tokens` parameter

### ❌ Still shows "mistral" instead of "Bob AI"

**Problem**: Old version still in memory

**Solution**:

1. Restart backend: Stop and run `python backend/main.py` again

2. Clear browser cache: Ctrl+Shift+Del → Select "All time"

3. Close and reopen bob-ai-chat.html

4. Check backend logs for "Bob AI" initialization message

## Browser Compatibility

✅ **Fully Supported**:

- Chrome/Chromium 90+
- Firefox 88+
- Edge 90+
- Safari 14+

⚠️ **Partial Support**:

- Internet Explorer - Not supported
- Mobile browsers - Responsive but not optimized

## Performance Expectations

| Operation | Expected Time | Status |
|-----------|----------------|--------|
| Backend startup | 2-5 seconds | ✅ Fast |
| First message | 3-8 seconds | ✅ Normal |
| Follow-up messages | 1-5 seconds | ✅ Normal |
| Status check | <100ms | ✅ Very Fast |
| Ollama not running | ~5 seconds timeout | ⚠️ Expected |

## Next Steps

### Try These Prompts with Bob AI

1. **"Explain quantum computing in simple terms"**

   - Tests comprehension and explanation ability

2. **"Write a Python function to calculate fibonacci numbers"**

   - Tests code generation

3. **"What are the top 5 tips for productive work?"**

   - Tests reasoning and advice

4. **"Summarize the key points of [topic]"**
   - Tests summary capability

### Pro Tips

- **Typing Indicator**: Helps you know when Bob AI is thinking
- **Response Time**: Console logs show latency (F12 → Console)
- **Model Badge**: Always shows "Bob AI" for your local assistant
- **Notification Banner**: Purple gradient notification appears automatically

## Files & Locations

| File | Location | Purpose |
|------|----------|---------|
| `bob-ai-chat.html` | Root directory | Chat interface |
| `backend/main.py` | backend/ | Flask backend |
| `backend/local_llm_router.py` | backend/ | LLM routing logic |
| `backend/llm_routes.py` | backend/ | API endpoints |

## Environment Variables (Optional)

These are now set by default, but can be overridden:

```bash

## Enable/disable local LLM (default: true)

ENABLE_LOCAL_LLMS=true

## Ollama server address (default: http://localhost:11434)

LOCAL_LLM_SERVER=http://localhost:11434

## Model name for Ollama (default: mistral)

LOCAL_LLM_MODEL=mistral

## Temperature for responses (default: 0.3)

LOCAL_LLM_TEMPERATURE=0.3

## Maximum tokens per response (default: 2048)

LOCAL_LLM_MAX_TOKENS=2048

```text

## Getting Help

### Common Issues

1. **Backend won't start**

   - Check Python is installed: `python --version`
   - Check requirements: `pip install -r backend/requirements.txt`
   - Check port 5000 is available: `netstat -ano | findstr :5000`

2. **Ollama won't start**

   - Download from: https://ollama.ai
   - Check port 11434: `netstat -ano | findstr :11434`
   - Run from command line to see errors

3. **Chat interface doesn't load**

   - Try direct file path: `file://c:/Users/johng/Documents/oscar/bob-ai-chat.html`
   - Or through browser: `http://localhost:5000/bob-ai-chat.html`
   - Check browser console for errors: F12

### Getting More Info

Check the comprehensive guide:

- 📄 `BOB_AI_IMPLEMENTATION_SUMMARY.md` - Full technical details

## Summary

🎉 **Bob AI is ready to use!**

- **Default behavior**: Enabled automatically on startup
- **User-friendly name**: "Bob AI" throughout the interface
- **Visual feedback**: Clear notifications when active
- **Easy selection**: Model dropdown for future expansion
- **Local processing**: All responses processed on your machine

Start chatting with Bob AI today! 🚀
