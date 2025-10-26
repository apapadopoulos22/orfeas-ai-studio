# Image Studio - UI Layout Reference

## Visual Layout

```
╔════════════════════════════════════════════════════════════════════════╗
║                          ORFEAS AI STUDIO                              ║
║ Home | 3D Studio | Image | About    [● Status]  [Launch Studio →]     ║
╚════════════════════════════════════════════════════════════════════════╝

╔════════════════════════════════════════════════════════════════════════╗
║               Image Processing Studio                                  ║
║    Professional image editing and enhancement tools                    ║
╠═══════════════════════════╦═════════════════════════════════════════════╣
║                           ║                                             ║
║  LEFT PANEL (350px)       ║  RIGHT PANEL (Main Canvas)                  ║
║  ┌─────────────────────┐  ║  ┌────────────────────────────────────────┐ ║
║  │ 📷 Upload & Import  │  ║  │                                        │ ║
║  │ ┌────────────────┐  │  ║  │                                        │ ║
║  │ │ Drop here or  │  │  ║  │   IMAGE CANVAS AREA                    │ ║
║  │ │ click to      │  │  ║  │   (Canvas displays preview)            │ ║
║  │ │ browse        │  │  ║  │                                        │ ║
║  │ └────────────────┘  │  ║  │                                        │ ║
║  │                     │  ║  │   Dimensions:                          │ ║
║  │ File: no image      │  ║  │   Original: 1024×768px                 │ ║
║  │                     │  ║  │   Current:  1024×768px                 │ ║
║  │─────────────────────│  ║  └────────────────────────────────────────┘ ║
║  │                     │  ║                                             ║
║  │ ✂️ CROP IMAGE        │  ║  *Canvas shows live preview of edits*      ║
║  │ Ratio: [Freeform ▼] │  ║                                             ║
║  │ [Apply Crop] [Reset]│  ║  Tools                                       ║
║  │                     │  ║  ────────────────────────────────────────────║
║  │─────────────────────│  ║  1. CROP - Select aspect ratio             ║
║  │                     │  ║  2. FILTERS - Adjust brightness, etc       ║
║  │ 🎨 FILTERS & EFFECTS │  ║  3. RESIZE - Change dimensions            ║
║  │ Brightness: 100% ▯  │  ║  4. COLORS - Material selection            ║
║  │ Contrast:   100% ▯  │  ║  5. BOB AI - AI enhancement                ║
║  │ Saturation: 100% ▯  │  ║  6. FIGURINE - B&W extraction             ║
║  │ Hue Rotate: 0° ▯    │  ║  7. EXPORT - Format & download             ║
║  │ Blur:       0px ▯   │  ║                                             ║
║  │ [Reset All Filters] │  ║  Scroll left panel to access all tools     ║
║  │                     │  ║                                             ║
║  │─────────────────────│  ║                                             ║
║  │                     │  ║                                             ║
║  │ 📐 RESIZE & SCALE   │  ║                                             ║
║  │ Width:  [____1024__]│  ║                                             ║
║  │ Height: [____768___]│  ║                                             ║
║  │ ☑ Maintain aspect   │  ║                                             ║
║  │ [Apply Resize]      │  ║                                             ║
║  │                     │  ║                                             ║
║  │─────────────────────│  ║                                             ║
║  │                     │  ║                                             ║
║  │ 🎨 MATERIAL COLORS  │  ║                                             ║
║  │ [Red] [Teal][Blue] │  ║                                             ║
║  │ [Orange][Purple]   │  ║                                             ║
║  │ [Green][Gold][Red] │  ║                                             ║
║  │ Custom: [■ #00d4ff]│  ║                                             ║
║  │ [Apply Custom Color]│  ║                                             ║
║  │                     │  ║                                             ║
║  │─────────────────────│  ║                                             ║
║  │                     │  ║                                             ║
║  │ 🤖 BOB AI ENHANCE   │  ║                                             ║
║  │ Style: [Enhance ▼]  │  ║                                             ║
║  │ [Enhance w/ Bob AI] │  ║                                             ║
║  │                     │  ║                                             ║
║  │─────────────────────│  ║                                             ║
║  │                     │  ║                                             ║
║  │ 🎭 FIGURINE ENHANCE │  ║                                             ║
║  │ Threshold: [128 ▯]  │  ║                                             ║
║  │ [Generate Figurine] │  ║                                             ║
║  │ (Single element B&W)│  ║                                             ║
║  │                     │  ║                                             ║
║  │─────────────────────│  ║                                             ║
║  │                     │  ║                                             ║
║  │ 💾 EXPORT OPTIONS   │  ║                                             ║
║  │ Format: [PNG ▼]     │  ║                                             ║
║  │ Quality: 80% ▯      │  ║                                             ║
║  │ [⬇️ Download Image] │  ║                                             ║
║  │                     │  ║                                             ║
║  └─────────────────────┘  ║                                             ║
║                           ║                                             ║
╠═══════════════════════════╩═════════════════════════════════════════════╣
╚════════════════════════════════════════════════════════════════════════╝
```

