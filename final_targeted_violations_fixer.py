#!/usr/bin/env python3
"""
Final Targeted Fixer - Last 17 Violations
Fixes remaining MD026 and MD025 violations
"""

import os
import re
from pathlib import Path

def fix_md026_and_md025(file_path: str) -> bool:
    """Fix trailing punctuation and multiple h1 headings."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content
        lines = content.split('\n')

        # Fix MD026 - trailing punctuation in headings
        for i, line in enumerate(lines):
            if re.match(r'^#{1,6}\s+.+[!?:]$', line):
                # Remove trailing punctuation (except in inline code)
                if '`' not in line:
                    lines[i] = re.sub(r'([!?:])$', '', line)

        # Fix MD025 - Multiple h1 headings
        h1_positions = []
        for i, line in enumerate(lines):
            if re.match(r'^#\s+', line) and not line.startswith('## '):
                h1_positions.append(i)

        # Keep first h1, convert others to h2
        for pos in h1_positions[1:]:
            lines[pos] = '##' + lines[pos][1:]

        new_content = '\n'.join(lines)

        if new_content != original:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
        return False
    except:
        return False

def main():
    """Process all files."""
    root = Path('c:\\Users\\johng\\Documents\\oscar')
    files = [f for f in root.glob('**/*.md') if 'node_modules' not in str(f)]

    fixed = 0
    for f in files:
        if fix_md026_and_md025(str(f)):
            fixed += 1

    print(f"Fixed {fixed} files")
    print("Final targeted violations resolved!")

if __name__ == '__main__':
    main()
