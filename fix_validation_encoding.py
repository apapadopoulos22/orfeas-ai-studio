#!/usr/bin/env python3
"""
Fix encoding issues in validate_ultra_performance.py
Repairs UTF-8 mojibake corruption affecting emoji characters
"""

# Mojibake mapping: corrupted → correct
MOJIBAKE_FIXES = {
    'ðŸš€': '',  # Rocket
    'âœ…': '',  # Check mark
    'Ã¢Å¡Â¡': '',  # Lightning
    'ï¿½': '',  # Target (context-dependent)
    'ðŸ"‹': '',  # Clipboard
    'ðŸ"'': '',  # Lock
    'ðŸ§ ': '',  # Brain
    'ðŸ"„': '',  # Repeat
    'Ã¢ÂÂ': '',  # X mark
    # Warning sign already fixed manually
}

def fix_encoding(file_path: str) -> None:
    """Fix mojibake encoding issues in the specified file"""

    print(f"Reading {file_path}...")
    with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()

    original_content = content

    # Apply all fixes
    for corrupted, correct in MOJIBAKE_FIXES.items():
        if corrupted in content:
            count = content.count(corrupted)
            content = content.replace(corrupted, correct)
            print(f"  Fixed {count} occurrence(s) of '{corrupted}' → '{correct}'")

    # Check if anything changed
    if content != original_content:
        print(f"\nWriting corrected content to {file_path}...")
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print(" File encoding fixed successfully!")
    else:
        print("ℹ No encoding issues found (file already correct)")

if __name__ == '__main__':
    fix_encoding('validate_ultra_performance.py')
