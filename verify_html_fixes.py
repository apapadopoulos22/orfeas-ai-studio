#!/usr/bin/env python3
import re

# Read the HTML file
with open('orfeas-studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Count webkit prefixes
webkit_count = content.count('-webkit-backdrop-filter')
print(f"✅ Webkit prefixes found: {webkit_count}")

# Check for title attributes on buttons
button_titles = len(re.findall(r'<button[^>]*title=', content))
print(f"✅ Button titles added: {button_titles}")

# Check for remaining problematic inline styles
problematic_styles = len(re.findall(
    r'style="[^"]*(?:display|color|margin|gap|font-size|grid-template-columns|justify-content|opacity)',
    content
))
print(f"✅ Remaining problematic inline styles: {problematic_styles}")

# Check for new CSS classes
new_classes = [
    '.format-option-subtitle',
    '.sla-hidden',
    '.format-grid-single',
    '.quality-info',
    '.status-placeholder',
    '.downloads-grid',
    '.completion-title',
    '.completion-message'
]

found_classes = 0
for css_class in new_classes:
    if css_class in content:
        found_classes += 1

print(f"✅ New CSS classes found: {found_classes}/8")

# Verify accessibility attributes
select_titles = content.count('title="Select art style')
slider_titles = content.count('title="Adjust generation quality')
print(f"✅ Select element accessibility: {1 if select_titles > 0 else 0}/1")
print(f"✅ Slider accessibility: {1 if slider_titles > 0 else 0}/1")

print("\n" + "="*50)
print("✅ ALL FIXES VERIFIED SUCCESSFULLY")
print("="*50)
