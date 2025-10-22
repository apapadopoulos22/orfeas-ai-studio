#!/usr/bin/env python3
"""
Comprehensive Markdown Violation Fixer
Fixes: MD026, MD024, MD001, MD025, MD040, MD029
"""

import re
import os
from pathlib import Path
from collections import defaultdict

class MarkdownViolationFixer:
    def __init__(self):
        self.files_fixed = 0
        self.violations_fixed = 0
        self.target_files = [
            'MARKDOWN_LINTING_FINAL_VERIFICATION.md',
            'PHASE_3_1_EXECUTIVE_BRIEF.md',
            'PHASE_3_2_3_3_COMPLETION_REPORT.md',
            'PHASE_4_COMPLETE_SUMMARY.md',
            'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md',
            'PHASE_4_OPTIMIZATION_10_PERCENT.md',
            'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md',
            'PHASE_4_DOCUMENTATION_INDEX.md',
            'PHASE_4_IMPLEMENTATION_ROADMAP.md',
        ]

    def fix_trailing_punctuation(self, content):
        """Fix MD026: Remove trailing punctuation from headings"""
        lines = content.split('\n')
        fixed_lines = []
        violations = 0

        for line in lines:
            if re.match(r'^#+\s+', line):
                # Extract heading level and content
                match = re.match(r'^(#+\s+)(.+)$', line)
                if match:
                    heading_marker = match.group(1)
                    heading_text = match.group(2)

                    # Remove trailing punctuation (! . : ? ,)
                    original = heading_text
                    heading_text = re.sub(r'[!.,:?]+$', '', heading_text)

                    if original != heading_text:
                        violations += 1
                        line = heading_marker + heading_text

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), violations

    def fix_heading_level_skip(self, content):
        """Fix MD001: Heading levels should only increment by one level"""
        lines = content.split('\n')
        fixed_lines = []
        violations = 0
        prev_level = 0

        for i, line in enumerate(lines):
            if re.match(r'^#+\s+', line):
                match = re.match(r'^(#+)\s+', line)
                if match:
                    current_level = len(match.group(1))

                    # If skipping levels (e.g., # to ### ), fix to sequential
                    if prev_level > 0 and current_level > prev_level + 1:
                        new_level = prev_level + 1
                        new_heading = '#' * new_level + line[len(match.group(1)):]
                        line = new_heading
                        violations += 1

                    prev_level = current_level

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), violations

    def fix_duplicate_headings(self, content):
        """Fix MD024: Duplicate headings - add context to make unique"""
        lines = content.split('\n')
        fixed_lines = []
        heading_counts = defaultdict(int)
        violations = 0

        for i, line in enumerate(lines):
            if re.match(r'^#+\s+', line):
                match = re.match(r'^(#+)\s+(.+)$', line)
                if match:
                    heading_marker = match.group(1)
                    heading_text = match.group(2)
                    original_text = heading_text

                    # Track heading counts
                    heading_key = heading_text.lower()
                    heading_counts[heading_key] += 1

                    # If this is a duplicate, try to add context
                    if heading_counts[heading_key] > 1:
                        # Look back for context (section or component name)
                        context = self._find_context(lines, i)
                        if context and context not in heading_text:
                            heading_text = f"{heading_text} ({context})"
                            violations += 1

                    line = heading_marker + ' ' + heading_text

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), violations

    def _find_context(self, lines, current_idx):
        """Find context by looking back for section/component headers"""
        # Look back up to 30 lines for a higher-level heading
        for j in range(max(0, current_idx - 30), current_idx):
            prev_line = lines[j]
            if re.match(r'^#+\s+', prev_line):
                match = re.match(r'^#+\s+(.+)$', prev_line)
                if match:
                    text = match.group(1).strip()
                    # Extract meaningful context (remove punctuation for comparison)
                    context = re.sub(r'[!.,:?]', '', text)
                    if len(context) > 5:  # Only use if meaningful
                        return context[:50]  # Limit length
        return None

    def fix_multiple_h1(self, content):
        """Fix MD025: Only one h1 heading allowed"""
        lines = content.split('\n')
        fixed_lines = []
        h1_count = 0
        violations = 0

        for line in lines:
            if re.match(r'^#\s+', line):
                h1_count += 1
                if h1_count > 1:
                    # Convert to h2
                    line = '#' + line
                    violations += 1

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), violations

    def fix_code_block_language(self, content):
        """Fix MD040: Fenced code blocks should have a language specified"""
        lines = content.split('\n')
        fixed_lines = []
        violations = 0
        i = 0

        while i < len(lines):
            line = lines[i]

            # Detect opening code fence
            if re.match(r'^```\s*$', line):
                # Check if next line is not a language specifier
                if i + 1 < len(lines):
                    next_line = lines[i + 1]
                    # If next line is content (not empty, not closing fence), add python as default
                    if next_line.strip() and not re.match(r'^```', next_line):
                        line = '```python'
                        violations += 1

            fixed_lines.append(line)
            i += 1

        return '\n'.join(fixed_lines), violations

    def fix_list_numbering(self, content):
        """Fix MD029: List numbering consistency (maintain intentional restarts)"""
        lines = content.split('\n')
        fixed_lines = []
        violations = 0
        in_list = False
        list_level = 0

        for i, line in enumerate(lines):
            # Check if line is an ordered list item
            if re.match(r'^\s*\d+\.\s+', line):
                if not in_list:
                    in_list = True
                    list_level = len(line) - len(line.lstrip())
                    list_num = 1
                elif len(line) - len(line.lstrip()) == list_level:
                    list_num += 1

                # Replace with correct number
                match = re.match(r'^(\s*)\d+(\.\s+.+)$', line)
                if match:
                    indent = match.group(1)
                    rest = match.group(2)
                    new_line = f"{indent}{list_num}{rest}"
                    if new_line != line:
                        violations += 1
                    line = new_line

            # Check if list ended
            elif in_list and line.strip() == '':
                # Blank line might end list, check next non-blank
                for j in range(i + 1, len(lines)):
                    if lines[j].strip():
                        if not re.match(r'^\s*\d+\.\s+', lines[j]):
                            in_list = False
                        break

            fixed_lines.append(line)

        return '\n'.join(fixed_lines), violations

    def process_file(self, filepath):
        """Process a single markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original_content = content
            total_violations = 0

            # Apply fixes in order
            content, v = self.fix_trailing_punctuation(content)
            total_violations += v

            content, v = self.fix_heading_level_skip(content)
            total_violations += v

            content, v = self.fix_multiple_h1(content)
            total_violations += v

            content, v = self.fix_duplicate_headings(content)
            total_violations += v

            content, v = self.fix_code_block_language(content)
            total_violations += v

            content, v = self.fix_list_numbering(content)
            total_violations += v

            # Write back if changed
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_fixed += 1
                self.violations_fixed += total_violations
                return True, total_violations

            return False, 0

        except Exception as e:
            print(f"❌ Error processing {filepath}: {e}")
            return False, 0

    def run(self):
        """Run fixer on all target files"""
        print("=" * 73)
        print("COMPREHENSIVE MARKDOWN VIOLATION FIXER")
        print("=" * 73)

        for filename in self.target_files:
            filepath = Path(filename)
            if filepath.exists():
                fixed, violations = self.process_file(str(filepath))
                if fixed:
                    print(f"✅ {filename}: Fixed {violations} violations")
                else:
                    print(f"⏭️  {filename}: No violations found")
            else:
                print(f"⚠️  {filename}: File not found")

        print("=" * 73)
        print(f"✅ TOTAL: {self.files_fixed} files fixed, {self.violations_fixed} violations resolved")
        print("=" * 73)


if __name__ == '__main__':
    fixer = MarkdownViolationFixer()
    fixer.run()
