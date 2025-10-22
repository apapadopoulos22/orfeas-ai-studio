# [LAUNCH] QUICK START: ULTIMATE TEXT-TO-IMAGE

## # # [FAST] GET STARTED IN 5 MINUTES

## # # Option 1: FREE MODE (NO API KEYS)

## # # Pollinations.ai is FREE and works immediately

```bash

## 1. Start ORFEAS

cd "C:\Users\johng\Documents\Erevus\orfeas"
.\START_ORFEAS_AUTO.ps1

## 2. Open browser to orfeas-studio.html

## 3. Enter prompt and click "Generate Image"

## [OK] Done! No configuration needed

```text

**Uses:** Pollinations.ai (FREE, unlimited, no signup)

---

## # # Option 2: MAXIMUM POWER MODE [ORFEAS]

## # # Get API keys for best quality models

## # # Step 1: HuggingFace Token (RECOMMENDED)

```bash

## 1. Visit: https://huggingface.co/settings/tokens

## 2. Click "New token"

## 3. Select "Fine-grained"

## 4. Enable "Make calls to Inference Providers"

## 5. Copy token

## 6. Set environment variable

$env:HF_TOKEN="hf_xxxxxxxxxxxxxxxxxxxxx"

## OR add to backend/.env file

HF_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxx

```text

**Gives you:** FLUX.1-dev (best quality), SDXL, SD 1.5

## # # Step 2: Stability AI Key (OPTIONAL)

```bash

## 1. Visit: https://platform.stability.ai/account/keys

## 2. Click "Create API Key"

## 3. Copy key

## 4. Set environment variable

$env:STABILITY_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxx"

## OR add to backend/.env

STABILITY_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxx

```text

**Gives you:** SDXL 1.0, SD3 (premium quality)

---

## # # [LAB] TEST IT

## # # Quick Test (Python)

```bash
cd backend
python ultimate_text_to_image.py

```text

**Output:** `test_ultimate_generation.png` (majestic lion)

## # # Full Integration Test (Web)

```bash

## 1. Start backend

cd "C:\Users\johng\Documents\Erevus\orfeas"
.\START_ORFEAS_AUTO.ps1

## 2. Open browser console (F12)

## 3. Test generation

## - Enter: "A majestic lion on a mountain at sunset"

## - Style: Realistic

## - Click: Generate Image

## 4. Watch console for progress

## [ORFEAS] Initializing ULTIMATE AI engine...

## [ART] Generating with best AI models...

## [OK] Generation successful

```text

---

## # # [STATS] VERIFY PROVIDERS

## # # Check Available Providers

```python
from ultimate_text_to_image import get_ultimate_engine

engine = get_ultimate_engine()
stats = engine.get_provider_stats()

for provider, data in stats.items():
    print(f"{provider}: {data['status']}")

```text

## # # Output

```text
huggingface: available (if HF_TOKEN set)
pollinations: available (always!)
stability: available (if API key set)
automatic1111: available (if running locally)
replicate: unavailable (not configured)

```text

---

## # # [SETTINGS] CONFIGURATION OPTIONS

## # # Quality Modes

```python

## BEST MODE (default) - Highest quality, tries all providers

image_bytes = engine.generate_ultimate(
    prompt="Epic dragon",
    quality_mode="best"  # 30-120 seconds
)

## BALANCED MODE - Good quality, faster

image_bytes = engine.generate_ultimate(
    prompt="Epic dragon",
    quality_mode="balanced"  # 15-60 seconds
)

## FAST MODE - Quick generation

image_bytes = engine.generate_ultimate(
    prompt="Epic dragon",
    quality_mode="fast"  # 5-20 seconds
)

```text

## # # Styles Available

```python
styles = [
    "realistic",    # Photorealistic, 8K
    "artistic",     # Oil painting style
    "anime",        # Manga/anime art
    "cyberpunk",    # Neon, futuristic
    "fantasy",      # Magical, epic
    "cinematic",    # Movie still quality
    "3d_render",    # 3D CGI render
    "minimalist"    # Clean, simple
]

```text

---

## # # [CONFIG] TROUBLESHOOTING

## # # Issue: "All providers failed"

## # # Fix

1. Check internet connection

2. Verify API keys (if using)

3. Try FREE mode (Pollinations always works)

## # # Issue: "HuggingFace model loading"

**Solution:** Wait 20-30 seconds, model is starting up

## # # Issue: "AUTOMATIC1111 not available"

**Solution:** Install and run Stable Diffusion WebUI:

```bash

## Download: https://github.com/AUTOMATIC1111/stable-diffusion-webui

## Run: webui-user.bat

## Access: http://127.0.0.1:7860

```text

## # # Issue: Slow generation

## # # Solutions

1. Use `quality_mode="fast"`

2. Use smaller resolution (512x512)

3. Reduce steps (20-30)

---

## # # [METRICS] PERFORMANCE TIPS

## # # Fastest Generation

```python
image_bytes = engine.generate_ultimate(
    prompt="Quick test",
    width=512,
    height=512,
    steps=20,
    quality_mode="fast"
)

## Result: 5-10 seconds

```text

## # # Best Quality

```python
image_bytes = engine.generate_ultimate(
    prompt="Masterpiece artwork",
    width=1024,
    height=1024,
    steps=75,
    guidance_scale=8.0,
    quality_mode="best"
)

## Result: 60-120 seconds (but AMAZING quality)

```text

## # # Balanced (Recommended)

```python
image_bytes = engine.generate_ultimate(
    prompt="Beautiful landscape",
    width=768,
    height=768,
    steps=40,
    quality_mode="balanced"
)

## Result: 20-40 seconds (excellent quality)

```text

---

## # # [OK] SUCCESS CRITERIA

After setup, you should see:

## # # Console Output

```text
[ORFEAS] ULTIMATE TEXT-TO-IMAGE ENGINE INITIALIZED
[OK] Configured providers: huggingface, stability
[WEB] Always available: Pollinations.ai (FREE, no API key)

```text

## # # Generation Success

```text
[ART] Generating with HuggingFace: black-forest-labs/FLUX.1-dev
[OK] HuggingFace generation successful (FLUX.1-dev)
[OK] SUCCESS: huggingface | Time: 45.2s | Quality: 0.98
[TROPHY] BEST RESULT: huggingface | Quality: 0.98 | Time: 45.2s

```text

---

## # # [TARGET] NEXT STEPS

1. [OK] **Test with FREE mode** (no setup required)

2. [OK] **Add HuggingFace token** (best quality)

3. [OK] **Add Stability key** (optional, premium)

4. [OK] **Install AUTOMATIC1111** (optional, local)
5. [OK] **Generate amazing images!** [ART]

---

**READY TO CREATE MAGIC?** [ORFEAS]

Open ORFEAS Studio and start generating!
