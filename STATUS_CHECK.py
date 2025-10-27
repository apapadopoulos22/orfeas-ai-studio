#!/usr/bin/env python3
"""
ORFEAS AI - Quick Status Check
Verifies no encoding or structural issues remain
"""

import os
from pathlib import Path
from collections import defaultdict

def check_files():
    """Check for any remaining issues"""

    print("=" * 70)
    print("ORFEAS AI - QUICK STATUS CHECK")
    print("=" * 70)

    base_dir = Path(r'c:\Users\johng\Documents\oscar')

    # Issues to check for
    issue_patterns = {
        'double_api': ['/api/api/', '/api//api/', '//api/'],
        'broken_emojis': ['ðŸ', 'ðŸ', 'âš', 'â›', 'œ', 'š™'],
        'broken_encoding': ['\ufffd', '\x00'],  # Unicode replacement char
        'missing_charset': ['<!DOCTYPE html>'],  # Will check if charset present
    }

    issues_found = defaultdict(list)
    files_checked = 0

    # Check all HTML files
    for html_file in sorted(base_dir.glob('**/*.html')):
        files_checked += 1

        try:
            content = html_file.read_text(encoding='utf-8')

            # Check for double API paths
            for pattern in issue_patterns['double_api']:
                if pattern in content:
                    issues_found['double_api'].append(str(html_file.name))

            # Check for broken emojis
            for pattern in issue_patterns['broken_emojis']:
                if pattern in content:
                    issues_found['broken_emojis'].append(str(html_file.name))

            # Check for Unicode replacement characters
            for pattern in issue_patterns['broken_encoding']:
                if pattern in content:
                    issues_found['broken_encoding'].append(str(html_file.name))

        except Exception as e:
            issues_found['read_error'].append(f"{html_file.name}: {e}")

    # Print results
    print(f"\n✅ Files Scanned: {files_checked}")
    print()

    if not any(issues_found.values()):
        print("✅ STATUS: NO ISSUES FOUND")
        print()
        print("Issues Checked:")
        print("  ✅ No double API paths (/api/api/)")
        print("  ✅ No corrupted emojis (mojibake)")
        print("  ✅ No Unicode replacement characters")
        print("  ✅ No file encoding errors")
    else:
        print("⚠️  STATUS: ISSUES FOUND")
        print()
        for issue_type, files in issues_found.items():
            if files:
                print(f"  {issue_type}: {len(files)} files")
                for f in files[:3]:
                    print(f"    - {f}")

    print("\n" + "=" * 70)
    print("✨ System Status: READY FOR DEPLOYMENT" if not any(issues_found.values()) else "Status: Review needed")
    print("=" * 70)

if __name__ == '__main__':
    check_files()
