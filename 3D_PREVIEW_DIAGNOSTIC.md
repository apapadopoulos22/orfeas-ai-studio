# 3D Preview Debugging - Diagnostic Steps

## Step 1: Check if Fix is in Code

**Status:** ✅ CONFIRMED

The fix IS present in synexa-style-studio.html:

- Line 2203: `const viewer = document.getElementById("viewer-3d");`
- Line 2204: `viewer.classList.remove("hidden");`
- Line 2217: `console.log("[INIT] Canvas dimensions:", width, "x", height);`

## Step 2: Diagnose Why Preview Still Not Working

### Possible Issue 1: Canvas Still Getting 0x0 Dimensions

**Check in browser DevTools:**

```javascript
// F12 → Console, paste this:
const canvas = document.getElementById("three-canvas");
const viewer = document.getElementById("viewer-3d");
console.log("Viewer has 'hidden' class?", viewer.classList.contains("hidden"));
console.log("Viewer display style:", window.getComputedStyle(viewer).display);
console.log("Canvas offsetWidth:", canvas.offsetWidth);
console.log("Canvas offsetHeight:", canvas.offsetHeight);
console.log("Canvas computed style:", window.getComputedStyle(canvas));
```

**Expected Results:**

- Viewer has 'hidden' class? **false** (should be removed)
- Viewer display style? **block** (not none)
- Canvas offsetWidth? **400+** (real number)
- Canvas offsetHeight? **500+** (real number)

### Possible Issue 2: Parent Element Also Hidden

The viewer might have parent elements that are also hidden! Check:

```javascript
// F12 → Console:
const viewer = document.getElementById("viewer-3d");
let parent = viewer;
while (parent) {
  const style = window.getComputedStyle(parent);
  console.log("Element:", parent.tagName, parent.id, parent.className);
  console.log("  Display:", style.display);
  console.log("  Visibility:", style.visibility);
  console.log("  Hidden attr:", parent.hasAttribute("hidden"));
  parent = parent.parentElement;
  if (parent === document.body) break;
}
```

### Possible Issue 3: CSS Override

The `.hidden` class might be applied dynamically somewhere else. Check:

```javascript
// F12 → Console:
const viewer = document.getElementById("viewer-3d");
const classes = viewer.classList;
console.log("All classes on viewer:", Array.from(classes));

// Check if any parent has .hidden
let parent = viewer.parentElement;
while (parent) {
  if (parent.classList.contains("hidden")) {
    console.log("Parent", parent.tagName, "has 'hidden' class!");
  }
  parent = parent.parentElement;
}
```

### Possible Issue 4: Not Reaching the Fix Code

The `load3DModel()` function might not be called at all. Check:

```javascript
// F12 → Console:
// After trying to generate 3D, check console for these messages:
// "[INIT] Canvas dimensions: XXX x YYY"
// "[INIT] Initializing Three.js scene..."
// "[INIT] WebGL renderer created successfully"

// If you don't see these, the function wasn't called!
// Check console for any errors
```

### Possible Issue 5: Three.js Not Loading

```javascript
// F12 → Console:
console.log("THREE defined?", typeof THREE !== "undefined");
console.log("THREE.Scene available?", typeof THREE.Scene);
console.log("THREE.OrbitControls available?", typeof THREE.OrbitControls);
```

## Step 3: Run Full Diagnostic

Paste this complete diagnostic script in DevTools console:

```javascript
console.clear();
console.log("=== 3D PREVIEW DIAGNOSTIC ===");

// 1. Check DOM elements
const canvas = document.getElementById("three-canvas");
const viewer = document.getElementById("viewer-3d");
const preview = document.getElementById("preview-container");

console.log("\n1. DOM ELEMENTS:");
console.log("Canvas exists?", !!canvas);
console.log("Viewer exists?", !!viewer);
console.log("Preview container exists?", !!preview);

// 2. Check visibility
console.log("\n2. VISIBILITY:");
console.log("Viewer has 'hidden' class?", viewer?.classList.contains("hidden"));
console.log("Viewer computed display:", window.getComputedStyle(viewer)?.display);
console.log("Preview computed display:", window.getComputedStyle(preview)?.display);

// 3. Check dimensions
console.log("\n3. DIMENSIONS:");
console.log("Canvas offsetWidth:", canvas?.offsetWidth);
console.log("Canvas offsetHeight:", canvas?.offsetHeight);
console.log("Viewer offsetWidth:", viewer?.offsetWidth);
console.log("Viewer offsetHeight:", viewer?.offsetHeight);

// 4. Check Three.js
console.log("\n4. THREE.JS:");
console.log("THREE loaded?", typeof THREE !== "undefined");
console.log("Scene exists?", typeof scene !== "undefined");
console.log("Renderer exists?", typeof renderer !== "undefined");
console.log("Camera exists?", typeof camera !== "undefined");

// 5. Check animation loop
console.log("\n5. ANIMATION:");
console.log("OrbitControls available?", typeof THREE?.OrbitControls !== "undefined");
console.log("Controls initialized?", typeof controls !== "undefined");

// 6. Check for errors
console.log("\n6. ERRORS:");
// Scroll up in console to see if there are red error messages
console.log("Check console above for any red error messages");

console.log("\n=== END DIAGNOSTIC ===");
```

## Step 4: What to Do Based on Results

### If Viewer Still Has 'hidden' Class

The `remove("hidden")` line isn't working. Could be:

1. Code not being executed
2. Class added back by other code
3. Different element being targeted

**Solution:** Check browser console for errors during generation

### If Viewer Display is 'none'

Parent element might be hidden. Check the parent hierarchy:

1. Upload zone container
2. Studio main
3. Page body

**Solution:** Look for parent with `.hidden` class

### If Canvas Dimensions are 0x0

The element is still not visible.

1. Check if `remove("hidden")` is actually being called
2. Check if another `hidden` class is being added after
3. Check if there's a timing issue

**Solution:** Add more debugging to verify when element becomes visible

### If Three.js Not Defined

The Three.js library didn't load.

1. Check Network tab in DevTools
2. Look for failed script loads
3. Check browser console for load errors

**Solution:** Reload page, check if three.js CDN is working

### If Scene Doesn't Exist

The initialization code didn't run.

1. Check if `load3DModel()` was called
2. Check for JavaScript errors in console
3. Verify STL file was actually generated on backend

**Solution:** Check browser console during generation process

## Step 5: Check Backend

Make sure the 3D generation is actually completing:

```bash
# In PowerShell:
docker-compose logs backend | tail -50
# Look for success messages like:
# "[3D-GENERATION] Complete"
# "[FILE-SAVED] stl_output_*.stl"
```

## Step 6: Manual Test

Try manually calling the load function:

```javascript
// F12 → Console, after generation completes:
console.log("Testing load3DModel...");
load3DModel("stl_output_latest.stl");
// Watch console for initialization messages
```

## Next Steps

1. **Run the diagnostic** (Step 3) and share results
2. **Check console errors** - are there any red errors?
3. **Verify backend** - did 3D generation complete?
4. **Check browser** - which browser are you using?
5. **Check network** - in DevTools Network tab, did all resources load?

Once we know what's failing, we can fix it specifically.

---

**Status:** Investigating why preview still not working despite code fix

**Action Required:** Run diagnostic steps above and report results
