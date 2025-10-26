<!-- markdownlint-disable MD022 -->

# Quick Test Guide: Mesh Improvements

## What Was Improved

✅ **Better Fallback**: Cube (12 triangles) → Icosphere (1,280 triangles)
✅ **Better Debugging**: Detailed pipeline logging + mesh analysis

## Quick Test (5 minutes)

### Step 1: Start Backend

```powershell
cd c:\Users\johng\Documents\oscar
python backend/main.py
```

Wait for:

```
[ORFEAS] Hunyuan3D: model load attempted...
[ORFEAS] Backend is ready!
```

### Step 2: Open Studio

Open browser: `http://127.0.0.1:5000` → Navigate to **3D Studio**

### Step 3: Test Generation

1. **Click "Drop your image here"**
2. **Upload any image** (JPG, PNG recommended)
3. **Preview appears** - shows your image
4. **Click "Generate 3D Model"**
5. **Watch progress bar**

### Step 4: Check Logs for Improvements

**In PowerShell terminal**, look for:

#### Good Path (Hunyuan3D worked)

```
[ORFEAS] 📸 Loading image: /tmp/upload_12345.png
[ORFEAS]    Original size: (1024, 1024), mode: RGB
[ORFEAS] 🎨 Removing background with rembg...
[ORFEAS] 🚀 Calling Hunyuan3D shapegen_pipeline...
[ORFEAS] 📊 Analyzing Generated mesh from pipeline:
[ORFEAS]    Vertices: 45,283
[ORFEAS]    Faces/Triangles: 87,456
[ORFEAS]    Bounds: min=[-125.3, -98.2], max=[134.2, 118.5]
[ORFEAS]    ✅ Mesh analysis complete
[ORFEAS] 💾 Exporting 3D model to: /tmp/output_12345.stl
[ORFEAS]    ✓ mesh.export() completed successfully
[ORFEAS]    File exported: 4,372,848 bytes
[ORFEAS] ✅ Successfully generated volumetric 3D model
```

**Result**: Download 3D model and open in:

- Windows 3D Viewer
- MeshLab
- Blender

Should show **realistic 3D shape** (not flat box)

#### Fallback Path (Hunyuan3D failed)

```
[ORFEAS] ❌ Pipeline returned None
[ORFEAS] Creating icosphere fallback (scale=50.0, subdivisions=4)...
[ORFEAS]    ✅ Icosphere generated: 651 vertices, 1280 triangles
[ORFEAS]    ✅ Icosphere fallback created: output.stl (651 vertices, 1280 triangles)
```

**Result**: Download 3D model shows **smooth sphere**

- Much better than old cube!
- Professional-looking geometry
- ~1,280 triangles (vs 12 before)

## What to Look For

### ✅ GOOD Signs

- Logs show multiple `[ORFEAS]` entries
- Mesh analysis shows > 20,000 vertices/triangles
- "✅" checkmarks in logs
- Downloaded STL file > 100 KB
- 3D viewer shows realistic geometry

### ❌ PROBLEMS to Debug

If logs show:

```
[ORFEAS] ❌ CRITICAL: Model not loaded at generation time!
```

→ **Backend issue**: Hunyuan3D didn't load on startup
→ Fix: Check GPU memory, model files exist

If logs show:

```
[ORFEAS] 📊 STL contains 0 triangles (invalid)
```

→ **Export failed silently**
→ Fix: Check disk space, file permissions

If logs show:

```
[ORFEAS] ❌ mesh.export() FAILED: CUDA out of memory
```

→ **GPU memory issue**
→ Fix: Close other GPU apps, reduce quality setting

## Verification Checklist

| Test | Expected | Status |
|------|----------|--------|
| Backend starts | "[ORFEAS] Backend ready" | ? |
| Image uploads | Preview shows in UI | ? |
| Generation works | Progress bar appears | ? |
| Logs are detailed | 25+ log lines per generation | ? |
| Good fallback | Smooth icosphere (1,280 tri) | ? |
| File downloads | STL file opens in 3D viewer | ? |
| 3D model appears | Realistic shape (not cube) | ? |

## Troubleshooting

### Logs don't show [ORFEAS] markers

Check if logging is configured:

```python
# In backend/main.py, ensure:
import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### Still getting simple cube instead of icosphere

Old code might be cached. **Restart backend**:

```powershell
# Kill old process
Get-Process python | Stop-Process -Force

# Wait 2 seconds
Start-Sleep -Seconds 2

# Start fresh
python backend/main.py
```

### 3D model looks the same as before

1. Check logs for mesh triangle count
   - If < 50 triangles: Fallback is working (good!)
   - If > 50,000 triangles: Hunyuan3D worked (even better!)
2. Download fresh copy (clear browser cache)
3. Try different 3D viewer

## Demo Images to Test

Great images to test with:

- **Simple object**: Ball, cube, chair
- **Complex shape**: Dinosaur, animal figure
- **With background**: Object on carpet/table
- **No background**: Cutout/transparent PNG

## Next Steps

1. ✅ Verify both paths work (good + fallback)
2. ✅ Check logs are detailed and helpful
3. ✅ Confirm 3D models look good
4. 🔧 Optional: Adjust `subdivisions=3` for faster fallback
5. 🔧 Optional: Adjust `scale=75` for bigger icosphere

## Log File Locations

```
backend/logs/backend_requests.log     # All requests (if logging enabled)
stdout (terminal)                     # Live output (best for debugging)
```

**Tip**: Run backend with this to save logs:

```powershell
python backend/main.py | Tee-Object -FilePath backend_debug.log
```

---

**Questions?** Check `MESH_FALLBACK_LOGGING_IMPROVEMENTS.md` for detailed docs.
