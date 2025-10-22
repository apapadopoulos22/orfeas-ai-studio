#!/usr/bin/env python3
"""
Comprehensive Markdown Linting Fixer
Scans all markdown files and fixes common linting issues
"""

import os
import re
import sys
from pathlib import Path
from collections import defaultdict

class MarkdownLinter:
    def __init__(self, workspace_root):
        self.workspace_root = workspace_root
        self.issues_found = defaultdict(list)
        self.issues_fixed = defaultdict(list)
        self.files_processed = 0
        self.files_fixed = 0

    def find_all_markdown_files(self):
        """Find all markdown files in the workspace"""
        md_files = []
        for root, dirs, files in os.walk(self.workspace_root):
            # Skip common non-essential directories
            dirs[:] = [d for d in dirs if d not in ['.git', '__pycache__', '.pytest_cache', 'node_modules', '.conda']]

            for file in files:
                if file.endswith('.md'):
                    md_files.append(os.path.join(root, file))
        return md_files

    def fix_md040_code_blocks(self, content):
        """Fix MD040: Fenced code blocks must have language specified"""
        lines = content.split('\n')
        fixed_lines = []
        i = 0

        while i < len(lines):
            line = lines[i]

            # Check for opening fence
            if line.lstrip().startswith('```'):
                fence_indent = len(line) - len(line.lstrip())
                fence_content = line[fence_indent + 3:].strip()

                # If no language specified, add 'text'
                if not fence_content:
                    fixed_lines.append(line[:fence_indent] + '```text')
                    self.issues_fixed['MD040'].append(f"Line {i+1}: Added language 'text' to code block")
                else:
                    fixed_lines.append(line)
            else:
                fixed_lines.append(line)

            i += 1

        return '\n'.join(fixed_lines)

    def fix_md036_emphasis_as_heading(self, content):
        """Fix MD036: Emphasis should not be used as heading"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # Pattern: **HEADING TEXT:** on its own line (emphasis as heading)
            if re.match(r'^\*\*[A-Z][A-Za-z0-9\s\-]*:\*\*\s*$', line):
                # Convert to proper heading
                heading_text = line.replace('**', '').replace(':', '')
                fixed_lines.append(f"### {heading_text}")
                self.issues_fixed['MD036'].append(f"Line {i+1}: Converted emphasis to heading: {heading_text}")
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_md022_heading_spacing(self, content):
        """Fix MD022: Headings should be surrounded by blank lines"""
        lines = content.split('\n')
        fixed_lines = []
        in_code_block = False

        for i, line in enumerate(lines):
            # Track code blocks
            if line.lstrip().startswith('```'):
                in_code_block = not in_code_block

            # Skip if in code block
            if in_code_block:
                fixed_lines.append(line)
                continue

            # Check if this is a heading
            if re.match(r'^#+\s+', line):
                # Add blank line before heading if needed
                if fixed_lines and fixed_lines[-1].strip():
                    fixed_lines.append('')
                    self.issues_fixed['MD022'].append(f"Line {i+1}: Added blank line before heading")

                fixed_lines.append(line)

                # Add blank line after heading if next line exists and is not blank
                if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].lstrip().startswith('```'):
                    fixed_lines.append('')
                    self.issues_fixed['MD022'].append(f"Line {i+1}: Added blank line after heading")
            else:
                fixed_lines.append(line)

        return '\n'.join(fixed_lines)

    def fix_md031_fence_spacing(self, content):
        """Fix MD031: Fenced code blocks should be surrounded by blank lines"""
        lines = content.split('\n')
        fixed_lines = []

        for i, line in enumerate(lines):
            # Check for opening fence
            if line.lstrip().startswith('```') and not (i > 0 and lines[i-1].lstrip().startswith('```')):
                # Add blank line before fence if needed
                if fixed_lines and fixed_lines[-1].strip():
                    fixed_lines.append('')
                    self.issues_fixed['MD031'].append(f"Line {i+1}: Added blank line before fence")

            fixed_lines.append(line)

            # Check for closing fence
            if line.lstrip().startswith('```') and (i > 0 and lines[i-1].lstrip().startswith('```')):
                # Add blank line after fence if needed
                if i + 1 < len(lines) and lines[i + 1].strip() and not lines[i + 1].lstrip().startswith('```'):
                    fixed_lines.append('')
                    self.issues_fixed['MD031'].append(f"Line {i+1}: Added blank line after fence")

        return '\n'.join(fixed_lines)

    def fix_file(self, filepath):
        """Fix all issues in a markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return False

        original_content = content

        # Apply fixes in order
        content = self.fix_md040_code_blocks(content)
        content = self.fix_md036_emphasis_as_heading(content)
        content = self.fix_md022_heading_spacing(content)
        content = self.fix_md031_fence_spacing(content)

        # Write back if changes were made
        if content != original_content:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_fixed += 1
                return True
            except Exception as e:
                print(f"Error writing {filepath}: {e}")
                return False

        return False

    def scan_and_fix_all(self):
        """Scan and fix all markdown files"""
        md_files = self.find_all_markdown_files()

        print(f"Found {len(md_files)} markdown files")
        print("Scanning and fixing issues...\n")

        for i, filepath in enumerate(md_files, 1):
            if (i % 100) == 0:
                print(f"Progress: {i}/{len(md_files)} files processed...")

            self.files_processed += 1
            self.fix_file(filepath)

        return self.generate_report()

    def generate_report(self):
        """Generate a summary report"""
        report = []
        report.append("=" * 70)
        report.append("MARKDOWN LINTING FIX REPORT")
        report.append("=" * 70)
        report.append("")
        report.append(f"Files Processed: {self.files_processed}")
        report.append(f"Files Fixed: {self.files_fixed}")
        report.append("")
        report.append("Issues Fixed by Type:")
        report.append("-" * 70)

        total_issues = 0
        for issue_type in sorted(self.issues_fixed.keys()):
            count = len(self.issues_fixed[issue_type])
            total_issues += count
            report.append(f"  {issue_type}: {count} issues")

        report.append("")
        report.append(f"Total Issues Fixed: {total_issues}")
        report.append("=" * 70)

        return '\n'.join(report)

def main():
    workspace_root = r"c:\Users\johng\Documents\oscar"

    if not os.path.isdir(workspace_root):
        print(f"Workspace not found: {workspace_root}")
        sys.exit(1)

    linter = MarkdownLinter(workspace_root)
    report = linter.scan_and_fix_all()
    print(report)

    # Save report
    report_file = os.path.join(workspace_root, "MARKDOWN_FIX_COMPREHENSIVE_REPORT.txt")
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    main()
