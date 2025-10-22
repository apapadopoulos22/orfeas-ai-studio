#!/usr/bin/env python3
"""
Targeted encoding fix for remaining files with non-standard encoding
"""

import os
import sys
import json
import shutil
from ftfy import fix_text
import unicodedata
import chardet
from charset_normalizer import from_bytes

def detect_encoding(file_path: str) -> str:
    """Detect file encoding with BOM and fallback detection"""
    with open(file_path, 'rb') as f:
        raw = f.read()

    # BOM detection
    if raw.startswith(b'\xef\xbb\xbf'):
        return 'utf-8-sig'
    if raw.startswith(b'\xff\xfe'):
        return 'utf-16-le'
    if raw.startswith(b'\xfe\xff'):
        return 'utf-16-be'

    # chardet
    chardet_result = chardet.detect(raw)
    if chardet_result['encoding'] and chardet_result['confidence'] > 0.7:
        return chardet_result['encoding'].lower()

    # charset-normalizer
    normalizer_result = from_bytes(raw).best()
    if normalizer_result:
        return str(normalizer_result.encoding).lower()

    return 'utf-8'

def fix_file_encoding(file_path: str) -> int:
    """Fix encoding for a single file"""
    encoding = detect_encoding(file_path)

    print(f"Processing: {os.path.relpath(file_path)}")
    print(f"  Detected encoding: {encoding}")

    try:
        # Read with detected encoding
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()

        # Apply ftfy and NFC normalization
        fixed = fix_text(content)
        fixed = unicodedata.normalize('NFC', fixed)

        # Check if changed
        if fixed != content:
            # Backup
            backup_path = file_path + '.encoding.bak'
            shutil.copy2(file_path, backup_path)
            print(f"  Created backup: {os.path.basename(backup_path)}")

            # Write fixed
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(fixed)

            print(f"   Fixed and saved as UTF-8")
            return True
        else:
            print(f"   Already clean")
            return False

    except Exception as e:
        print(f"   Error: {e}")
        return False

def main() -> None:
    # Load encoding summary to find files needing attention
    summary_path = 'scripts/encoding_fix_summary.json'

    if not os.path.exists(summary_path):
        print("Error: encoding_fix_summary.json not found")
        sys.exit(1)

    with open(summary_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Find files with non-standard encoding that weren't fixed
    standard_encodings = {'utf-8', 'utf_8', 'ascii'}
    files_to_fix = []

    for detail in data['details']:
        encoding = detail.get('encoding', '')
        fixed = detail.get('fixed', False)

        if encoding not in standard_encodings and not fixed and not encoding.startswith('ERROR'):
            files_to_fix.append(detail['file'])

    print("="*80)
    print(f"TARGETED ENCODING FIX")
    print("="*80)
    print(f"Files to fix: {len(files_to_fix)}")
    print("="*80)
    print()

    if not files_to_fix:
        print(" No files need fixing!")
        return

    # Fix each file
    fixed_count = 0
    for file_path in files_to_fix:
        if os.path.exists(file_path):
            if fix_file_encoding(file_path):
                fixed_count += 1
            print()

    print("="*80)
    print(f"SUMMARY:")
    print(f"  Files processed: {len(files_to_fix)}")
    print(f"  Files fixed: {fixed_count}")
    print("="*80)

if __name__ == '__main__':
    main()
