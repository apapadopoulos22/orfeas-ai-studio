# Text to Image Tool - Quick User Guide

## Overview

The **Text to Image** tool lets you generate images directly from text descriptions using AI, powered by your local LLM (Ollama running Stable Diffusion).

```
📝 Prompt Input → ⚙️ Parameters → 🚀 Generate → 🎨 Canvas Display
                                                      ↓
                                            Edit & Export
```

## How to Use

### 1️⃣ Enter Your Prompt

Write a descriptive text about what image you want to generate:

**Examples:**

- "A red apple on a wooden table with natural sunlight"
- "Modern office space with large windows and plants"
- "Fantasy dragon perched on a mountain peak at sunset"
- "Professional 3D product mockup of a smartphone"

**Tips for better results:**

- Be specific and detailed
- Include style, lighting, and mood
- Mention materials and textures
- Use quality descriptors ("high quality", "detailed", "professional")

### 2️⃣ Adjust Generation Parameters

**Generation Steps** (10-100, default 50)

- Controls detail level and quality
- 30 steps: Fast (1-2 min), good for previews
- 50 steps: Balanced (3-5 min) ⭐ **Recommended**
- 75+ steps: High quality (5-10 min), more details

**Guidance Scale** (1-20, default 7.5)

- Controls how strictly to follow your prompt
- Lower (5-6): More creative interpretation
- 7.5: Balanced (⭐ **Recommended**)
- Higher (10+): Strict adherence to prompt

**Output Size** (Choose based on use)

- 512×512: Fast, good for previews (1-2 min)
- 768×768: Best balance (3-5 min) ⭐ **Recommended**
- 1024×1024: Highest quality (5-10 min)

### 3️⃣ Generate Image

1. Click **"✨ Generate Image from Text"** button
2. Wait for generation (progress bar shows)
3. Image appears on canvas when ready

### 4️⃣ Edit Generated Image

Once generated, your image appears on the canvas and you can:

✅ **Crop** - Adjust composition
✅ **Apply Filters** - Adjust brightness, contrast, saturation
✅ **Resize** - Change dimensions
✅ **Add Materials** - Apply color overlays
✅ **Enhance** - Further refine with other tools

### 5️⃣ Export

Choose format and quality, then download:

- **PNG** - Best quality, transparency support
- **JPG** - Smaller file size
- **WebP** - Modern format, best compression

## Quick Examples

### Example 1: Quick Product Mockup (2 min)

```
Prompt: "White smartphone mockup on minimalist desk"
Steps: 40
Size: 512×512
Result: Quick concept for review
```

### Example 2: Professional Render (5 min)

```
Prompt: "Luxury product photography, professional lighting, clean background"
Steps: 60
Size: 768×768
Guidance: 8.5
Result: High-quality product image
```

### Example 3: Concept Art (4 min)

```
Prompt: "Fantasy landscape with ancient ruins, magical lighting"
Steps: 50
Size: 768×768
Guidance: 6.5
Result: Creative concept art
```

## Common Settings

| Use Case | Steps | Size | Guidance | Time |
|----------|-------|------|----------|------|
| Quick preview | 30 | 512×512 | 7.5 | 1 min |
| **Balanced** (recommended) | 50 | 768×768 | 7.5 | 4 min |
| High quality | 75 | 1024×1024 | 8 | 8 min |
| Creative | 50 | 768×768 | 6 | 4 min |
| Strict | 50 | 768×768 | 10 | 4 min |

## Troubleshooting

### ❌ "Generation failed - Make sure local LLM is running"

**Solution:**

1. Open terminal
2. Run: `ollama serve`
3. Wait for startup message
4. Try generating again

### ❌ "Very slow generation"

**Solution:**

- Reduce steps to 30-40
- Use smaller size (512×512)
- Check if GPU is being used
- Close other applications

### ❌ "Out of memory"

**Solution:**

- Use 512×512 instead of 1024×1024
- Reduce steps to 30
- Close other programs
- Restart Ollama

## Tips for Success

### 📝 Prompt Writing

- Start simple: "A red apple"
- Add details: "A shiny red apple on a wooden table"
- Add style: "A photorealistic red apple with dramatic lighting"
- Add quality: "A detailed, high-quality red apple in 8K"

### ⚙️ Parameter Tuning

- Start with **defaults** (50 steps, 7.5 guidance, 768×768)
- For **more detail**: Increase steps to 60-75
- For **more creativity**: Decrease guidance to 5-6
- For **fast preview**: Use 512×512 with 30 steps

### 🔄 Workflow

1. Generate 512×512 preview (fast)
2. Check if you like the style
3. Refine prompt based on result
4. Generate final at 768×768 or 1024×1024
5. Edit in studio (crop, filter, etc.)
6. Export

### 💡 Quality Tips

- **Better prompts = Better results** (spend time writing!)
- More steps improve detail (diminishing returns after 70)
- Larger sizes increase fidelity
- Reference specific art styles (e.g., "anime", "photorealistic", "digital art")
- Be consistent in prompt style

## Workflow Integration

```
Generate Image (Text)
    ↓
View on Canvas
    ↓
Apply Edits (Crop, Filter, Resize, Color)
    ↓
Compare Original ↔ Edited (Comparison Panel)
    ↓
Export (PNG/JPG/WebP)
```

All editing tools available after generation:

- ✂️ Crop
- 🎨 Filters (brightness, contrast, saturation)
- 📐 Resize & Scale
- 🎨 Material Colors
- 🎭 Figurine Enhance
- 💾 Export

## Requirements

✅ **Ollama** installed and running
✅ **Stable Diffusion** or **SDXL** model downloaded
✅ **6GB+ GPU memory** recommended
✅ **Modern browser** (Chrome, Firefox, Safari, Edge)

## Getting Started with Ollama

If you don't have Ollama set up yet:

1. **Download Ollama** from [ollama.ai](https://ollama.ai)
2. **Install** and launch
3. **Pull a model**: `ollama pull stable-diffusion` (or `sdxl`)
4. **Run**: `ollama serve`
5. **Generate images** in the studio!

## Performance Expectations

| Setting | Time |
|---------|------|
| 512×512, 30 steps | ~1 minute |
| 512×512, 50 steps | ~1.5 minutes |
| 768×768, 50 steps | ~3-4 minutes |
| 768×768, 75 steps | ~5-6 minutes |
| 1024×1024, 50 steps | ~5-7 minutes |

*Times vary based on GPU and model. First generation may take longer due to model loading.*

## Now You're Ready

1. ✍️ Write your prompt
2. ⚙️ Adjust parameters
3. 🚀 Click generate
4. 🎨 Edit and export
5. 📤 Share your creation!

**Enjoy creating! 🎉**
