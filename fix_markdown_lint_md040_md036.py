#!/usr/bin/env python3
"""
Fix common markdownlint issues:
- MD040: Fenced code blocks must have a language specified
- MD036: Emphasis used instead of a heading
"""

import os
import re
from pathlib import Path

def fix_fenced_code_blocks(content):
    """
    Fix MD040: Fenced code blocks should have a language specified
    """
    # Pattern: ``` or ```` without language
    # Replace with ```text or ```bash etc

    # Match opening fence without language
    # Look for ``` followed by newline (no language specified)
    pattern = r'^(```+)\n'

    def replace_fence(match):
        fence = match.group(1)
        # Default to 'text' language
        return f"{fence}text\n"

    content = re.sub(pattern, replace_fence, content, flags=re.MULTILINE)
    return content

def fix_emphasis_as_heading(content):
    """
    Fix MD036: Use heading syntax instead of emphasis
    Pattern: **Bold text at start of line**
    Should be: ## Bold text (or # depending on context)
    """
    lines = content.split('\n')
    fixed_lines = []

    for line in lines:
        # Check if line is emphasis being used as heading (all bold, at line start)
        # Pattern: ^ followed by **text**$
        if re.match(r'^\*\*[^*]+\*\*$', line.strip()):
            # This is likely meant to be a heading
            text = re.sub(r'^\*\*(.+?)\*\*$', r'\1', line.strip())
            # Convert to heading
            line = f"### {text}"

        fixed_lines.append(line)

    return '\n'.join(fixed_lines)

def fix_markdown_file(filepath):
    """Fix markdown linting issues in a single file"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        original_content = content

        # Apply fixes
        content = fix_fenced_code_blocks(content)
        content = fix_emphasis_as_heading(content)

        # Write back if changed
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True, "Fixed"
        else:
            return False, "No changes needed"

    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    """Scan and fix all markdown files"""
    root_path = Path('.')
    md_files = list(root_path.rglob('*.md'))

    fixed_count = 0
    failed_count = 0

    print(f"[INFO] Found {len(md_files)} markdown files")
    print(f"[INFO] Fixing MD040 (code block language) and MD036 (emphasis as heading)...\n")

    for md_file in sorted(md_files):
        # Skip certain directories
        if any(skip in str(md_file) for skip in ['.git', 'node_modules', '.venv', '__pycache__']):
            continue

        success, message = fix_markdown_file(md_file)

        if success:
            print(f"[FIXED] {md_file}")
            fixed_count += 1
        else:
            if "No changes" not in message:
                print(f"[SKIP] {md_file} - {message}")
                failed_count += 1

    print(f"\n[DONE] Fixed: {fixed_count} | Skipped: {len(md_files) - fixed_count - failed_count}")
    if failed_count > 0:
        print(f"[WARN] Failed: {failed_count}")

if __name__ == '__main__':
    main()