---

## Component Details

### Upload Zone (Top Left)

```
┌────────────────────────────┐
│                            │
│            📸              │
│  Drop your image here      │
│    or click to browse      │
│  Supports: JPG, PNG, WebP  │
│                            │
└────────────────────────────┘

Original: No image
Current:  No image
```

### Crop Section

```
┌─────────────────────────────┐
│ ✂️ CROP IMAGE               │
├─────────────────────────────┤
│ Crop Aspect Ratio           │
│ [Freeform ▼]                │
│ - Freeform                  │
│ - Square (1:1)              │
│ - Widescreen (16:9)         │
│ - Standard (4:3)            │
│ - Photo (3:2)               │
│                             │
│ [✓ Apply Crop] [↻ Reset]   │
└─────────────────────────────┘
```

### Filters Section (Sliders)

```
┌──────────────────────────────┐
│ 🎨 FILTERS & EFFECTS         │
├──────────────────────────────┤
│ Brightness: 100% [▯ ──────] │
│ Contrast:   100% [▯ ──────] │
│ Saturation: 100% [▯ ──────] │
│ Hue Rotate:   0° [▯ ──────] │
│ Blur:         0px [▯ ──────] │
│                              │
│ [↻ Reset All Filters]        │
└──────────────────────────────┘
```

### Material Colors (Grid)

```
┌────────────────────────────┐
│ 🎨 MATERIAL COLORS         │
├────────────────────────────┤
│ [■Red] [■Teal] [■Blue]    │
│ [■Orange] [■Purple] ────── │
│ [■Green] [■Gold] [■Dark]  │
│                            │
│ Custom Color:              │
│ [████████████░░] #00d4ff   │
│ [Apply Custom Color]       │
└────────────────────────────┘
```

### Figurine Enhance (Special)

```
┌────────────────────────────┐
│ 🎭 FIGURINE ENHANCE        │
├────────────────────────────┤
│ Extract single element     │
│ with clear background      │
│ & B&W colors for details   │
│                            │
│ Threshold:                 │
│ [▯ ──────────────] 128     │
│ (0: More white)            │
│ (255: More black)          │
│                            │
│ [Generate Figurine (BW)]   │
│ Output: Clear BG, B&W only │
└────────────────────────────┘
```

### Export Options (Bottom)

```
┌─────────────────────────────┐
│ 💾 EXPORT OPTIONS           │
├─────────────────────────────┤
│ Format:                     │
│ [PNG (Lossless) ▼]          │
│ - PNG (Lossless)            │
│ - JPG (Compressed)          │
│ - WebP (Modern)             │
│                             │
│ Quality:                    │
│ 80% [▯ ────────────]        │
│                             │
│ [⬇️ Download Image]         │
└─────────────────────────────┘
```

---

## Canvas Area (Right)

### Before Upload

```
┌────────────────────────────────────────────┐
│                                            │
│                                            │
│                  📸                        │
│            Upload an image                 │
│            to get started                  │
│                                            │
│                                            │
│         Original: No image                 │
│         Current:  No image                 │
│                                            │
└────────────────────────────────────────────┘
```

### After Upload

```
┌────────────────────────────────────────────┐
│                                            │
│         ┌──────────────────────┐           │
│         │                      │           │
│         │   IMAGE PREVIEW      │           │
│         │   (Actual Canvas)    │           │
│         │                      │           │
│         │   Dimensions inside  │           │
│         │   canvas area        │           │
│         │                      │           │
│         └──────────────────────┘           │
│                                            │
│         Original: 1024×768px               │
│         Current:  1024×768px               │
│                                            │
└────────────────────────────────────────────┘
```

