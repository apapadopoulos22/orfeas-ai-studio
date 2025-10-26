# Image Processing Studio - Quick Start Guide

**Last Updated:** October 26, 2025

---

## Getting Started (30 Seconds)

1. **Navigate to Image Studio**

   ```
   http://localhost:5000/studio → Click "Image" in navigation
   ```

2. **Upload Image**

   ```
   Drag image to upload zone OR click to browse
   Supports: JPG, PNG, WebP
   ```

3. **Edit & Process**

   ```
   Use tools on left panel to edit
   See real-time preview on right canvas
   ```

4. **Download**

   ```
   Select format (PNG/JPG/WebP)
   Click "Download Image"
   ```

---

## Tools Overview

### Upload & Preview

- Drag-drop or click upload
- See original and current dimensions
- View real-time canvas preview

### Crop Image

- Choose aspect ratio (1:1, 16:9, 4:3, 3:2, freeform)
- Click "Apply Crop" to confirm
- Click "Reset" to revert

### Filters & Effects

**All sliders update in real-time:**

- Brightness: 0% (dark) to 200% (bright)
- Contrast: 0% (flat) to 200% (extreme)
- Saturation: 0% (gray) to 200% (vivid)
- Hue Rotation: 0° to 360° (color shift)
- Blur: 0px to 20px (smooth effect)

Click "Reset All Filters" to restore defaults.

### Resize & Scale

1. Enter new width and height (pixels)
2. Toggle "Maintain aspect ratio" if needed
3. Click "Apply Resize"
4. Dimensions update in real-time

### Material Colors

**8 Preset Colors:**

- Red, Teal, Blue, Orange
- Purple, Green, Gold, Dark Red

**Custom Color:**

1. Click color picker
2. Select any color
3. Click "Apply Custom Color"

**Effect:** 30% opacity overlay (realistic material appearance)

### Bob AI Enhancement

1. Select style:
   - General Enhancement (auto-optimize)
   - Sharpen Details (edge enhance)
   - Upscale Resolution (improve quality)
   - Denoise (remove noise)
2. Click "Enhance with Bob AI"
3. Processing indicator shown

### Figurine Enhance ⭐ (Special Feature)

**Purpose:** Extract single element with clear background in black & white

**Usage:**

1. Upload image of object/figurine
2. Adjust "Threshold" slider (0-255)
   - Lower = More white (lighter elements)
   - Higher = More black (darker elements)
3. Click "Generate Figurine (BW PNG)"
4. Result: Pure B&W image with clear background

**Perfect for:**

- 3D model generation (high contrast)
- Detail enhancement
- Single object extraction
- Material texture analysis

### Export Options

1. **Select Format:**
   - PNG (best quality, larger file)
   - JPG (compressed, smaller file)
   - WebP (modern, best compression)

2. **Adjust Quality:**
   - Slider from 10% to 100%
   - Higher = Better quality, larger file
   - 80% recommended for balance

3. **Download:**
   - Click "Download Image"
   - File saved to Downloads folder
   - Format: `edited-image.{format}`

---

## Workflows

### Basic Editing Flow

```
Upload → Crop → Filter → Resize → Download
```

### Material Visualization

```
Upload → Filter (saturation +50%) → Color Material → Download
```

### 3D Model Preparation

```
Upload → Figurine Enhance (B&W) → Export PNG → Upload to 3D Studio
```

### Professional Enhancement

```
Upload → Filters → Bob AI Enhance → Color Overlay → Download
```

---

## Tips & Tricks

### Tip 1: Aspect Ratio Cropping

For social media or specific formats, use crop presets:

- Instagram: 1:1 (Square)
- YouTube: 16:9 (Widescreen)
- Standard: 4:3 or 3:2

### Tip 2: Figurine Extraction

To isolate objects on plain backgrounds:

1. Use Figurine Enhance with threshold ~128
2. Increase contrast with Filters first (helps threshold)
3. Adjust threshold slider to separate element from background

### Tip 3: Material Preview

Test different colors for 3D prints:

1. Select object image
2. Try each color swatch
3. Preview how material will look
4. Use final color as reference for 3D generation

### Tip 4: Upscaling Workflow

To increase resolution without quality loss:

1. Resize to desired dimensions
2. Apply Bob AI "Upscale Resolution"
3. Sharpen Details (if needed)
4. Export as PNG (lossless)

### Tip 5: Batch Editing

Edit multiple images quickly:

- Use same filter settings (sliders remember position)
- Upload new image
- Apply same filters
- Download each one

