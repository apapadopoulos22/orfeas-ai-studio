#!/usr/bin/env python3
"""
ORFEAS AI - Phase 2 Syntax Recovery Script
==========================================

Fix obvious syntax errors from previous enhancement attempts.
"""

import re
from pathlib import Path
from typing import Dict, List

class SyntaxRecoveryTool:
    """Tool to fix common syntax errors from regex enhancements"""

    def __init__(self):
        self.backend_dir = Path("backend")

    def fix_main_py(self) -> bool:
        """Fix main.py syntax issues"""
        try:
            file_path = self.backend_dir / "main.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix the broken hash function around line 3535
            # Replace the broken pattern
            broken_pattern = r'hasher = hashlib\.md5\(\)\s*try:\s*\n\s*with open\(image_path, \'rb\'\) as f:\s*hasher\.update\(f\.read\(\)\)\s*return\s*except FileNotFoundError as e:\s*\n\s*logger\.error\(f"\[ORFEAS\] Image file not found for hash: \{e\}"\)'

            fixed_code = '''hasher = hashlib.md5()
        try:
            with open(image_path, 'rb') as f:
                hasher.update(f.read())
            return hasher.hexdigest()
        except FileNotFoundError as e:
            logger.error(f"[ORFEAS] Image file not found for hash: {e}")
            return "default_hash"'''

            # Try a simpler approach - find and fix the obvious issues
            lines = content.split('\n')
            fixed_lines = []

            i = 0
            while i < len(lines):
                line = lines[i]

                # Fix "try:" with missing indent/content
                if line.strip() == 'try:' and i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if not next_line.strip() or next_line.strip().startswith('with '):
                        # Fix the try block structure
                        fixed_lines.append(line)
                        if i + 1 < len(lines) and lines[i + 1].strip().startswith('with '):
                            fixed_lines.append('            ' + lines[i + 1].strip())
                            i += 2
                            continue

                # Fix broken "return" statements
                if line.strip() == 'return' and i + 1 < len(lines):
                    next_line = lines[i + 1] if i + 1 < len(lines) else ''
                    if next_line.strip().startswith('except'):
                        fixed_lines.append('            return hasher.hexdigest()')
                        fixed_lines.append('')
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
            print(f" Error fixing main.py: {e}")
            return False

    def fix_validation_py(self) -> bool:
        """Fix validation.py syntax issues"""
        try:
            file_path = self.backend_dir / "validation.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix the broken try block
            content = re.sub(
                r'(\s+)try:\s*"""([^"]+)"""',
                r'\1"""Validate job_id is proper UUID format"""\n\1try:',
                content
            )

            # Fix any other obvious issues
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                # Fix try: followed by docstring
                if 'try:' in line and i + 1 < len(lines) and '"""' in lines[i + 1]:
                    # Move docstring before try
                    docstring = lines[i + 1]
                    fixed_lines.append(line.replace('try:', docstring))
                    fixed_lines.append(line.replace(line.strip(), 'try:'))
                    continue
                elif i > 0 and 'try:' in lines[i - 1] and '"""' in line:
                    # Skip this line as it was moved up
                    continue

                fixed_lines.append(line)

            fixed_content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            return True

        except Exception as e:
            print(f" Error fixing validation.py: {e}")
            return False

    def fix_hunyuan_integration_py(self) -> bool:
        """Fix hunyuan_integration.py syntax issues"""
        try:
            file_path = self.backend_dir / "hunyuan_integration.py"
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Fix the broken try block
            lines = content.split('\n')
            fixed_lines = []

            for i, line in enumerate(lines):
                # Fix "try:" without proper content
                if line.strip() == 'try:' and i + 1 < len(lines):
                    next_line = lines[i + 1]
                    if not next_line.strip().startswith(' ') or len(next_line.strip()) == 0:
                        # Fix indentation
                        fixed_lines.append(line)
                        if i + 1 < len(lines):
                            fixed_lines.append('            ' + lines[i + 1].strip())
                        continue

                fixed_lines.append(line)

            fixed_content = '\n'.join(fixed_lines)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_content)

            return True

        except Exception as e:
            print(f" Error fixing hunyuan_integration.py: {e}")
            return False

    def run_syntax_recovery(self) -> Dict[str, bool]:
        """Run syntax recovery on all corrupted files"""
        print(" PHASE 2: Syntax Recovery")
        print("=" * 30)

        results = {
            'main.py': self.fix_main_py(),
            'validation.py': self.fix_validation_py(),
            'hunyuan_integration.py': self.fix_hunyuan_integration_py()
        }

        success_count = sum(results.values())
        total_count = len(results)

        print(f"\n SYNTAX RECOVERY SUMMARY")
        print(f"   Files processed: {total_count}")
        print(f"   Files fixed: {success_count}")
        print(f"   Success rate: {success_count/total_count*100:.1f}%")

        for file_name, success in results.items():
            status = "" if success else ""
            print(f"   {status} {file_name}")

        return results

def main():
    """Main execution function"""
    print(" ORFEAS AI - Phase 2 Syntax Recovery")
    print("=" * 45)

    recovery_tool = SyntaxRecoveryTool()
    results = recovery_tool.run_syntax_recovery()

    print(f"\n NEXT STEPS:")
    print(f"   1. Run validation to verify fixes")
    print(f"   2. Add careful error handling enhancements")

    return results

if __name__ == "__main__":
    main()
