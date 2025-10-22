#!/usr/bin/env python3
"""
Markdown Lint Fixer
Automatically fixes common markdown linting issues across multiple files.
"""

import os
import re
from pathlib import Path
from typing import List, Tuple

# Define the rules to fix
RULES = {
    'MD012': 'Multiple consecutive blank lines',
    'MD022': 'Headings should be surrounded by blank lines',
    'MD031': 'Fenced code blocks should be surrounded by blank lines',
    'MD032': 'Lists should be surrounded by blank lines',
    'MD009': 'Trailing spaces',
    'MD040': 'Fenced code blocks should have a language specified',
}

def fix_multiple_blank_lines(content: str) -> Tuple[str, int]:
    """Fix MD012: Multiple consecutive blank lines"""
    fixes = 0
    # Replace 3+ consecutive newlines with 2 newlines (1 blank line)
    pattern = r'\n\n\n+'
    new_content = content
    while re.search(pattern, new_content):
        new_content = re.sub(pattern, '\n\n', new_content)
        fixes += 1
    return new_content, fixes

def fix_trailing_spaces(content: str) -> Tuple[str, int]:
    """Fix MD009: Trailing spaces"""
    fixes = 0
    lines = content.split('\n')
    new_lines = []
    for line in lines:
        original = line
        # Keep exactly 2 trailing spaces (for line breaks), remove others
        if line.endswith('  '):
            new_lines.append(line)
        else:
            stripped = line.rstrip()
            if stripped != original:
                fixes += 1
            new_lines.append(stripped)
    return '\n'.join(new_lines), fixes

def fix_headings_blank_lines(content: str) -> Tuple[str, int]:
    """Fix MD022: Headings should be surrounded by blank lines"""
    fixes = 0
    lines = content.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        # Check if this is a heading (starts with #)
        if line.strip().startswith('#') and not line.strip().startswith('#!'):
            # Check if previous line exists and is not blank
            if i > 0 and lines[i-1].strip() != '':
                new_lines.append('')  # Add blank line before
                fixes += 1

            new_lines.append(line)

            # Check if next line exists and is not blank
            if i < len(lines) - 1 and lines[i+1].strip() != '':
                new_lines.append('')  # Add blank line after
                fixes += 1
        else:
            new_lines.append(line)

    return '\n'.join(new_lines), fixes

def fix_fenced_code_blocks(content: str) -> Tuple[str, int]:
    """Fix MD031: Fenced code blocks should be surrounded by blank lines"""
    fixes = 0
    lines = content.split('\n')
    new_lines = []
    in_code_block = False

    for i, line in enumerate(lines):
        # Check if this is a code fence
        if line.strip().startswith('```'):
            if not in_code_block:
                # Opening fence - ensure blank line before
                if i > 0 and lines[i-1].strip() != '':
                    new_lines.append('')
                    fixes += 1
                in_code_block = True
            else:
                # Closing fence - ensure blank line after
                in_code_block = False
                new_lines.append(line)
                if i < len(lines) - 1 and lines[i+1].strip() != '':
                    new_lines.append('')
                    fixes += 1
                continue

        new_lines.append(line)

    return '\n'.join(new_lines), fixes

def fix_lists_blank_lines(content: str) -> Tuple[str, int]:
    """Fix MD032: Lists should be surrounded by blank lines"""
    fixes = 0
    lines = content.split('\n')
    new_lines = []

    for i, line in enumerate(lines):
        # Check if this is a list item (starts with -, *, or number.)
        is_list_item = (line.strip().startswith(('-', '*')) or
                       re.match(r'^\s*\d+\.', line))

        if is_list_item:
            # Check if previous line is not blank and not a list item
            if i > 0:
                prev_line = lines[i-1]
                prev_is_list = (prev_line.strip().startswith(('-', '*')) or
                               re.match(r'^\s*\d+\.', prev_line))
                if prev_line.strip() != '' and not prev_is_list:
                    new_lines.append('')
                    fixes += 1

            new_lines.append(line)

            # Check if next line exists and is not blank and not a list item
            if i < len(lines) - 1:
                next_line = lines[i+1]
                next_is_list = (next_line.strip().startswith(('-', '*')) or
                               re.match(r'^\s*\d+\.', next_line))
                if next_line.strip() != '' and not next_is_list:
                    new_lines.append('')
                    fixes += 1
        else:
            new_lines.append(line)

    return '\n'.join(new_lines), fixes

