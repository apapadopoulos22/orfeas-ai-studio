#!/usr/bin/env python3
"""Fix all mojibake corrupted characters in HTML files"""

import os
from pathlib import Path

def fix_mojibake():
    """Fix corrupted characters in all HTML files"""

    # Mojibake to correct character mappings
    fixes = {
        '¨': '✨',      # Sparkles
        '¢': '•',       # Bullet point
        ''': "'",       # Single quote
        ''': "'",       # Single quote variant
        '"': '"',       # Left double quote
        '"': '"',       # Right double quote
        '–': '-',       # En dash to hyphen
        '—': '-',       # Em dash to hyphen
        '¤': '🤖',      # Robot
        '§': '🔧',      # Wrench
        '†': '↔',       # Arrows
        'ž': 'ß',       # Fix variant
        'œ': '✨',      # Sparkles variant
        'š': 's',       # S variant
        '¬': '↔',       # Left/right
        '«': '"',       # Left guillemet
        '»': '"',       # Right guillemet
        '×': '×',       # Multiplication (keep as is)
        'μ': 'μ',       # Micro (keep as is)
        '°': '°',       # Degree (keep as is)
    }

    base_dir = Path(r'c:\Users\johng\Documents\oscar')

    files_fixed = 0
    total_fixes = 0

    # Fix all HTML files
    for html_file in sorted(base_dir.glob('**/*.html')):
        try:
            content = html_file.read_text(encoding='utf-8')
            original = content

            for broken, fixed in fixes.items():
                if broken in content:
                    content = content.replace(broken, fixed)
                    total_fixes += content.count(fixed) - original.count(fixed)

            if content != original:
                html_file.write_text(content, encoding='utf-8')
                files_fixed += 1
                print(f"Fixed: {html_file.name}")
        except Exception as e:
            print(f"Error: {html_file.name} - {e}")

    print(f"\nTotal files fixed: {files_fixed}")
    print(f"Total replacements: {total_fixes}")

if __name__ == '__main__':
    fix_mojibake()
