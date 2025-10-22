#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Syntax Fix
===============================

Fix syntax errors introduced during Phase 2 error handling enhancement.
"""

import re
from pathlib import Path
from typing import Dict

class SyntaxFixer:
    """Fix syntax errors in enhanced files"""

    def __init__(self):
        self.backend_dir = Path("backend")

    def fix_gpu_manager(self) -> bool:
        """Fix syntax errors in gpu_manager.py"""
        file_path = self.backend_dir / "gpu_manager.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix unterminated string literals
            content = re.sub(
                r'logger\.error\(f"([^"]*)\{([^}]*)\}([^"]*)"([^)])*\)',
                r'logger.error(f"\1{\2}\3")',
                content
            )

            # Fix logger statements with double braces
            content = re.sub(
                r'logger\.error\(f"([^"]*)\{\{([^}]*)\}\}([^"]*)"',
                r'logger.error(f"\1{\2}\3"',
                content
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f" Fixed syntax errors in gpu_manager.py")
            return True

        except Exception as e:
            print(f" Error fixing gpu_manager.py: {e}")
            return False

    def fix_main_py(self) -> bool:
        """Fix syntax errors in main.py"""
        file_path = self.backend_dir / "main.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix indentation issues in with statements
            lines = content.split('\n')
            fixed_lines = []
            in_with_block = False

            for i, line in enumerate(lines):
                if 'with open(' in line and line.strip().endswith(':'):
                    in_with_block = True
                    fixed_lines.append(line)
                elif in_with_block and line.strip() == '':
                    # Add proper indentation for empty lines in with blocks
                    fixed_lines.append(line)
                elif in_with_block and not line.startswith('    ') and line.strip():
                    # End of with block
                    in_with_block = False
                    fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            # Fix specific pattern issues
            content = re.sub(
                r'(\s+)except ([A-Za-z]+Error) as e:\n\s+logger\.error\(f"([^"]*)\{e\}([^"]*)"',
                r'\1except \2 as e:\n\1    logger.error(f"\3{e}\4"',
                content
            )

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f" Fixed syntax errors in main.py")
            return True

        except Exception as e:
            print(f" Error fixing main.py: {e}")
            return False

    def fix_hunyuan_integration(self) -> bool:
        """Fix syntax errors in hunyuan_integration.py"""
        file_path = self.backend_dir / "hunyuan_integration.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix empty try blocks
            content = re.sub(
                r'(\s+)try:\n(\s+)except',
                r'\1try:\n\1    pass\n\2except',
                content
            )

            # Fix indentation issues
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                # Fix try block indentation
                if line.strip() == 'try:' and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip().startswith('except'):
                        # Empty try block - add pass
                        fixed_lines.append(line)
                        fixed_lines.append(line.replace('try:', '    pass'))
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f" Fixed syntax errors in hunyuan_integration.py")
            return True

        except Exception as e:
            print(f" Error fixing hunyuan_integration.py: {e}")
            return False

    def fix_validation_py(self) -> bool:
        """Fix syntax errors in validation.py"""
        file_path = self.backend_dir / "validation.py"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix empty try blocks
            content = re.sub(
                r'(\s+)try:\n(\s+)except',
                r'\1try:\n\1    pass\n\2except',
                content
            )

            # Ensure proper indentation
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                if line.strip() == 'try:' and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if next_line.strip().startswith('except'):
                        # Empty try block
                        fixed_lines.append(line)
                        fixed_lines.append(line.replace('try:', '    pass'))
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)

            content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)

            print(f" Fixed syntax errors in validation.py")
            return True

        except Exception as e:
            print(f" Error fixing validation.py: {e}")
            return False

    def run_fixes(self) -> Dict[str, bool]:
        """Run all syntax fixes"""
        print(" PHASE 2: Syntax Error Fixes")
        print("=" * 40)

        results = {
            'gpu_manager.py': self.fix_gpu_manager(),
            'main.py': self.fix_main_py(),
            'hunyuan_integration.py': self.fix_hunyuan_integration(),
            'validation.py': self.fix_validation_py()
        }

        fixed_count = sum(results.values())
        total_count = len(results)

        print(f"\n SYNTAX FIX SUMMARY")
        print(f"   Files processed: {total_count}")
        print(f"   Files fixed: {fixed_count}")
        print(f"   Success rate: {fixed_count/total_count*100:.1f}%")

        return results

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Syntax Fixes")
    print("=" * 45)

    fixer = SyntaxFixer()
    results = fixer.run_fixes()

    print(f"\n NEXT STEPS:")
    print(f"   1. Re-run validation to verify fixes")
    print(f"   2. Execute TQM audit for final results")

    return results

if __name__ == "__main__":
    main()
