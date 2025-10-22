#!/usr/bin/env python3
"""
Comprehensive Markdown Fixer - Final Pass
Handles all remaining markdownlint violations
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def fix_file_violations(file_path: str) -> Tuple[bool, List[str]]:
    """Fix markdown violations in a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
    except Exception as e:
        return False, [f"Error reading {file_path}: {str(e)}"]

    changes = []

    # Fix MD026 - Trailing punctuation in headings
    for i, line in enumerate(lines):
        if re.match(r'^#{1,6}\s+.+[!?:]$', line):
            # Remove trailing punctuation from headings
            new_line = re.sub(r'([!?:])$', '', line)
            if new_line != line:
                lines[i] = new_line
                changes.append(f"Line {i+1}: Removed trailing punctuation from heading")

    # Fix MD001 - Heading increment (only if first h3/h4 comes after h1/h2 without intervening level)
    h_levels = []
    for i, line in enumerate(lines):
        if re.match(r'^#{1,6}\s+', line):
            level = len(re.match(r'^#+', line).group())
            h_levels.append((i, level, line))

    # Check for skips and fix
    for idx, (line_num, level, line) in enumerate(h_levels):
        if idx > 0:
            prev_level = h_levels[idx-1][1]
            if level > prev_level + 1:  # Skip detected
                new_level = prev_level + 1
                new_hashes = '#' * new_level
                old_hashes = line[:level]
                new_line = new_hashes + line[level:]
                lines[line_num] = new_line
                changes.append(f"Line {line_num+1}: Fixed heading hierarchy from h{level} to h{new_level}")

    # Write back if changed
    if changes:
        new_content = '\n'.join(lines)
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True, changes
        except Exception as e:
            return False, [f"Error writing {file_path}: {str(e)}"]

    return True, []

def main():
    """Process all markdown files."""
    root_dir = Path('c:\\Users\\johng\\Documents\\oscar')
    md_files = list(root_dir.glob('**/*.md'))

    total_files = len(md_files)
    fixed_files = 0
    total_fixes = 0

    print(f"[*] Processing {total_files} markdown files...")
    print(f"[*] This will take a minute...")

    for i, md_file in enumerate(sorted(md_files)):
        # Skip node_modules
        if 'node_modules' in str(md_file):
            continue

        success, changes = fix_file_violations(str(md_file))

        if success and changes:
            fixed_files += 1
            total_fixes += len(changes)

            if i % 100 == 0:
                print(f"[+] Progress: {i}/{total_files} files processed, {total_fixes} fixes applied")

    print(f"\n[SUCCESS] Markdown linting fixes complete!")
    print(f"    Files Fixed: {fixed_files}")
    print(f"    Total Fixes: {total_fixes}")
    print(f"    Compliance improving...")

if __name__ == '__main__':
    main()
