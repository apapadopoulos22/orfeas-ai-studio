#!/usr/bin/env python3
"""Comprehensive mojibake fixer - handles all corrupted emoji patterns"""

from pathlib import Path
import re

def comprehensive_fix():
    """Fix all mojibake patterns in HTML files"""

    # More comprehensive mojibake patterns
    fixes = [
        # UTF-8 double-encoded emojis (the main issue)
        (b'\xc3\xb0\xc2\x9f', '🎨'),  # 🎨 pattern
        (b'\xc3\xb0\xc2\x9f\xc2\x8e\xc2\xa8', '🎨'),  # Full palette
        (b'\xc3\xb0\xc2\x9f\xc2\x9a\xc2\x80', '🚀'),  # Rocket
        (b'\xc3\xb0\xc2\x9f\xc2\xa4\xc2\x96', '🤖'),  # Robot
        (b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xa7', '🔧'),  # Wrench
        (b'\xc3\xb0\xc2\x9f\xc2\x8e\xc2\xaf', '🎯'),  # Target
        (b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xb8', '📸'),  # Camera
        (b'\xc3\xb0\xc2\x9f\xc2\x94\xc2\xb7', '📷'),  # Camera2
        (b'\xc3\xa2\xc2\x9a\xc2\xa1', '⚡'),       # Lightning
        (b'\xc3\xa2\xc2\x9b\xc2\x94', '⛔'),       # No entry
    ]

    base_dir = Path(r'c:\Users\johng\Documents\oscar')

    files_fixed = 0

    for html_file in sorted(base_dir.glob('**/*.html')):
        try:
            # Read as bytes to handle binary patterns
            with open(html_file, 'rb') as f:
                content = f.read()

            original = content

            # Apply all fixes
            for pattern, replacement in fixes:
                if isinstance(replacement, str):
                    replacement = replacement.encode('utf-8')
                if isinstance(pattern, bytes):
                    content = content.replace(pattern, replacement)

            # Write back if changed
            if content != original:
                with open(html_file, 'wb') as f:
                    f.write(content)
                files_fixed += 1
                print(f"Fixed: {html_file.name}")
        except Exception as e:
            print(f"Error: {html_file.name}: {e}")

    print(f"\nTotal files fixed: {files_fixed}")

if __name__ == '__main__':
    comprehensive_fix()
