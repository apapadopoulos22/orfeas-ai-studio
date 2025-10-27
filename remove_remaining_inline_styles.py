#!/usr/bin/env python3
"""
Robust inline styles converter - removes style= attributes directly
"""

import re
from pathlib import Path

def remove_inline_styles(file_path):
    """Remove all inline style= attributes from HTML file."""

    print(f"\nProcessing: {file_path.name}")

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Count before
    before = len(re.findall(r'style="[^"]*"', content))
    print(f"  Before: {before} inline style attributes")

    # Simple replacement: remove style="..." attributes entirely
    # This is safe since we already have classes
    modified_content = re.sub(r'\s*style="[^"]*"', '', content)

    # Count after
    after = len(re.findall(r'style="[^"]*"', modified_content))
    print(f"  After: {after} inline style attributes")
    print(f"  Removed: {before - after} attributes")

    if before > after:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"  ✅ File updated")
        return True
    else:
        print(f"  ⚠️  No changes made")
        return False

def main():
    base_path = Path(r'c:\Users\johng\Documents\oscar')

    files_to_fix = [
        ('synexa-style-studio.html', base_path / 'synexa-style-studio.html'),
        ('orfeas-studio.html', base_path / 'orfeas-studio.html'),
        ('material-studio.html', base_path / 'material-studio.html'),
        ('ORFEAS-Connection-Fix/studio.html', base_path / 'ORFEAS-Connection-Fix' / 'studio.html'),
    ]

    print("\n" + "="*70)
    print("INLINE STYLES REMOVAL PASS 2")
    print("="*70)

    total = 0
    for name, file_path in files_to_fix:
        if file_path.exists():
            if remove_inline_styles(file_path):
                total += 1
        else:
            print(f"  ⚠️  Not found")

    print("\n" + "="*70)
    print(f"✅ Processed {total} files successfully")
    print("="*70)

if __name__ == '__main__':
    main()
