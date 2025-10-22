#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Targeted Syntax Fix
========================================

Fix remaining specific syntax issues.
"""

import re
from pathlib import Path

class TargetedSyntaxFix:
    """Fix specific syntax issues"""

    def __init__(self):
        self.backend_dir = Path("backend")

    def fix_main_py_duplicate_try(self) -> bool:
        """Fix duplicate try statements in main.py"""
        try:
            file_path = self.backend_dir / "main.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix duplicate try: statements
            content = re.sub(r'try:\s*\n\s*try:\s*\n', 'try:\n', content)

            # Fix missing indentation for with statements
            content = re.sub(
                r'(\s*)try:\s*\n\s*with open\(',
                r'\1try:\n\1    with open(',
                content
            )

            # Fix missing indentation for other statements after try
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                if line.strip() == 'try:' and i + 1 < len(lines):
                    fixed_lines.append(line)
                    # Ensure next non-empty line is properly indented
                    j = i + 1
                    while j < len(lines) and not lines[j].strip():
                        fixed_lines.append(lines[j])
                        j += 1

                    if j < len(lines):
                        next_line = lines[j]
                        indent = len(line) - len(line.lstrip())
                        if next_line.strip() and not next_line.startswith(' ' * (indent + 4)):
                            # Fix indentation
                            fixed_lines.append(' ' * (indent + 4) + next_line.strip())
                        else:
                            fixed_lines.append(next_line)

                        # Skip the processed line
                        for k in range(i + 1, j + 1):
                            if k != j:  # We already added this line
                                pass
                        i = j
                        continue

                fixed_lines.append(line)

            fixed_content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            return True

        except Exception as e:
            print(f" Error fixing main.py: {e}")
            return False

    def fix_validation_py_try_block(self) -> bool:
        """Fix try block issues in validation.py"""
        try:
            file_path = self.backend_dir / "validation.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix try: without proper indentation
            lines = content.split('\n')
            fixed_lines = []

            i = 0
            while i < len(lines):
                line = lines[i]

                if 'try:' in line and i + 1 < len(lines):
                    # Check if next line is properly indented
                    next_line = lines[i + 1]
                    if next_line.strip() and not next_line.startswith('    '):
                        # Fix indentation
                        fixed_lines.append(line)
                        fixed_lines.append('        ' + next_line.strip())
                        i += 2
                        continue

                fixed_lines.append(line)
                i += 1

            fixed_content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            return True

        except Exception as e:
            print(f" Error fixing validation.py: {e}")
            return False

    def fix_hunyuan_indentation(self) -> bool:
        """Fix indentation issues in hunyuan_integration.py"""
        try:
            file_path = self.backend_dir / "hunyuan_integration.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix indentation issues
            lines = content.split('\n')
            fixed_lines = []

            for line in lines:
                # Detect and fix inconsistent indentation
                if line.strip() and line.startswith(' '):
                    # Count leading spaces
                    spaces = len(line) - len(line.lstrip())
                    # Ensure consistent 4-space indentation
                    if spaces % 4 != 0:
                        # Round to nearest 4-space indent
                        new_spaces = ((spaces + 1) // 4) * 4
                        fixed_lines.append(' ' * new_spaces + line.lstrip())
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            fixed_content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            return True

        except Exception as e:
            print(f" Error fixing hunyuan_integration.py: {e}")
            return False

    def run_targeted_fixes(self):
        """Run all targeted syntax fixes"""
        print(" PHASE 2: Targeted Syntax Fixes")
        print("=" * 35)

        results = {
            'main.py': self.fix_main_py_duplicate_try(),
            'validation.py': self.fix_validation_py_try_block(),
            'hunyuan_integration.py': self.fix_hunyuan_indentation()
        }

        success_count = sum(results.values())
        total_count = len(results)

        print(f"\n TARGETED FIX SUMMARY")
        print(f"   Files processed: {total_count}")
        print(f"   Files fixed: {success_count}")
        print(f"   Success rate: {success_count/total_count*100:.1f}%")

        for file_name, success in results.items():
            status = "" if success else ""
            print(f"   {status} {file_name}")

        return results

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Targeted Fixes")
    print("=" * 42)

    fixer = TargetedSyntaxFix()
    results = fixer.run_targeted_fixes()

    print(f"\n NEXT STEPS:")
    print(f"   1. Run validation to verify all fixes")
    print(f"   2. Proceed with error handling improvements")

    return results

if __name__ == "__main__":
    main()
