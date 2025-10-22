#!/usr/bin/env python3
"""
Comprehensive emoji removal script for ORFEAS project
Removes all emoji characters from all project files
"""
import os
import re
from pathlib import Path

# Comprehensive emoji pattern
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

TARGET_EXTENSIONS = {'.md', '.py', '.html', '.ps1', '.txt', '.json', '.yml', '.yaml', '.sh', '.bat'}

def remove_emojis_from_file(filepath):
    """Remove emojis from a file, return (success, chars_removed, error_msg)"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()

        original_len = len(content)
        new_content = EMOJI_PATTERN.sub('', content)
        new_len = len(new_content)

        if original_len == new_len:
            # No changes needed
            return False, 0, None

        # Write back the cleaned content
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        chars_removed = original_len - new_len
        return True, chars_removed, None

    except Exception as e:
        return False, 0, str(e)

def main():
    """Main function to scan and clean all project files"""
    project_root = Path('.')

    files_scanned = 0
    files_cleaned = 0
    total_chars_removed = 0
    errors = []

    print("\n" + "="*70)
    print("COMPREHENSIVE EMOJI REMOVAL - ORFEAS PROJECT")
    print("="*70 + "\n")

    # Walk through all directories
    for root, dirs, files in os.walk(project_root):
        # Skip hidden directories (except .github) and common exclusions
        # .github is legitimate project config, .git is not
        exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', '.next', '.eslintcache', 'build', 'dist', 'coverage'}
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in sorted(files):
            # Only process target file types
            if not any(file.endswith(ext) for ext in TARGET_EXTENSIONS):
                continue

            filepath = os.path.join(root, file)
            files_scanned += 1

            success, chars_removed, error = remove_emojis_from_file(filepath)

            if error:
                errors.append((filepath, error))
                print(f"[ERROR] {filepath}")
                print(f"        {error}\n")
            elif success and chars_removed > 0:
                files_cleaned += 1
                total_chars_removed += chars_removed
                rel_path = os.path.relpath(filepath)
                print(f" {rel_path:<70} ({chars_removed} chars)")

    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Files scanned:           {files_scanned}")
    print(f"Files cleaned:           {files_cleaned}")
    print(f"Total chars removed:     {total_chars_removed:,}")
    print(f"Errors encountered:      {len(errors)}")

    if errors:
        print("\nFiles with errors:")
        for filepath, error in errors:
            print(f"  - {filepath}: {error}")

    print("="*70 + "\n")

    if total_chars_removed > 0:
        print(f"SUCCESS! Removed {total_chars_removed:,} emoji characters from {files_cleaned} files\n")
    else:
        print("No emojis found to remove.\n")

if __name__ == "__main__":
    main()