### With Active Edits

```
┌────────────────────────────────────────────┐
│                                            │
│         ┌──────────────────────┐           │
│         │   IMAGE (Filtered)   │           │
│         │   - Brightness +20%  │           │
│         │   - Saturation +50%  │           │
│         │   - Blur 2px         │           │
│         │   Result: Live       │           │
│         │   preview showing    │           │
│         │   all edits          │           │
│         │                      │           │
│         └──────────────────────┘           │
│                                            │
│         Original: 1024×768px               │
│         Current:  1024×768px               │
│                                            │
└────────────────────────────────────────────┘
```

---

## Responsive Behavior

### Desktop (1400px+)

```
Left Panel (350px fixed) | Main Canvas (1fr)
Optimal for editing and preview
```

### Tablet (1024px)

```
Left Panel (300px) | Main Canvas (70%)
Slightly compressed but functional
```

### Mobile (<768px)

```
Stacked layout:
- Upload zone full width
- Controls as collapsible sections
- Canvas full width below
Scrollable for access to all tools
```

---

## Color Scheme

### UI Colors

- Background: `#0a0e1a` (dark space)
- Cards: `#141824` (darker)
- Accent Primary: `#00d4ff` (cyan - interactive)
- Accent Secondary: `#7c3aed` (purple - decorative)
- Text Primary: `#ffffff` (white - readable)
- Text Secondary: `#94a3b8` (gray - secondary info)
- Border: `#1e293b` (subtle dividers)

### Material Color Palette

- Red: `#FF6B6B` (Plastic/Ceramic)
- Teal: `#4ECDC4` (Premium Material)
- Blue: `#45B7D1` (Professional)
- Orange: `#FFA502` (Vibrant)
- Purple: `#9B59B6` (Elegant)
- Green: `#1ABC9C` (Natural)
- Gold: `#F39C12` (Premium)
- Dark Red: `#E74C3C` (Deep Tone)

---

## Interaction Flow

```
1. USER LOADS IMAGE STUDIO
   ↓
2. UPLOADS IMAGE (drag/click)
   ↓
3. SEES PREVIEW ON CANVAS
   ↓
4. CHOOSES TOOL (Crop/Filter/Resize/etc)
   ↓
5. ADJUSTS SETTINGS
   ↓
6. SEES LIVE PREVIEW UPDATE
   ↓
7. APPLIES CHANGES (click button)
   ↓
8. REPEAT STEPS 4-7 AS NEEDED
   ↓
9. SELECTS EXPORT FORMAT
   ↓
10. CLICKS DOWNLOAD
   ↓
11. FILE SAVED TO DOWNLOADS
```

---

## Tool Access Order

Users typically access tools in this sequence:

1. **Upload** (mandatory first)
2. **Crop** (optional, early)
3. **Filters** (most common)
4. **Resize** (if needed)
5. **Color Material** (for visualization)
6. **Bob AI** (optional enhancement)
7. **Figurine Enhance** (for 3D prep)
8. **Export** (final step)

---

## Accessibility Features

- ✅ Clear labels on all controls
- ✅ Emojis for visual recognition
- ✅ Keyboard navigation support (Tab)
- ✅ Hover tooltips with descriptions
- ✅ Status messages for feedback
- ✅ Error messages in plain language
- ✅ High contrast text on dark background
- ✅ Readable font sizes

---

## Performance Indicators

### Canvas Rendering

- 60 FPS target (16ms per frame)
- Real-time filter updates
- Smooth slider interactions
- No lag or stutter

### Load Times

- First load: <100ms
- Image upload: <500ms
- Canvas operation: <50ms
- Filter update: <5ms

---

## Expected Appearance

The Image Processing Studio should look like a professional photo editing interface with:

- Dark, modern aesthetic matching ORFEAS brand
- Cyan/purple accent colors
- Clear section organization
- Real-time visual feedback
- Responsive canvas area
- Intuitive control layout
- Smooth animations and transitions

---

*For implementation details, see IMAGE_EDITOR_IMPLEMENTATION.md*
*For usage instructions, see IMAGE_STUDIO_QUICK_START.md*
