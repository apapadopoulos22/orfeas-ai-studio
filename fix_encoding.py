#!/usr/bin/env python3
import re

# Fix orfeas-ai-studio.html
with open('orfeas-ai-studio.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace any remaining issues with "2D" followed by any junk followed by "3D" with proper arrow
content = re.sub(r'2D[^3]+3D', '2D→3D', content)

# Fix dimensions like 512—512 to 512×512
content = re.sub(r'(\d+)[—–‐](\d+)', r'\1×\2', content)

with open('orfeas-ai-studio.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✓ orfeas-ai-studio.html fixed")

# Fix connection-fix files
files_to_fix = [
    'netlify-deploy-folder/connection-fix.html',
    'netlify-frontend/connection-fix.html'
]

for fpath in files_to_fix:
    try:
        with open(fpath, 'r', encoding='utf-8') as f:
            c = f.read()
        # Already fixed via replace_string_in_file, just verify
        if '⚙️' in c:
            print(f"✓ {fpath} already fixed")
        else:
            print(f"⚠ {fpath} needs checking")
    except FileNotFoundError:
        print(f"✗ {fpath} not found")

print("\nEncoding fixes complete!")
