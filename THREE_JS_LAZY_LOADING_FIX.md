# THREE.js Not Loading - ROOT CAUSE & FIX

## Problem Found (From Console Logs)

```
[ORFEAS] THREE.js not loaded!
```

The STL preview was failing because **Three.js library was never being loaded**.

## Root Cause

In `load3DModel()` function, the code was:

```javascript
// OLD CODE (WRONG):
if (typeof THREE !== 'undefined') {
    console.log('[ORFEAS] THREE.js is loaded, initializing viewer');
    init3DViewer(modelUrl);
} else {
    console.error('[ORFEAS] THREE.js not loaded!');  // ← We end up here!
    showFallback3DViewer(modelUrl);
}
```

**Problem:** This checks if THREE.js is already loaded, but:

1. Three.js is NOT loaded immediately on page load (it's lazy-loaded)
2. The condition fails, so we never call `init3DViewer()`
3. `init3DViewer()` contains the lazy loader that LOADS Three.js
4. Catch-22: We can't load Three.js because we're checking if it's loaded first!

## Solution Applied

Changed `load3DModel()` to:

```javascript
// NEW CODE (CORRECT):
console.log('[ORFEAS] Calling init3DViewer for lazy loading...');
init3DViewer(modelUrl);
```

**Why this works:**

1. We now ALWAYS call `init3DViewer()`
2. `init3DViewer()` checks if Three.js is loaded
3. If not loaded, it calls `threeJSLoader.load()` to load it
4. Then Three.js is available for the 3D viewer

## What init3DViewer Does

```javascript
async function init3DViewer(modelUrl) {
    // Check WebGL support...

    // LAZY LOAD THREE.JS:
    if (!threeJSLoader.isLoaded()) {
        console.log('[ORFEAS] Loading Three.js library...');
        await threeJSLoader.load();  // ← LOADS IT HERE
        console.log('[ORFEAS] Three.js loaded successfully');
    }

    // Now THREE is available
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(...);
    // ... etc
}
```

## Before vs After

### BEFORE (Broken)

```
load3DModel() called
  ↓
Check if THREE loaded? → NO
  ↓
Show fallback → FAIL ❌
```

### AFTER (Fixed)

```
load3DModel() called
  ↓
Call init3DViewer()
  ↓
init3DViewer checks if THREE loaded? → NO
  ↓
Call threeJSLoader.load()
  ↓
Load Three.js from CDN
  ↓
THREE now available → SUCCESS ✅
```

## File Changed

- `orfeas-studio.html` line 2493-2500: Removed the broken condition check, now directly calls init3DViewer()

## Expected Behavior Now

When you generate an STL:

1. ✅ Backend generates valid STL file
2. ✅ Frontend gets download URL
3. ✅ show3DPreview() is called with URL
4. ✅ load3DModel() creates canvas
5. ✅ **init3DViewer() LOADS THREE.JS**
6. ✅ Canvas initializes with Three.js
7. ✅ loadSTLModel() loads the STL file
8. ✅ **RED 3D CUBE APPEARS**

## Test Again

Now try:

1. Upload image
2. Generate 3D Model
3. **Watch browser console**
4. Look for: `[ORFEAS] Three.js loaded successfully`
5. Then: `[ORFEAS] STL loaded, triangles: 12`
6. **You should see the RED CUBE!**

## Summary

**Problem:** Checking if THREE.js was loaded before loading it
**Solution:** Removed the check, let init3DViewer() handle lazy loading
**Result:** Three.js now loads automatically when needed ✅
