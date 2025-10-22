#!/usr/bin/env python3
"""
Debug TQM audit encoding detection - identify which file is flagged
"""
import os
import glob

def check_python_files() -> None:
    """Check all Python files for encoding issues"""

    python_files = []

    # Get all Python files in the project
    for pattern in ['*.py', 'backend/**/*.py', 'scripts/**/*.py']:
        python_files.extend(glob.glob(pattern, recursive=True))

    files_with_issues = []

    for py_file in python_files:
        # Skip backup directory
        if 'encoding_backups' in py_file:
            continue

        try:
            with open(py_file, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Check for encoding issues
            if any(x in content for x in ['Ãƒ', 'Ã¢â‚¬', 'Ã…']):
                # Check if it's a pattern definition (false positive)
                is_pattern_definition = (
                    "mojibake_patterns = [" in content or
                    "['Ãƒ', 'Ã¢â‚¬', 'Ã…']" in content or
                    'if any(x in content for x in [' in content
                )

                if not is_pattern_definition:
                    files_with_issues.append(py_file)
                    print(f"ðŸ”´ ENCODING ISSUE: {py_file}")

                    # Show context
                    lines = content.split('\n')
                    for i, line in enumerate(lines, 1):
                        if any(x in line for x in ['Ãƒ', 'Ã¢â‚¬', 'Ã…']):
                            print(f"  Line {i}: {line[:100]}")
                else:
                    print(f"âœ“ Pattern definition (OK): {py_file}")

        except Exception as e:
            pass

    print(f"\n" + "=" * 60)
    print(f"Total files with encoding issues: {len(files_with_issues)}")
    for f in files_with_issues:
        print(f"  - {f}")
    print("=" * 60)

if __name__ == "__main__":
    check_python_files()
