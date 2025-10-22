#!/usr/bin/env python3
"""
Fix all markdown files recursively, including subdirectories.
Follows markdownlint rules:
- Blank lines around headings (MD022)
- Blank lines around lists (MD032)
- No trailing spaces (MD009)
"""

import os
import glob
import re
from pathlib import Path


def fix_markdown_file(filepath):
    """Fix a single markdown file."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
    except Exception as e:
        return False, str(e)

    original_content = content
    lines = content.split('\n')
    fixed_lines = []

    i = 0
    while i < len(lines):
        current_line = lines[i]

        # Remove trailing spaces (MD009)
        current_line = current_line.rstrip()

        # Handle blank lines around headings (MD022)
        if current_line.startswith('#'):
            # Add blank line before heading if needed
            if fixed_lines and fixed_lines[-1].strip() != '':
                fixed_lines.append('')

            fixed_lines.append(current_line)

            # Add blank line after heading if needed (but not at end of file)
            if i + 1 < len(lines) and lines[i + 1].strip() != '':
                if not lines[i + 1].startswith('#'):
                    fixed_lines.append('')

        # Handle blank lines around lists (MD032)
        elif current_line.startswith(('- ', '* ', '+ ', '1. ', '2. ', '3. ')):
            # Add blank line before list if needed
            if fixed_lines and not fixed_lines[-1].startswith(('- ', '* ', '+ ')) and fixed_lines[-1].strip() != '':
                fixed_lines.append('')

            fixed_lines.append(current_line)

            # Add blank line after list if needed
            if i + 1 < len(lines):
                next_line = lines[i + 1].strip()
                if next_line != '' and not lines[i + 1].startswith(('- ', '* ', '+ ')):
                    fixed_lines.append('')

        # Handle code fences - preserve exactly as is
        elif current_line.startswith('```'):
            fixed_lines.append(current_line)

        else:
            fixed_lines.append(current_line)

        i += 1

    # Remove multiple consecutive blank lines
    final_lines = []
    prev_blank = False
    for line in fixed_lines:
        if line.strip() == '':
            if not prev_blank:
                final_lines.append(line)
                prev_blank = True
        else:
            final_lines.append(line)
            prev_blank = False

    # Remove trailing blank lines
    while final_lines and final_lines[-1].strip() == '':
        final_lines.pop()

    # Ensure single newline at end of file
    fixed_content = '\n'.join(final_lines) + '\n'

    # Only write if changed
    if fixed_content != original_content:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(fixed_content)
            return True, "Fixed"
        except Exception as e:
            return False, str(e)
    return False, "Clean"


def main():
    """Fix all markdown files recursively."""
    os.chdir('c:\\Users\\johng\\Documents\\oscar')

    # Get all .md files recursively
    md_files = glob.glob('**/*.md', recursive=True)

    # Filter out node_modules and other dependency directories
    exclude_dirs = {'.git', 'node_modules', '.venv', 'venv', '__pycache__',
                    '.pytest_cache', '.benchmarks', 'htmlcov', '.conda', 'Hunyuan3D-2.1-SOURCE'}

    filtered_files = []
    for f in md_files:
        # Skip files in excluded directories
        skip = False
        for exclude_dir in exclude_dirs:
            if exclude_dir in f.split(os.sep):
                skip = True
                break
        if not skip:
            filtered_files.append(f)

    md_files = sorted(filtered_files)

    if not md_files:
        print("❌ No markdown files found!")
        return

    print(f"\n[*] MARKDOWN FIXER (RECURSIVE) - Processing {len(md_files)} files\n")
    print("=" * 70)

    fixed_count = 0
    clean_count = 0
    error_count = 0

    for md_file in md_files:
        rel_path = Path(md_file).relative_to('.')
        fixed, status = fix_markdown_file(md_file)

        if fixed:
            print(f"[OK] {rel_path}")
            fixed_count += 1
        elif status == "Clean":
            clean_count += 1
        else:
            print(f"[!] {rel_path}: {status[:40]}")
            error_count += 1

    print("=" * 70)
    print(f"\n[SUMMARY]:")
    print(f"   Total files: {len(md_files)}")
    print(f"   Fixed: {fixed_count}")
    print(f"   Already clean: {clean_count}")
    if error_count:
        print(f"   Errors: {error_count}")
    print(f"\n[DONE] All markdown files optimized!\n")
if __name__ == '__main__':
    main()
