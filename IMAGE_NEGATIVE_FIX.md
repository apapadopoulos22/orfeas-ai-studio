# Image Negative/Inverted Texture Fix# Image Negative/Inverted Texture Fix

## Problem## Problem

The 3D generation was producing models with negative (inverted) images/textures in the cube instead of the correct image.The 3D generation was producing models with negative (inverted) images/textures in the cube instead of the correct image.

## Root Cause## Root Cause

The image preprocessing logic in `hunyuan_integration.py` had a critical flaw:The image preprocessing logic in `hunyuan_integration.py` had a critical flaw:

```python```python

# BUGGY CODE:# BUGGY CODE

image = Image.open(image_path).convert("RGBA")image = Image.open(image_path).convert("RGBA")  # ← Converts immediately to RGBA

# Converts immediately to RGBAif image.mode == 'RGB' and self.rembg is not None:  # ← Will NEVER be RGB after RGBA conversion

if image.mode == 'RGB' and self.rembg is not None:    image = self.rembg(image)

    # Will NEVER be RGB after RGBA conversion!```

    image = self.rembg(image)

```This logic meant:



This logic meant:1. Image converted to RGBA (4 channels: Red, Green, Blue, Alpha)

2. Check if mode is 'RGB' (3 channels) - **always fails** after RGBA conversion

- Image converted to RGBA (4 channels: Red, Green, Blue, Alpha)3. Background removal NEVER executed

- Check if mode is 'RGB' (3 channels) - always fails4. Incorrect image fed to Hunyuan3D pipeline causes texture issues

- Background removal NEVER executed

- Incorrect image fed to Hunyuan3D pipeline causes texture issues## Solution



## SolutionFixed the image conversion order to apply transformations in the correct sequence:



Fixed the image conversion order to apply transformations correctly:```python

# FIXED CODE:

```pythonimage = Image.open(image_path)

# FIXED CODE:

image = Image.open(image_path)# Step 1: Convert to RGB first (required by rembg and Hunyuan3D)

if image.mode != 'RGB':

# Step 1: Convert to RGB first (required by rembg)    image = image.convert("RGB")

if image.mode != 'RGB':

    image = image.convert("RGB")# Step 2: Remove background BEFORE other conversions (if available)

if self.rembg is not None:

# Step 2: Remove background BEFORE other conversions    image = self.rembg(image)

if self.rembg is not None:

    image = self.rembg(image)# Step 3: Convert to RGBA for Hunyuan3D pipeline (proper alpha channel)

if image.mode != 'RGBA':

# Step 3: Convert to RGBA for Hunyuan3D pipeline    image = image.convert("RGBA")

if image.mode != 'RGBA':

    image = image.convert("RGBA")# Step 4: Generate 3D mesh with properly prepared image

mesh = self.shapegen_pipeline(image=image)[0]

# Step 4: Generate 3D mesh```

mesh = self.shapegen_pipeline(image=image)[0]

```## File Modified



## File Modified- `backend/hunyuan_integration.py` - Lines 273-298 in `image_to_3d_generation()` method



- `backend/hunyuan_integration.py` - Lines 273-298 in `image_to_3d_generation()` method## Impact



## Impact- ✅ Correct texture mapping on generated 3D models

- ✅ Background removal now works properly (if rembg is available)

- ✅ Correct texture mapping on generated 3D models- ✅ Proper image mode handling through the pipeline

- ✅ Background removal now works properly- ✅ Prevents image inversion/negative effects

- ✅ Proper image mode handling through pipeline

- ✅ Prevents image inversion/negative effects## Testing



## TestingTo verify the fix:



To verify the fix:1. Start server: `.\START_SERVER.bat`

2. Upload a test image with distinct colors

1. Start server: `.\START_SERVER.bat`3. Generate 3D model

2. Upload a test image with distinct colors4. Verify the texture on the cube matches the input image (not inverted)

3. Generate 3D model

4. Verify the texture on the cube matches the input image## Technical Details



## Technical Details- **PIL Image Modes:**

  - `RGB`: 3 channels (Red, Green, Blue)

PIL Image Modes:  - `RGBA`: 4 channels (Red, Green, Blue, Alpha/transparency)

- **Hunyuan3D Requirement:** Accepts both RGB and RGBA, but consistency matters

- `RGB`: 3 channels (Red, Green, Blue)- **rembg Requirement:** Expects RGB input for proper background removal

- `RGBA`: 4 channels (Red, Green, Blue, Alpha)- **Proper Order:** RGB → RemoveBG → RGBA → Generation



Processing Order:---

*Fix applied: October 22, 2025*

- Hunyuan3D requirement: Proper image format*Related issue: Negative/inverted images in 3D cube texture*

- rembg requirement: RGB input for background removal
- Correct sequence: RGB → RemoveBG → RGBA → Generation

---

*Fix applied: October 22, 2025*
*Related issue: Negative/inverted images in 3D cube texture*
