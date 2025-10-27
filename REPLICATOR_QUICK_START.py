#!/usr/bin/env python3
"""
REPLICATOR QUICK START - 30-Second Guide

The Replicator converts physical objects into precise 3D digital models using photographs.
"""

# ============================================================================
# QUICK START (5 STEPS)
# ============================================================================

print("""
🔬 ORFEAS REPLICATOR - QUICK START

┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Upload Images                                           │
├─────────────────────────────────────────────────────────────────┤
│ • Take photos of object from multiple angles                    │
│ • Include a ruler or reference object in at least 1 photo      │
│ • Upload 2-8 photos (PNG, JPG, WebP)                           │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Specify Angles (Optional)                              │
├─────────────────────────────────────────────────────────────────┤
│ For each image, optionally label the angle:                    │
│   👀 Front    🔙 Back    ◀️ Left    ▶️ Right                   │
│   ⬆️ Top      ⬇️ Bottom   ↗️ 45°     🔍 Macro                    │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Configure Ruler Calibration                            │
├─────────────────────────────────────────────────────────────────┤
│ Option A: Auto-detect                                          │
│   ✓ System finds ruler automatically                           │
│                                                                 │
│ Option B: Manual                                               │
│   ✓ Select ruler type (cm, inch, metric, reference object)    │
│   ✓ Enter ruler length in photo (pixels)                       │
│   ✓ Enter actual ruler length (mm)                             │
│   ✓ Example: 500 pixels = 150mm → 0.3 mm/pixel                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Analyze                                                │
├─────────────────────────────────────────────────────────────────┤
│ Click: "⚡ Analyze Images & Extract Dimensions"                │
│ Wait: 5-15 seconds per image                                  │
│ Result: Dimensions, cavities, suggested photos                │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Export                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Option A: Export 3D Model (OBJ/GLB)                           │
│   ✓ Use in 3D printing software                               │
│   ✓ Import to CAD programs                                    │
│   ✓ View in 3D viewers                                        │
│                                                                │
│ Option B: Export Report (HTML)                                │
│   ✓ Full analysis documentation                               │
│   ✓ Measurement confidence scores                             │
│   ✓ Next steps recommendations                                │
└─────────────────────────────────────────────────────────────────┘


📸 OPTIMAL PHOTOGRAPHY SETUP
═════════════════════════════════════════════════════════════════

FOR BEST RESULTS, CAPTURE THESE ANGLES:

1. Front View (👀)          3. Top View (⬆️)          5. Macro (🔍)
   └─ Eye level             └─ Directly overhead    └─ Detail closeup

2. Right View (▶️)         4. Bottom View (⬇️)      6. 45° Angle (↗️)
   └─ 90° from front      └─ If visible/relevant   └─ Isometric view


✅ BEST PRACTICES
═════════════════════════════════════════════════════════════════

RULER PHOTOGRAPHY:
  ✓ Ruler fully visible and in frame
  ✓ Ruler flat and perpendicular to camera
  ✓ Good contrast between ruler and background
  ✓ Clear markings (cm lines visible)
  ✓ Positioned near object being measured

LIGHTING:
  ✓ Even, diffuse lighting (avoid harsh shadows)
  ✓ No backlit objects
  ✓ Minimize reflections
  ✓ Clear visibility of all details

FOCUS & SHARPNESS:
  ✓ Use tripod or stable surface
  ✓ Ensure sharp focus (use autofocus, then tap)
  ✓ Avoid motion blur (good lighting + faster shutter)
  ✓ High resolution images (3+ megapixels)


⚙️ UNDERSTANDING RESULTS
═════════════════════════════════════════════════════════════════

CONFIDENCE LEVELS:
  🟢 90-100% = Excellent (ruler visible, multiple angles)
  🟢 80-90%  = Very Good (ruler + good geometry)
  🟡 70-80%  = Good (solid geometric analysis)
  🔴 <70%    = Fair (recommend additional photos)

MEASUREMENT SOURCE:
  📏 "ruler"    = Direct measurement from ruler reference
  📐 "geometry" = Derived from shape and proportions
  💯 Higher source = More accurate

SUGGESTED ADDITIONAL PHOTOS:
  • If cavities detected: Close-up macro shots
  • If coverage gaps: Shoot suggested angles
  • If low confidence: More reference images


🎯 COMMON SCENARIOS
═════════════════════════════════════════════════════════════════

SCENARIO 1: Simple Box
  Images needed: 3 (front, top, side + ruler)
  Time: ~2 min
  Confidence: 92%
  Best use: 3D printing

SCENARIO 2: Complex Assembly
  Images needed: 6-8 (all angles + macro)
  Time: ~5 min
  Confidence: 75-85%
  Best use: Documentation, CAD import

SCENARIO 3: Small Detail/Cavity
  Images needed: 5 + 2 macro closeups
  Time: ~8 min
  Confidence: 70-80%
  Best use: Detail verification

SCENARIO 4: Delicate/Reflective Object
  Images needed: 8 (many angles, special lighting)
  Time: ~10 min
  Confidence: 60-75%
  Best use: Reference model, not production


🔧 TROUBLESHOOTING
═════════════════════════════════════════════════════════════════

ISSUE: "Low Confidence"
→ Add photos from more angles
→ Include ruler in photos
→ Improve lighting
→ Re-analyze

ISSUE: "Wrong Dimensions"
→ Verify ruler calibration
→ Check ruler is perpendicular to camera
→ Ensure ruler length values are correct
→ Provide clearer ruler image

ISSUE: "Cavities Detected But None Exist"
→ May be texture/shadows
→ Verify with close-up photo
→ Adjust lighting and re-shoot

ISSUE: "Can't see object clearly"
→ Better lighting needed
→ Use higher resolution camera
→ Increase image contrast
→ Use macro lens for detail


📤 EXPORT & NEXT STEPS
═════════════════════════════════════════════════════════════════

EXPORT 3D MODEL:
  Format: OBJ, GLB (GLTF binary)
  Use in:
    • 3D printing (Cura, PrusaSlicer)
    • CAD software (Fusion 360, FreeCAD)
    • Game engines (Unity, Unreal)
    • Visualization software

EXPORT REPORT:
  Format: HTML (interactive)
  Contains:
    • Dimension measurements table
    • Confidence scores
    • Object classification
    • Cavity detection results
    • Recommendations


🎓 ACCURACY & PRECISION
═════════════════════════════════════════════════════════════════

WITH RULER REFERENCE:
  Typical error: ±2-5%
  Example: Measure 100mm → 98-102mm result
  Use for: Production parts, precise models

WITHOUT RULER REFERENCE:
  Typical error: ±10-20%
  Example: Measure 100mm → 85-115mm result
  Use for: Approximate models, reference only


📊 SPECIFICATIONS
═════════════════════════════════════════════════════════════════

Input:
  • Formats: PNG, JPG, WebP
  • Max size: 50MB per image
  • Recommended: 2-8 images
  • Resolution: 3+ megapixels

Processing:
  • Speed: 5-15 sec/image
  • GPU: Enabled (RTX 3090)
  • Batch: 2-8 images recommended

Output:
  • 3D model (OBJ, GLB)
  • Analysis report (HTML)
  • Dimension table (CSV ready)
  • Confidence metrics


💡 PRO TIPS
═════════════════════════════════════════════════════════════════

1. Grid Background
   • Use grid mat under object
   • Helps with angle detection
   • Improves geometric analysis

2. Multiple Rulers
   • Use different scale rulers in different photos
   • Validates calibration accuracy
   • Increases confidence

3. Reference Objects
   • Coins, credit cards, batteries
   • Use if ruler unavailable
   • Specify size in configuration

4. Macro Photography
   • Close-up detail shots
   • Critical for cavities/features
   • Include with wide shots

5. Batch Process
   • Save photos, analyze together
   • System combines all data
   • Better results than individual photos


🚀 WORKFLOW INTEGRATION
═════════════════════════════════════════════════════════════════

REPLICATOR → 3D STUDIO:
  1. Export model from Replicator
  2. Import to 3D Studio
  3. Add materials, textures, lighting
  4. Export final render

REPLICATOR → 2.5D STUDIO:
  1. Generate top-down projection
  2. Convert to vector (SVG/DXF)
  3. Use for laser cutting
  4. Send to laser cutter

FULL PIPELINE:
  Object → Replicator → 3D Model → 3D Studio →
  Texture/Material → 2.5D Studio → Laser/3D Printer


═════════════════════════════════════════════════════════════════
Status: ✅ Ready to use
Last updated: October 26, 2025
Documentation: See REPLICATOR_COMPLETE_GUIDE.md for full details
═════════════════════════════════════════════════════════════════
""")
