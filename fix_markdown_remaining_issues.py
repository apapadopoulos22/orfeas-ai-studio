#!/usr/bin/env python3
"""
Fix remaining markdown linting issues:
- MD040: Fenced code blocks must have a language
- MD036: Emphasis (bold/italic) used as heading
"""

import re
from pathlib import Path

def fix_markdown_file(filepath):
    """Fix markdown linting issues"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original = content

        # Fix MD040: Add language to code blocks
        # Match ``` followed by newline (no language)
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check if this is an opening fence with no language
            if re.match(r'^```+\s*$', line):
                # Add 'text' as default language
                line = line.rstrip() + 'text'

            # Fix MD036: Check for emphasis-as-heading patterns
            # Pattern: ### Bold text or similar where whole line is bold
            if re.match(r'^#{1,6}\s+\*\*', line):
                # Replace ** ** with regular text (keep the heading)
                line = re.sub(r'\*\*(.+?)\*\*', r'\1', line)

            fixed_lines.append(line)
            i += 1

        content = '\n'.join(fixed_lines)

        if content != original:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed"
        return False, "No changes"

    except Exception as e:
        return False, str(e)

def main():
    """Process all markdown files"""
    root = Path('.')
    md_files = sorted(root.rglob('*.md'))

    fixed_count = 0
    no_change_count = 0
    error_count = 0

    print(f"[INFO] Processing {len(md_files)} markdown files...")
    print(f"[INFO] Fixing MD040 (code block language) and MD036 (emphasis as heading)\n")

    for md_file in md_files:
        # Skip certain paths
        if any(skip in str(md_file) for skip in ['.git', 'node_modules', '.venv']):
            continue

        success, msg = fix_markdown_file(md_file)

        if success:
            print(f"[FIXED] {md_file}")
            fixed_count += 1
        elif "No changes" in msg:
            no_change_count += 1
        else:
            print(f"[ERROR] {md_file}: {msg}")
            error_count += 1

    print(f"\n[DONE]")
    print(f"  Fixed: {fixed_count}")
    print(f"  No changes: {no_change_count}")
    print(f"  Errors: {error_count}")

if __name__ == '__main__':
    main()
