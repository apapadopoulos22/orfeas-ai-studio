#!/usr/bin/env python3
"""Remove all emojis from project files"""
import os
import re
import sys
from pathlib import Path

# Emoji pattern - matches Unicode characters in emoji ranges
EMOJI_PATTERN = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"  # Enclosed characters
    "\U0001f926-\U0001f937"  # People
    "\U00010000-\U0010ffff"  # Other characters
    "\u2640-\u2642"          # Gender symbols
    "\u2600-\u2B55"          # Miscellaneous symbols
    "\u200d"                 # Zero width joiner
    "\u23cf"                 # Play symbol
    "\u23e9"                 # Fast forward
    "\u231b"                 # Hourglass
    "]+",
    flags=re.UNICODE
)

def remove_emojis_from_file(file_path):
    """Remove emojis from a file and return if changes were made"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        original_length = len(content)
        new_content = EMOJI_PATTERN.sub('', content)
        new_length = len(new_content)

        if original_length != new_length:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)

            chars_removed = original_length - new_length
            return True, chars_removed
        return False, 0

    except Exception as e:
        return None, str(e)

def main():
    project_root = Path('c:\\Users\\johng\\Documents\\oscar')
    file_extensions = {'.md', '.py', '.html', '.ps1', '.txt', '.json', '.yml', '.yaml'}

    files_changed = 0
    total_chars_removed = 0
    files_with_errors = []

    print("=" * 80)
    print("EMOJI REMOVAL SCRIPT - Scanning project files")
    print("=" * 80)

    for file_path in project_root.rglob('*'):
        if not file_path.is_file():
            continue

        if file_path.suffix.lower() not in file_extensions:
            continue

        # Skip certain directories - but INCLUDE .github (legitimate config)
        relative_path = file_path.relative_to(project_root)
        excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.next'}
        if any(part in excluded_dirs for part in relative_path.parts):
            continue

        result, data = remove_emojis_from_file(str(file_path))

        if result is None:
            files_with_errors.append((str(relative_path), data))
            print(f" ERROR: {relative_path} - {data}")
        elif result:
            files_changed += 1
            total_chars_removed += data
            print(f" CLEANED: {relative_path} ({data} chars removed)")

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Files cleaned: {files_changed}")
    print(f"Total characters removed: {total_chars_removed}")
    print(f"Files with errors: {len(files_with_errors)}")

    if files_with_errors:
        print("\nFiles with errors:")
        for fname, error in files_with_errors:
            print(f"  - {fname}: {error}")

    print("=" * 80)
    return 0 if not files_with_errors else 1

if __name__ == '__main__':
    sys.exit(main())
