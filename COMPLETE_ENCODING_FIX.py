#!/usr/bin/env python3
"""
ORFEAS AI - Complete Encoding Issue Fixer
Fixes UTF-8 mojibake (double-encoded emojis) in HTML files
"""

import os
from pathlib import Path

def fix_encoding_issues():
    """Fix all encoding issues in HTML files"""

    # Mapping of mojibake to correct UTF-8
    # These are the actual byte sequences that need to be fixed
    fixes_map = {
        'ðŸŽ¨': '🎨',  # Artist palette
        'ðŸš€': '🚀',  # Rocket
        'ðŸ¤–': '🤖',  # Robot
        'ðŸ"§': '🔧',  # Wrench
        'ðŸŽ¯': '🎯',  # Target
        'ðŸ"¸': '📸',  # Camera
        'ðŸ–¼ï¸': '🖼️', # Picture
        'ðŸ"·': '📷',  # Camera 2
        'âš¡': '⚡',   # Lightning
        'â›"': '⛔',   # No entry
        'œ¨': '✨',    # Sparkles
        'š™ï¸': '⚙️',  # Gear
        '€¢': '•',     # Bullet
        'üìã': '🔍',  # Magnifying glass
        ''úÖ': '✅',   # Checkmark
        ''ùå': '❌',   # X mark
        'üì°': '📡',  # Antenna
        'üéØ': '🎨',  # Palette 2
    }

    base_dir = Path(r'c:\Users\johng\Documents\oscar')

    # Find all HTML files
    html_files = []
    for pattern in ['*.html', '*/*.html', '*/*/*.html']:
        html_files.extend(base_dir.glob(pattern))

    html_files = sorted(list(set(html_files)))

    print("=" * 70)
    print("ORFEAS AI - HTML Encoding Issue Fixer")
    print("=" * 70)
    print(f"Found {len(html_files)} HTML files to process...\n")

    total_fixes = 0
    files_modified = 0

    for html_file in html_files:
        try:
            # Read file with UTF-8 encoding
            with open(html_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()

            original_content = content

            # Apply all fixes
            for mojibake, correct in fixes_map.items():
                if mojibake in content:
                    count = content.count(mojibake)
                    content = content.replace(mojibake, correct)
                    total_fixes += count

            # Only write if changes were made
            if content != original_content:
                with open(html_file, 'w', encoding='utf-8-sig') as f:
                    f.write(content)

                # Count fixes in this file
                file_fixes = sum(original_content.count(m) for m in fixes_map.keys())
                if file_fixes > 0:
                    print(f"✅ {html_file.name:40} - {file_fixes} fixes applied")
                    files_modified += 1

        except Exception as e:
            print(f"⚠️  {html_file.name:40} - Error: {e}")

    print("\n" + "=" * 70)
    print("Summary:")
    print(f"  Total files processed: {len(html_files)}")
    print(f"  Files modified:       {files_modified}")
    print(f"  Total issues fixed:   {total_fixes}")
    print("=" * 70)
    print("✨ Encoding fixes complete!\n")

if __name__ == '__main__':
    fix_encoding_issues()