---

## Common Tasks

### Task: Make Background Transparent

**Current:** Not yet supported (canvas limitation)
**Workaround:** Use figurine enhance for B&W, then use external tool

### Task: Rotate Image

**Current:** No direct rotation tool
**Workaround:** Use Hue Rotation for color rotation, or external tool

### Task: Flip/Mirror

**Current:** Not yet supported
**Workaround:** Prepare pre-flipped image

### Task: Add Text

**Current:** Not yet supported
**Workaround:** Add text before uploading to Image Studio

### Task: Batch Resize

**Process:**

1. Upload first image
2. Resize to target dimensions
3. Download
4. Upload next image
5. Same resize dimensions should auto-fill
6. Apply and download

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Upload Image | `Ctrl + Click` on upload zone |
| Reset Crop | Click "Reset" button |
| Reset Filters | Click "Reset All Filters" button |
| Focus Width Field | `Tab` from Height field |
| Download Image | `Ctrl + S` after clicking Download |

---

## Troubleshooting

### Q: Image not loading after upload

**A:**

- Check file format (JPG, PNG, WebP only)
- Try a smaller file size
- Refresh browser (F5)
- Check browser console (F12) for errors

### Q: Filters not working

**A:**

- Ensure image is loaded (canvas should be visible)
- Try resetting filters first
- Check that slider values are changing (visible in label)

### Q: Figurine enhance shows wrong threshold

**A:**

- Adjust threshold slider 0-255
- Lower values = more white areas
- Higher values = more black areas
- Find optimal balance for your object

### Q: Downloaded file is too large

**A:**

- Use JPG instead of PNG
- Lower quality slider (try 60-75%)
- Resize image to smaller dimensions first

### Q: Export button disabled

**A:**

- Load an image first (canvas must be active)
- Check all fields are filled
- Try reloading the page

---

## Performance Guide

### Canvas Size Limits

- Maximum: ~4000×4000 pixels
- Recommended: 1000-2000 pixels (fast)
- Performance: Real-time at all sizes

### Filter Performance

- Single filter: <5ms
- All 5 filters: <20ms
- Very fast even on older devices

### Best Settings for Speed

- Resize to 1000px width first
- Use PNG format for export
- Quality 70-80% for balance

---

## Integration with 3D Studio

### Workflow: Image → 3D Model

1. **Edit Image**

   ```
   Image Studio → Upload → Edit → Export PNG
   ```

2. **Generate 3D**

   ```
   3D Studio → Upload same PNG → Generate 3D Model
   ```

3. **Compare**

   ```
   View 3D preview next to original image
   Iterate if needed
   ```

### Special: Figurine to 3D

1. **Extract Element**

   ```
   Image Studio → Upload → Figurine Enhance → Export PNG
   ```

2. **Generate Model**

   ```
   3D Studio → Upload B&W PNG → High quality setting
   → Generate 3D with details
   ```

3. **Result**

   ```
   High-detail 3D model with extracted element
   ```

---

## Keyboard Cheat Sheet

```
F5              - Reload page
F12             - Open developer console
Ctrl+R          - Hard refresh (clear cache)
Tab             - Move to next field
Enter           - Submit (if in form)
Ctrl+Click      - Multi-select
Drag + Drop     - Upload image
```

---

## File Size Reference

| Original | Crop 1:1 | Filter Applied | Resize 512px | Export PNG | Export JPG |
|----------|----------|---|---|---|---|
| 2MB | 1MB | 1MB | 256KB | 512KB | 128KB |
| 5MB | 3MB | 3MB | 625KB | 1.2MB | 350KB |

---

## Support & Issues

### Report Issues

- Check browser console (F12)
- Note error messages
- Include image size and tool used
- Report in: [Support Channel]

### Get Help

- Read inline tooltips (hover over labels)
- Check function descriptions above
- Review workflow examples
- Contact support team

---

## Feature Roadmap

### Coming Soon 🚀

- [ ] Undo/Redo history
- [ ] Rotate image tool
- [ ] Flip/Mirror options
- [ ] Text overlay
- [ ] Brush tools
- [ ] Layer support
- [ ] Batch processing
- [ ] ML-based object detection

### Under Development 🔧

- WebGL filters (10x faster)
- Advanced color grading
- Histogram view
- Batch resize tool

---

**Thank you for using ORFEAS Image Processing Studio!**

*For more information, see IMAGE_EDITOR_IMPLEMENTATION.md*