def fix_markdown_file(filepath: Path) -> dict:
    """Fix markdown linting issues in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content
        total_fixes = 0
        fixes_by_rule = {}

        # Apply fixes in order
        content, fixes = fix_multiple_blank_lines(content)
        if fixes > 0:
            fixes_by_rule['MD012'] = fixes
            total_fixes += fixes

        content, fixes = fix_trailing_spaces(content)
        if fixes > 0:
            fixes_by_rule['MD009'] = fixes
            total_fixes += fixes

        content, fixes = fix_headings_blank_lines(content)
        if fixes > 0:
            fixes_by_rule['MD022'] = fixes
            total_fixes += fixes

        content, fixes = fix_fenced_code_blocks(content)
        if fixes > 0:
            fixes_by_rule['MD031'] = fixes
            total_fixes += fixes

        content, fixes = fix_lists_blank_lines(content)
        if fixes > 0:
            fixes_by_rule['MD032'] = fixes
            total_fixes += fixes

        # Only write if changes were made
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)

            return {
                'status': 'fixed',
                'total_fixes': total_fixes,
                'fixes_by_rule': fixes_by_rule
            }
        else:
            return {'status': 'clean'}

    except Exception as e:
        return {'status': 'error', 'error': str(e)}

def main():
    """Main function to scan and fix all markdown files"""
    base_dir = Path(__file__).parent
    md_files = list(base_dir.glob('**/*.md'))

    # Filter out some directories we might want to skip
    skip_dirs = {'node_modules', '.git', 'htmlcov', 'ARCHIVE', '.venv'}
    md_files = [f for f in md_files if not any(skip in str(f) for skip in skip_dirs)]

    print(f"Found {len(md_files)} markdown files to check\n")
    print("=" * 80)

    fixed_files = []
    clean_files = []
    error_files = []

    for md_file in md_files:
        result = fix_markdown_file(md_file)

        if result['status'] == 'fixed':
            fixed_files.append((md_file, result))
            print(f"'úÖ FIXED: {md_file.relative_to(base_dir)}")
            print(f"   Total fixes: {result['total_fixes']}")
            for rule, count in result['fixes_by_rule'].items():
                print(f"   - {rule} ({RULES[rule]}): {count} fix(es)")
            print()
        elif result['status'] == 'clean':
            clean_files.append(md_file)
        else:
            error_files.append((md_file, result['error']))
            print(f"'ùå ERROR: {md_file.relative_to(base_dir)}")
            print(f"   {result['error']}\n")

    print("=" * 80)
    print("\nüìä SUMMARY:")
    print(f"   'úÖ Fixed: {len(fixed_files)} file(s)")
    print(f"   'úì  Clean: {len(clean_files)} file(s)")
    print(f"   'ùå Errors: {len(error_files)} file(s)")
    print(f"    Total: {len(md_files)} file(s)")

    if fixed_files:
        print("\nüîß FILES FIXED:")
        for md_file, result in fixed_files:
            print(f"   - {md_file.relative_to(base_dir)} ({result['total_fixes']} fixes)")

    if error_files:
        print("\n  FILES WITH ERRORS:")
        for md_file, error in error_files:
            print(f"   - {md_file.relative_to(base_dir)}: {error}")

    print("\n'ú® Markdown lint fix complete!")

if __name__ == '__main__':
    main()
