#!/usr/bin/env python3
"""Remove inline styles from HTML and create CSS classes"""
import re

# Read the file
with open('orfeas-ai-studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Define replacements: find style patterns and replace with class names
replacements = [
    # Spell check info box
    (r'<div\s+id="bob-ai-spell-info-3d"\s+class="hidden"\s+style="\s+background: rgba\(59, 130, 246, 0\.1\);[^"]*"',
     '<div id="bob-ai-spell-info-3d" class="hidden spell-check-info"'),

    # Autocorrect button in spell check
    (r'<button\s+type="button"\s+class="btn btn-secondary"\s+onclick="autoCorrectPrompt3D\(\)"\s+style="\s+font-size: 0\.85rem;[^"]*"',
     '<button type="button" class="btn btn-secondary" onclick="autoCorrectPrompt3D()">'),

    # Generic margin-top fixes
    (r'style="\s*margin-top: 0\.5rem\s*"',
     'class="mt-sm"'),

    # Generic div with display: flex and gap
    (r'style="\s*display: flex;\s*gap: var\(--spacing-sm\);\s*margin-top: var\(--spacing-sm\);\s*flex-wrap: wrap;\s*"',
     'class="prompt-actions-flex"'),

    # Enhancement button styles
    (r'onclick="enhancePrompt\(\)"\s+style="[^"]*flex: 0 0 auto[^"]*"',
     'onclick="enhancePrompt()" class="enhance-prompt-btn"'),

    # Clear button styles
    (r'onclick="clearPrompt\(\)"\s+style="[^"]*flex: 0 0 auto[^"]*"',
     'onclick="clearPrompt()" class="clear-prompt-btn"'),
]

# Apply replacements
for pattern, replacement in replacements:
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Write back
with open('orfeas-ai-studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Removed inline styles and applied CSS classes")
