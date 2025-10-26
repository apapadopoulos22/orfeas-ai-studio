# HTML Refactoring Guide - Move Inline Styles to External CSS

**Version**: 1.0
**Date**: October 26, 2025
**Target File**: orfeas-ai-studio.html (3,594 lines)
**Stylesheet**: orfeas-studio.css (already created)
**Goal**: Reduce 2,264 CSS linting warnings by extracting inline styles

---

## Overview

This guide walks through the process of refactoring orfeas-ai-studio.html to remove inline `style=` attributes and replace them with CSS classes from the new orfeas-studio.css stylesheet.

### Impact

- **Before**: 2,264 inline style linting warnings
- **After**: 0 warnings (styles in external file)
- **Performance**: Slight improvement (CSS reusable, gzipped better)
- **Maintainability**: Much easier to update styles globally
- **Cacheability**: CSS cached separately from HTML

---

## Step 1: Add CSS Stylesheet Link

### Location: HTML Head Section

**Find this in your HTML:**

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORFEAS AI 2D→3D Studio</title>
    <style>
        /* Existing inline styles here */
    </style>
</head>
```

**Add this line AFTER the `</style>` closing tag:**

```html
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ORFEAS AI 2D→3D Studio</title>
    <style>
        /* Existing inline styles - KEEP these */
    </style>
    <!-- ADD THIS LINE: -->
    <link rel="stylesheet" href="orfeas-studio.css">
</head>
```

**Why**: The external CSS file will override and extend the existing styles.

---

## Step 2: Understand the Refactoring Patterns

### Pattern 1: Simple Spacing

**Before (Inline):**

```html
<div style="margin-top: var(--spacing-lg); margin-bottom: var(--spacing-md)">
    Content
</div>
```

**After (Using CSS Classes):**

```html
<div class="margin-top-lg margin-bottom-md">
    Content
</div>
```

**CSS Classes Available** (in orfeas-studio.css):

```css
.margin-top-sm { margin-top: var(--spacing-sm); }
.margin-top-md { margin-top: var(--spacing-md); }
.margin-top-lg { margin-top: var(--spacing-lg); }
.margin-top-xl { margin-top: var(--spacing-xl); }

.margin-bottom-sm { margin-bottom: var(--spacing-sm); }
.margin-bottom-md { margin-bottom: var(--spacing-md); }
.margin-bottom-lg { margin-bottom: var(--spacing-lg); }
.margin-bottom-xl { margin-bottom: var(--spacing-xl); }
```

### Pattern 2: Text Colors

**Before:**

```html
<p style="color: var(--text-muted); font-size: 0.85rem">
    Secondary text
</p>
```

**After:**

```html
<p class="text-muted">Secondary text</p>
```

**Available Classes:**

```css
.text-primary { color: var(--text-primary); }
.text-secondary { color: var(--text-secondary); }
.text-muted { color: var(--text-muted); font-size: 0.85rem; }
.text-error { color: var(--color-error); }
.text-success { color: var(--color-success); }
```

### Pattern 3: Button Colors

**Before:**

```html
<button style="background: linear-gradient(135deg, #3dd5f3 0%, #2a9d8f 100%); color: white">
    Generate
