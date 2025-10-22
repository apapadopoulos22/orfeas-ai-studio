import os
import sys
import glob
import json
import shutil
from ftfy import fix_text
import unicodedata
import chardet
from charset_normalizer import from_bytes
from typing import Any, Tuple

def detect_encoding(file_path: str) -> str:
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
    if chardet_result['encoding']:
        return chardet_result['encoding'].lower()
    # charset-normalizer
    normalizer_result = from_bytes(raw).best()
    if normalizer_result:
        return str(normalizer_result.encoding).lower()
    # fallback
    return 'utf-8'

def normalize_text(text: Any) -> None:
    # NFC normalization and ftfy
    text = unicodedata.normalize('NFC', text)
    text = fix_text(text)
    return text

def fix_file_encoding(file_path: str, backup_dir: Any) -> Tuple:
    encoding = detect_encoding(file_path)
    try:
        with open(file_path, 'r', encoding=encoding, errors='replace') as f:
            content = f.read()
        fixed = normalize_text(content)
        # Only write if changed
        if fixed != content:
            # Backup original
            rel_path = os.path.relpath(file_path)
            backup_path = os.path.join(backup_dir, rel_path)
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            shutil.copy2(file_path, backup_path)
            # Write fixed
            with open(file_path, 'w', encoding='utf-8', errors='replace') as f:
                f.write(fixed)
            return True, encoding
        else:
            return False, encoding
    except Exception as e:
        return False, f"ERROR: {e}"

def main() -> None:
    # File patterns
    patterns = [
        '**/*.md', '**/*.py', '**/*.txt', '**/*.html', '**/*.json'
    ]
    root = os.path.abspath(os.path.dirname(__file__))
    backup_dir = os.path.join(root, 'encoding_backups')
    stats = {'total': 0, 'fixed': 0, 'errors': 0, 'details': []}
    for pat in patterns:
        for file_path in glob.glob(os.path.join(root, '..', pat), recursive=True):
            if not os.path.isfile(file_path):
                continue
            stats['total'] += 1
            fixed, info = fix_file_encoding(file_path, backup_dir)
            if fixed:
                stats['fixed'] += 1
            if isinstance(info, str) and info.startswith('ERROR:'):
                stats['errors'] += 1
            stats['details'].append({'file': file_path, 'fixed': fixed, 'encoding': info})
    # Write summary
    with open(os.path.join(root, 'encoding_fix_summary.json'), 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    print(f"Encoding fix complete. {stats['fixed']} files fixed out of {stats['total']}. Errors: {stats['errors']}")

if __name__ == '__main__':
    main()
