#!/usr/bin/env python3
"""Verify emoji removal was successful"""
import re
from pathlib import Path

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

test_files = [
    ".github/copilot-instructions.md",
    ".github/workflows/markdown-lint.yml",
    "docs/.github/CONTRIBUTING.md",
]

print("\n" + "="*70)
print("EMOJI REMOVAL VERIFICATION")
print("="*70 + "\n")

total_emojis_found = 0
files_checked = 0

for file_path in test_files:
    try:
        path = Path(file_path)
        if not path.exists():
            print(f"❌ {file_path:<50} - FILE NOT FOUND")
            continue

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        emojis = EMOJI_PATTERN.findall(content)
        emoji_count = len(emojis)
        total_emojis_found += emoji_count
        files_checked += 1

        status = "✅ CLEAN" if emoji_count == 0 else f"⚠️  {emoji_count} EMOJIS FOUND"
        print(f"{status:20} {file_path:<50}")

    except Exception as e:
        print(f"❌ {file_path:<50} - ERROR: {e}")

print("\n" + "="*70)
print("VERIFICATION RESULTS")
print("="*70)
print(f"Files checked: {files_checked}")
print(f"Total emojis found: {total_emojis_found}")
print(f"Status: {'✅ SUCCESS - ALL CLEAN' if total_emojis_found == 0 else '⚠️  WARNING - EMOJIS STILL PRESENT'}")
print("="*70 + "\n")