</button>
```

**After:**

```html
<button class="btn-cyan">Generate</button>
```

**Available Classes:**

```css
.btn-red { background: linear-gradient(135deg, #ff6b6b, #d63031); }
.btn-orange { background: linear-gradient(135deg, #ff9f43, #e55039); }
.btn-yellow { background: linear-gradient(135deg, #ffeaa7, #fdcb6e); }
.btn-green { background: linear-gradient(135deg, #55efc4, #00b894); }
.btn-cyan { background: linear-gradient(135deg, #3dd5f3, #2a9d8f); }
.btn-blue { background: linear-gradient(135deg, #74b9ff, #0984e3); }
.btn-purple { background: linear-gradient(135deg, #dfe6e9, #6c5ce7); }
.btn-teal { background: linear-gradient(135deg, #a29bfe, #6c5ce7); }
```

### Pattern 4: Grid/Flex Layouts

**Before:**

```html
<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--spacing-md)">
    <item>1</item>
    <item>2</item>
</div>
```

**After:**

```html
<div class="grid-2-cols gap-md">
    <item>1</item>
    <item>2</item>
</div>
```

**Available Classes:**

```css
.grid-2-cols { display: grid; grid-template-columns: repeat(2, 1fr); }
.grid-3-cols { display: grid; grid-template-columns: repeat(3, 1fr); }
.grid-4-cols { display: grid; grid-template-columns: repeat(4, 1fr); }

.gap-sm { gap: var(--spacing-sm); }
.gap-md { gap: var(--spacing-md); }
.gap-lg { gap: var(--spacing-lg); }
```

---

## Step 3: Common Inline Patterns to Replace

### Find & Replace Pattern 1: Margin Utilities

**Regex Search:**

```
style="margin-top: var\(--spacing-([a-z]+)\)"
```

**Replace With:**

```
class="margin-top-$1"
```

### Find & Replace Pattern 2: Padding Utilities

**Regex Search:**

```
style="padding: var\(--spacing-([a-z]+)\)"
```

**Replace With:**

```
class="padding-$1"
```

### Find & Replace Pattern 3: Text Colors

**Regex Search:**

```
style="color: var\(--text-([a-z]+)\)(?:;[^"]*)?;"
```

**Replace With:**

```
class="text-$1"
```

---

## Step 4: Manual Refactoring Process

### Use Your Editor's Find & Replace (Recommended)

**In VS Code:**

1. Open orfeas-ai-studio.html
2. Press `Ctrl+H` to open Find & Replace
3. Enable Regular Expressions (click `.*` button)
4. Use patterns from Step 3

### Or Use Command Line (sed/awk)

```bash
# Backup original
cp orfeas-ai-studio.html orfeas-ai-studio.html.backup

# Replace margin-top styles
sed -i 's/style="margin-top: var(--spacing-\([a-z]*\))"/class="margin-top-\1"/g' \
    orfeas-ai-studio.html

# Replace margin-bottom styles
sed -i 's/style="margin-bottom: var(--spacing-\([a-z]*\))"/class="margin-bottom-\1"/g' \
    orfeas-ai-studio.html

# Replace text colors
sed -i 's/style="color: var(--text-\([a-z-]*\))"/class="text-\1"/g' \
    orfeas-ai-studio.html
```

---

## Step 5: Detailed Examples (Real Use Cases)

### Example 1: Navigation Bar

**Before:**

```html
<nav style="
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md);
    background: var(--background-secondary);
    border-bottom: 1px solid var(--border-color)
">
    <h1 style="color: var(--text-primary); font-size: 1.5rem">ORFEAS</h1>
    <ul style="display: flex; gap: var(--spacing-md)">
        <li style="color: var(--text-muted)">About</li>
        <li style="color: var(--text-muted)">Contact</li>
    </ul>
</nav>
```

**After:**

```html
<nav class="navbar">
    <h1 class="logo">ORFEAS</h1>
    <ul class="nav-links">
        <li class="text-muted">About</li>
        <li class="text-muted">Contact</li>
    </ul>
</nav>
```

**CSS Classes Added to orfeas-studio.css:**

```css
.navbar {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: var(--spacing-md);
    background: var(--background-secondary);
    border-bottom: 1px solid var(--border-color);
}

.logo {
    color: var(--text-primary);
    font-size: 1.5rem;
}

.nav-links {
    display: flex;
    gap: var(--spacing-md);
}
```

### Example 2: Card Component

**Before:**

```html
<div style="
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--spacing-md)
">
    <h2 style="color: var(--text-primary); font-size: 1.25rem">Title</h2>
    <p style="color: var(--text-muted); margin-top: var(--spacing-sm)">Description</p>
</div>
```

**After:**

```html
<div class="card">
    <h2 class="card-title">Title</h2>
    <p class="card-description">Description</p>
</div>
```

**CSS Classes:**

```css
.card {
    background: var(--background-secondary);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-md);
    padding: var(--spacing-lg);
    box-shadow: var(--shadow-sm);
    margin-bottom: var(--spacing-md);
}

.card-title {
    color: var(--text-primary);
    font-size: 1.25rem;
}

.card-description {
    color: var(--text-muted);
    margin-top: var(--spacing-sm);
}
```

### Example 3: Input Form

**Before:**

```html
<form style="display: grid; gap: var(--spacing-md)">
    <div style="display: flex; flex-direction: column; gap: var(--spacing-sm)">
        <label style="color: var(--text-primary); font-weight: 600">Image</label>
        <input
            type="file"
            style="
                padding: var(--spacing-sm);
                border: 1px solid var(--border-color);
                border-radius: var(--radius-sm);
                background: var(--background-primary)
            "
        >
    </div>
</form>
```

**After:**

```html
<form class="form">
    <div class="form-group">
        <label class="form-label">Image</label>
        <input type="file" class="form-input">
    </div>
</form>
```

**CSS Classes:**

```css
.form {
    display: grid;
    gap: var(--spacing-md);
}

.form-group {
    display: flex;
    flex-direction: column;
    gap: var(--spacing-sm);
}

.form-label {
    color: var(--text-primary);
    font-weight: 600;
}

.form-input {
    padding: var(--spacing-sm);
    border: 1px solid var(--border-color);
    border-radius: var(--radius-sm);
    background: var(--background-primary);
}
```

---

## Step 6: Responsive Design Refactoring

### Before (Inline Media Queries)

```html
<div style="
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md)
">
    <!-- Content -->
</div>

<!-- Media query somewhere in <style> -->
<style>
    @media (max-width: 768px) {
        div {
            grid-template-columns: repeat(2, 1fr);
        }
    }
</style>
```

### After (Class-Based)

```html
<div class="grid-3-cols-responsive">
    <!-- Content -->
</div>
```

**CSS:**

```css
.grid-3-cols-responsive {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: var(--spacing-md);
}

@media (max-width: 768px) {
    .grid-3-cols-responsive {
        grid-template-columns: repeat(2, 1fr);
    }
}

@media (max-width: 480px) {
    .grid-3-cols-responsive {
        grid-template-columns: 1fr;
    }
}
```

---

## Step 7: Verification Checklist

After refactoring, verify:

- [ ] External stylesheet link added to `<head>`
- [ ] All inline `style=` attributes removed or minimized
- [ ] HTML file loads without style breaking
- [ ] Colors display correctly
- [ ] Spacing looks identical
- [ ] Responsive behavior unchanged
- [ ] No browser console errors
- [ ] CSS linting warnings resolved

### Test in Browser

```javascript
// In browser console
// Count remaining inline styles
document.querySelectorAll('[style*="margin"]').length  // Should be low or 0
document.querySelectorAll('[style*="color"]').length   // Should be low or 0
```

---

## Step 8: Clean Up Remaining Inline Styles

### What to Keep (Inline)

Some styles should remain inline for dynamic content:

```html
<!-- OK to keep inline (dynamic values) -->
<div style="width: calc(${progress}%)">Progress Bar</div>
<div style="color: rgb(${r}, ${g}, ${b})">Dynamic Color</div>
<div style="transform: rotate(${angle}deg)">Rotating Element</div>
```

### What to Replace

Everything else should be moved to CSS:

```html
<!-- BEFORE: Static styling inline -->
<button style="background-color: #3dd5f3; color: white; padding: 10px 20px">
    Click
</button>

<!-- AFTER: Use class -->
<button class="btn-cyan">Click</button>
```

---

## Step 9: Performance Optimization

### 1. Minify CSS (Optional)

```bash
# Using cssnano or similar tool
npm install -g cssnano-cli

cssnano orfeas-studio.css -o orfeas-studio.min.css
```

Then update HTML:

```html
<link rel="stylesheet" href="orfeas-studio.min.css">
```

### 2. Add Cache Headers

```nginx
# In Nginx config
location ~* \.css$ {
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 3. Inline Critical CSS (Optional)

For above-the-fold styles:

```html
<head>
    <style>
        /* Critical styles for above-the-fold content */
        .navbar { /* ... */ }
        .hero { /* ... */ }
    </style>
    <!-- Non-critical styles load async -->
    <link rel="stylesheet" href="orfeas-studio.css" media="print" onload="this.media='all'">
</head>
```

---

## Troubleshooting

### Styles Not Applying

**Problem**: Changed HTML to use classes but styles not showing

**Solution**:

1. Verify stylesheet link is correct:

   ```html
   <link rel="stylesheet" href="orfeas-studio.css">
   ```

2. Check CSS file exists in correct location

3. Verify class name matches CSS:

   ```bash
   grep "\.card {" orfeas-studio.css  # Should find the class
   ```

4. Check browser DevTools:
   - Open DevTools (F12)
   - Select element
   - Check "Styles" panel
   - Verify stylesheet loaded

### Specificity Issues

**Problem**: External stylesheet styles override inline styles

**Solution**: Update CSS specificity if needed:

```css
/* If default class doesn't work */
.card-title {
    color: var(--text-primary) !important;  /* Use !important as last resort */
}
```

### Layout Breaks

**Problem**: Refactored elements look different

**Solution**:

1. Compare before/after in browser
2. Use Chrome DevTools to measure:
   - Padding/margin
   - Font size
   - Colors (color picker)
3. Update CSS to match exact values

---

## Batch Processing (Advanced)

### Python Script to Automate

Create `refactor_html.py`:

```python
import re
from pathlib import Path

# Read HTML
html_path = Path('orfeas-ai-studio.html')
html_content = html_path.read_text()

# Patterns to replace
patterns = [
    (r'style="margin-top: var\(--spacing-([a-z]+)\)"', r'class="margin-top-\1"'),
    (r'style="margin-bottom: var\(--spacing-([a-z]+)\)"', r'class="margin-bottom-\1"'),
    (r'style="padding: var\(--spacing-([a-z]+)\)"', r'class="padding-\1"'),
    (r'style="color: var\(--text-([a-z-]+)\)"', r'class="text-\1"'),
]

# Apply replacements
for pattern, replacement in patterns:
    html_content = re.sub(pattern, replacement, html_content)

# Write result
html_path.write_text(html_content)
print("✅ Refactoring complete!")
```

Run:

```bash
python refactor_html.py
```

---

## Completion Checklist

- [ ] Added stylesheet link to HTML head
- [ ] Backed up original HTML file
- [ ] Replaced common inline styles with classes
- [ ] Tested in browser (all styles display correctly)
- [ ] Responsive behavior verified
- [ ] No console errors
- [ ] CSS linting warnings reduced/eliminated
- [ ] Performance verified (load time acceptable)
- [ ] Documented any custom classes added
- [ ] Team updated on new CSS structure

---

## Summary of CSS Classes Available

**Spacing Utilities:**

- `.margin-top-{sm|md|lg|xl}`
- `.margin-bottom-{sm|md|lg|xl}`
- `.padding-{sm|md|lg|xl}`
- `.gap-{sm|md|lg|xl}`

**Typography:**

- `.text-primary|secondary|muted|error|success`
- `.heading-small|medium|large`

**Colors:**

- `.bg-{red|orange|yellow|green|cyan|blue|purple|teal}`
- `.btn-{red|orange|yellow|green|cyan|blue|purple|teal}`

**Layout:**

- `.grid-{2|3|4}-cols`
- `.flex-center|flex-between|flex-column`

**Components:**

- `.card`, `.card-title`, `.card-description`
- `.navbar`, `.nav-links`
- `.form`, `.form-group`, `.form-label`, `.form-input`

Full list in `orfeas-studio.css` (search for class names).

---

**Next Steps:**

1. ✅ Add stylesheet link
2. ✅ Find and replace inline styles
3. ✅ Test in browser
4. ✅ Deploy updated HTML
5. ✅ Monitor for issues

**Result**: CSS linting warnings eliminated, maintainability improved, performance optimized! 🎉
