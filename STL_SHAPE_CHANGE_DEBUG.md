# STL Shape Change - Debugging Guide

## What You're Seeing

The red cube appears to be **changing shape** in the preview.

## Most Likely Causes

### 1. **Perspective Distortion** (Most Likely ✅)

- **What:** A cube looks different from different angles
- **Why:** Three.js uses perspective camera, not orthographic
- **Solution:** Normal behavior - this is 3D perspective

### 2. **Mouse Rotation** (Very Likely)

- **What:** You might be rotating the view with mouse
- **How to test:** Don't touch mouse/trackpad - watch the cube
- **Result:** If it only changes when you move mouse, it's this

### 3. **Auto-Rotation** (Possible)

- **What:** The cube rotates automatically
- **How to check:** Look for spinning animation
- **How to disable:** Click the rotation button (⟲ icon)

### 4. **Geometry Issue** (Less Likely)

- **What:** The STL file has distorted geometry
- **How to check:** Open console and look for geometry dimensions
- **Expected:** Should log bounding box size and scale factor

## How to Debug

### Check Console Output

After loading, you should see:

```
[ORFEAS] STL loaded, triangles: 12
[ORFEAS] Bounding box size: {x: 20, y: 20, z: 20}
[ORFEAS] Max dimension: 20
[ORFEAS] Scale factor applied: 0.15
```

### What These Numbers Mean

- **x, y, z size:** Physical dimensions of the cube
- **Max dimension:** Largest axis (for uniform cube = all same)
- **Scale factor:** How much to scale to fit in view (0.15 = 15%)

### If All Axes Are Equal

If x, y, z are all roughly equal → **it's a proper cube** ✓

### If Axes Are Different

If x ≠ y ≠ z → **the STL is distorted** ✗

## Visual Tests

### Test 1: Don't Move Mouse

1. Load STL
2. **Sit still** - don't touch mouse for 10 seconds
3. **Does the cube change?**
   - YES → Auto-rotation or animation
   - NO → User input causing change

### Test 2: Click Reset View

1. Load STL
2. Click "Reset View" button
3. **Is the cube a proper cube now?**
   - YES → It's perspective distortion
   - NO → Geometry issue

### Test 3: Disable Auto-Rotation

1. Click the rotate button to disable auto-rotation
2. Watch the cube - should be completely still
3. Move mouse without clicking
4. **Does it move?** (OrbitControls might be active)

## Expected Behavior

A proper red cube in the preview should:

- ✅ Look cubic from most angles
- ✅ Have 12 triangles (6 faces × 2 triangles)
- ✅ Appear red with slight transparency
- ✅ Cast shadows
- ✅ Rotate smoothly when you move mouse (if OrbitControls enabled)
- ✅ Stay centered in view

## If It's Actually Deformed

If the cube is truly distorted (not perspective):

```
Symptoms:
- Elongated like a rectangle or stretched
- Inconsistent sizing per axis
- Weird angles or twisted shape

Next steps:
1. Check console for geometry dimensions
2. Verify backend STL file
3. Regenerate STL file from backend
```

## Next Action

Try these in order:

1. **Don't touch anything** - watch for 5 seconds
2. **Click "Reset View"** button
3. **Disable auto-rotation** if enabled
4. **Check console** for geometry dimensions
5. **Report what you see**

---

**Note:** Most "shape changes" in 3D viewers are just perspective/rotation.
The geometry is likely fine!
