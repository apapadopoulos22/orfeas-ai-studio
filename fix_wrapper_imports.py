#!/usr/bin/env python3
"""Fix all wrapper tier module imports to use relative imports"""

import glob
import os

os.chdir(r'c:\Users\johng\Documents\oscar\backend')

tier_files = glob.glob('bob_ai_expansion_tier*.py')

for filepath in tier_files:
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace absolute import with relative import
    content = content.replace(
        'from backend.bob_ai_expansion_200_disciplines',
        'from bob_ai_expansion_200_disciplines'
    )

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Fixed: {filepath}")

print(f"Fixed {len(tier_files)} files")
