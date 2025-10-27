#!/usr/bin/env python3
"""Fix corrupted emoji encoding in HTML files"""

import os
from pathlib import Path

def fix_file(filepath):
    """Fix encoding in a single file"""
    try:
        # Read as binary to handle encoding issues
        with open(filepath, 'rb') as f:
            content = f.read()

        original = content

        # Fix corrupted emoji sequences
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x8e\xc2\xa8', '🎨'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x9a\xc2\x80', '🚀'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\xa4\xc2\x96', '🤖'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xa7', '🔧'.encode('utf-8'))
        content = content.replace(b'\xc5\x93\xc3\xaf\xc2\xb8', '✨'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x8e\xc2\xaf', '🎯'.encode('utf-8'))
        content = content.replace(b'\xc2\xac\xc2\x87\xc3\xaf\xc2\xb8', '⬇️'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xb8', '📸'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x96\xc2\xbc\xc3\xaf\xc2\xb8', '🖼️'.encode('utf-8'))
        content = content.replace(b'\xc5\xa1\xc2\x99\xc3\xaf\xc2\xb8', '⚙️'.encode('utf-8'))
        content = content.replace(b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xb7', '📷'.encode('utf-8'))
        content = content.replace(b'\xc3\xa2\xc2\x9a\xc2\xa1', '⚡'.encode('utf-8'))
        content = content.replace(b'\xc3\xa2\xc2\x9b\xc2\x94', '⛔'.encode('utf-8'))

        # Write back if changed
        if content != original:
            with open(filepath, 'wb') as f:
                f.write(content)
            return True
        return False

    except Exception as e:
        print(f"Error fixing {filepath}: {e}")
        return False

def main():
    """Main entry point"""
    print("Fixing encoding issues in HTML files...")

    base_dir = Path(r'c:\Users\johng\Documents\oscar')

    # Find all HTML files
    html_files = list(base_dir.glob('*.html'))
    html_files.extend(base_dir.glob('*/*.html'))

    # Remove duplicates
    html_files = list(set(html_files))

    fixed_count = 0

    for html_file in sorted(html_files):
        if fix_file(str(html_file)):
            print(f"Fixed: {html_file.name}")
            fixed_count += 1

    print(f"\nTotal files fixed: {fixed_count}/{len(html_files)}")

if __name__ == '__main__':
    main()
