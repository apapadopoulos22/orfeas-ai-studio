#!/usr/bin/env python3
"""
Enhanced Markdown Fixer - Targets remaining MD036 and MD040 issues
"""

import os
import re
from collections import defaultdict

class EnhancedMarkdownFixer:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.issues_fixed = defaultdict(int)

    def fix_md040_code_blocks(self, content):
        """Fix MD040: Add language tags to code blocks"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]
            stripped = line.lstrip()

            # Check for opening fence without language
            if stripped.startswith('```') and not stripped.startswith('````'):
                fence_indent = len(line) - len(stripped)
                after_fence = stripped[3:].strip()

                # If no language or only whitespace
                if not after_fence:
                    fixed_lines.append(line[:fence_indent] + '```bash')
                    self.issues_fixed['MD040'] += 1
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return '\n'.join(fixed_lines)

    def fix_md036_emphasis_heading(self, content):
        """Fix MD036: Convert emphasis to proper headings"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            stripped = line.strip()

            # Pattern 1: **BOLD TEXT** on its own line
            if stripped.startswith('**') and stripped.endswith('**') and len(stripped) > 4:
                # Check it's not part of a code block or list item
                if not (i > 0 and lines[i-1].lstrip().startswith('```')):
                    if not stripped.startswith('**-') and not stripped.startswith('**✅'):
                        # Extract the text
                        text = stripped[2:-2].strip()
                        # Skip if it's just emphasis without heading intent
                        if ':' in text or text.isupper() or len(text) > 20:
                            fixed_lines.append(f"### {text}")
                            self.issues_fixed['MD036'] += 1
                        else:
                            fixed_lines.append(line)
                    else:
                        fixed_lines.append(line)
                else:
                    fixed_lines.append(line)
            # Pattern 2: Emphasis with colon at end of line (heading marker)
            elif re.match(r'^\*\*[^*]+:\*\*\s*$', stripped):
                text = stripped[2:-3]  # Remove ** and :**
                fixed_lines.append(f"### {text}")
                self.issues_fixed['MD036'] += 1
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_file(self, filepath):
        """Fix all issues in a markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            return False

        original_content = content

        # Apply fixes
        content = self.fix_md040_code_blocks(content)
        content = self.fix_md036_emphasis_heading(content)

        # Write back if changes were made
        if content != original_content:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                return True
            except Exception as e:
                return False

        return False

    def fix_target_files(self, target_files):
        """Fix specific target files with issues"""
        fixed_count = 0

        for fname in target_files:
            filepath = os.path.join(self.workspace_root, fname)
            if os.path.exists(filepath):
                if self.fix_file(filepath):
                    fixed_count += 1
                    print(f"✅ Fixed: {fname}")
                else:
                    print(f"⏭️  Skipped: {fname} (no changes needed)")
            else:
                print(f"⚠️  Not found: {fname}")

        return fixed_count

def main():
    workspace_root = r"c:\Users\johng\Documents\oscar"

    # Target files with known issues
    target_files = [
        "COMPREHENSIVE_TEST_RESULTS.md",
        "DECISION_PHASE_4_OPTIONS.md",
        "DEPLOYMENT_COMPLETE.md",
        "DEPLOYMENT_READY.md",
        "FINAL_HTML_FIXES_REPORT.md",
        "FINAL_PROJECT_COMPLETION_VERIFICATION.md",
        "FINAL_REPORT_COMPLETE_PATH_FORWARD.md",
    ]

    print("Enhanced Markdown Fixer - Targeting Remaining Issues")
    print("=" * 70)
    print(f"Workspace: {workspace_root}")
    print(f"Target files: {len(target_files)}")
    print()

    fixer = EnhancedMarkdownFixer(workspace_root)
    fixed_count = fixer.fix_target_files(target_files)

    print()
    print("=" * 70)
    print(f"Files Fixed: {fixed_count}")
    print("Issues Fixed:")
    for issue_type, count in sorted(fixer.issues_fixed.items()):
        print(f"  {issue_type}: {count}")

    total_issues = sum(fixer.issues_fixed.values())
    print(f"Total Issues Fixed: {total_issues}")
    print("=" * 70)

if __name__ == "__main__":
    main()
