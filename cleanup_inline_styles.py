#!/usr/bin/env python3
"""Remove all inline styles from orfeas-ai-studio.html and add CSS classes"""
import re

with open('orfeas-ai-studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove all inline style attributes and replace with class names
# Pattern 1: Simple margin-top only
content = re.sub(r'\s+style="\s*margin-top:\s*0\.5rem\s*"', ' class="mt-sm"', content)
content = re.sub(r'\s+style="\s*margin-top:\s*var\(--spacing-lg\)\s*"', ' class="mt-lg"', content)

# Pattern 2: Font-size and margin-bottom
content = re.sub(r'\s+style="\s*font-size:\s*2rem;\s*margin-bottom:\s*var\(--spacing-md\)\s*"', ' class="text-2xl mb-md"', content)
content = re.sub(r'\s+style="\s*font-size:\s*0\.85rem;\s*color:\s*var\(--text-muted\)\s*"', ' class="text-sm text-muted"', content)

# Pattern 3: Button styles with flex
content = re.sub(
    r'onclick="autoCorrectPrompt3D\(\)"\s+style="[^"]*font-size:\s*0\.85rem;[^"]*margin-left:\s*0\.5rem[^"]*"',
    'onclick="autoCorrectPrompt3D()" class="btn-spell-autocorrect"',
    content,
    flags=re.DOTALL
)

# Pattern 4: Various display and flex styles
content = re.sub(
    r'\s+style="\s*display:\s*flex;\s*gap:\s*var\(--spacing-sm\);\s*margin-top:\s*var\(--spacing-sm\);\s*flex-wrap:\s*wrap;\s*"',
    ' class="prompt-actions-flex"',
    content,
    flags=re.DOTALL
)

# Pattern 5: Large style blocks (multi-line)
content = re.sub(
    r'\s+style="\s*[^"]*flex:\s*0\s*0\s*auto[^"]*background:\s*linear-gradient\([^)]*\)[^"]*"',
    ' class="btn-gradient-primary"',
    content,
    flags=re.DOTALL
)

# Pattern 6: Clean up remaining style="" attributes
content = re.sub(r'\s+style="\s*"', '', content)

with open('orfeas-ai-studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Cleaned up inline styles")
