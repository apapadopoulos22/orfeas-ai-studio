#!/usr/bin/env python3
"""
ORFEAS AI - Targeted Syntax Recovery for Phase 2 Completion
===========================================================

Fix specific syntax issues blocking Phase 2 completion.
"""

import ast
import re
from pathlib import Path
from datetime import datetime

class TargetedSyntaxRecovery:
    """Targeted syntax recovery for specific files"""

    def __init__(self):
        self.backend_dir = Path("backend")
        self.fixes_applied = []

    def fix_main_py_line_170(self):
        """Fix main.py syntax error at line 170"""

        file_path = self.backend_dir / "main.py"
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Look for problematic patterns around line 170
            fixed = False
            for i in range(max(0, 165), min(len(lines), 175)):
                line = lines[i].strip()

                # Fix common issues
                if line.startswith('try:try:'):
                    lines[i] = lines[i].replace('try:try:', 'try:')
                    fixed = True
                    self.fixes_applied.append(f"main.py line {i+1}: Fixed duplicate try")

                elif 'try:' in line and line.count('try:') > 1:
                    # Remove duplicate try statements
                    lines[i] = re.sub(r'try:\s*try:', 'try:', lines[i])
                    fixed = True
                    self.fixes_applied.append(f"main.py line {i+1}: Removed duplicate try")

                # Fix incomplete try blocks
                elif line == 'try:' and i+1 < len(lines):
                    next_line = lines[i+1].strip()
                    if next_line.startswith('except') or next_line.startswith('finally'):
                        # Insert a pass statement
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        lines.insert(i+1, ' ' * (indent + 4) + 'pass\n')
                        fixed = True
                        self.fixes_applied.append(f"main.py line {i+1}: Added pass to empty try block")

            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing main.py: {e}")

        return False

    def fix_hunyuan_integration_line_38(self):
        """Fix hunyuan_integration.py indentation error at line 38"""

        file_path = self.backend_dir / "hunyuan_integration.py"
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Fix indentation issues around line 38
            fixed = False
            for i in range(max(0, 35), min(len(lines), 45)):
                line = lines[i]

                # Look for indentation problems
                if line.strip() and len(line) - len(line.lstrip()) % 4 != 0:
                    # Fix to proper 4-space indentation
                    content = line.lstrip()
                    if content:
                        # Determine proper indentation level
                        level = 0
                        if i > 0:
                            prev_line = lines[i-1].strip()
                            if prev_line.endswith(':'):
                                level = 1
                            elif any(keyword in prev_line for keyword in ['class ', 'def ', 'if ', 'try:', 'except', 'with ']):
                                level = 1

                        proper_indent = ' ' * (level * 4)
                        lines[i] = proper_indent + content
                        fixed = True
                        self.fixes_applied.append(f"hunyuan_integration.py line {i+1}: Fixed indentation")

            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing hunyuan_integration.py: {e}")

        return False

    def fix_validation_py_line_49(self):
        """Fix validation.py expected indented block error at line 49"""

        file_path = self.backend_dir / "validation.py"
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Fix empty try block around line 49
            fixed = False
            for i in range(max(0, 46), min(len(lines), 54)):
                line = lines[i].strip()

                if line == 'try:':
                    # Check if next line is properly indented
                    if i+1 < len(lines):
                        next_line = lines[i+1]
                        if next_line.strip().startswith(('except', 'finally')) or not next_line.strip():
                            # Insert pass statement
                            indent = len(lines[i]) - len(lines[i].lstrip())
                            lines.insert(i+1, ' ' * (indent + 4) + 'pass\n')
                            fixed = True
                            self.fixes_applied.append(f"validation.py line {i+1}: Added pass to empty try block")
                            break

            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing validation.py: {e}")

        return False

    def fix_production_metrics_line_255(self):
        """Fix production_metrics.py expected except/finally block at line 255"""

        file_path = self.backend_dir / "production_metrics.py"
        if not file_path.exists():
            return False

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Fix incomplete try block around line 255
            fixed = False
            for i in range(max(0, 250), min(len(lines), 260)):
                line = lines[i].strip()

                if line == 'try:' or (line.startswith('try:') and not line.endswith(':')):
                    # Look for corresponding except/finally
                    has_except = False
                    has_finally = False

                    for j in range(i+1, min(len(lines), i+10)):
                        next_line = lines[j].strip()
                        if next_line.startswith('except'):
                            has_except = True
                            break
                        elif next_line.startswith('finally'):
                            has_finally = True
                            break
                        elif next_line and not next_line.startswith('#') and len(lines[j]) - len(lines[j].lstrip()) <= len(lines[i]) - len(lines[i].lstrip()):
                            # End of try block without except/finally
                            break

                    if not has_except and not has_finally:
                        # Add generic exception handler
                        indent = len(lines[i]) - len(lines[i].lstrip())
                        try_content = f"{' ' * (indent + 4)}pass\n"
                        except_content = f"{' ' * indent}except Exception as e:\n{' ' * (indent + 4)}logger.error(f'Error: {{e}}')\n{' ' * (indent + 4)}raise\n"

                        # Insert after try line
                        lines.insert(i+1, try_content)
                        lines.insert(i+2, except_content)
                        fixed = True
                        self.fixes_applied.append(f"production_metrics.py line {i+1}: Added except block to try statement")
                        break

            if fixed:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.writelines(lines)
                return True

        except Exception as e:
            print(f"Error fixing production_metrics.py: {e}")

        return False

    def validate_syntax(self, file_path):
        """Validate Python syntax of a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            ast.parse(content)
            return True, None
        except SyntaxError as e:
            return False, f"Line {e.lineno}: {e.msg}"
        except Exception as e:
            return False, str(e)

    def run_targeted_recovery(self):
        """Run targeted syntax recovery"""

        print(" ORFEAS AI - Targeted Syntax Recovery")
        print("=" * 42)
        print(f"Started: {datetime.now().strftime('%H:%M:%S')}")
        print()

        # Target files with specific fixes
        fixes = [
            ("main.py", self.fix_main_py_line_170),
            ("hunyuan_integration.py", self.fix_hunyuan_integration_line_38),
            ("validation.py", self.fix_validation_py_line_49),
            ("production_metrics.py", self.fix_production_metrics_line_255)
        ]

        results = {}

        for filename, fix_func in fixes:
            file_path = self.backend_dir / filename

            print(f" Processing {filename}...")

            # Check current syntax
            is_valid_before, error_before = self.validate_syntax(file_path)

            if is_valid_before:
                print(f"   Already valid syntax")
                results[filename] = "already_valid"
                continue
            else:
                print(f"   Syntax error: {error_before}")

            # Apply fix
            if fix_func():
                # Check syntax after fix
                is_valid_after, error_after = self.validate_syntax(file_path)

                if is_valid_after:
                    print(f"   Fixed successfully")
                    results[filename] = "fixed"
                else:
                    print(f"   Still has error: {error_after}")
                    results[filename] = "still_broken"
            else:
                print(f"   Fix failed")
                results[filename] = "fix_failed"

            print()

        # Summary
        print(" RECOVERY SUMMARY")
        print("-" * 20)
        fixed_count = sum(1 for status in results.values() if status in ["fixed", "already_valid"])
        total_count = len(results)

        print(f"Files processed: {total_count}")
        print(f"Successfully fixed/valid: {fixed_count}")
        print(f"Success rate: {(fixed_count/total_count)*100:.1f}%")
        print()

        if self.fixes_applied:
            print(" FIXES APPLIED:")
            for fix in self.fixes_applied:
                print(f"  • {fix}")
            print()

        print(" Next: Run PHASE2_VALIDATION.py to verify fixes")

        return results

def main():
    """Main execution function"""
    recovery = TargetedSyntaxRecovery()
    results = recovery.run_targeted_recovery()

    # Count successful fixes
    success_count = sum(1 for status in results.values() if status in ["fixed", "already_valid"])

    if success_count == len(results):
        print(" All syntax issues resolved! Ready for Phase 2 completion.")
    else:
        print(f" {len(results) - success_count} files still need manual attention.")

if __name__ == "__main__":
    main()
