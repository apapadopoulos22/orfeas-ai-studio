#!/usr/bin/env python3
"""
Scan HTML files for CSS syntax errors, specifically malformed class names
containing template variables or incomplete expressions.
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def scan_html_file(filepath):
    """Scan a single HTML file for CSS syntax issues."""
    issues = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        # Check for CSS class definitions with template variables
        # Pattern: .classname { where classname contains ${
        malformed_pattern = r'\.([a-zA-Z0-9_-]*\$\{[^}]*)\s*\{'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(malformed_pattern, line)
            for match in matches:
                issues.append({
                    'file': filepath,
                    'line': line_num,
                    'type': 'malformed_css_class',
                    'content': line.strip(),
                    'class_name': f".{match.group(1)}"
                })

        # Check for class attributes with template variables (should use inline style instead)
        # Pattern: class="...${...}..."
        class_template_pattern = r'class="[^"]*\$\{[^}]*\}[^"]*"'

        for line_num, line in enumerate(lines, 1):
            matches = re.finditer(class_template_pattern, line)
            for match in matches:
                issues.append({
                    'file': filepath,
                    'line': line_num,
                    'type': 'template_in_class_attribute',
                    'content': line.strip(),
                    'class_attr': match.group(0)
                })

        # Check for incomplete CSS rules (opening brace but no closing)
        in_style_tag = False
        style_start = 0
        for line_num, line in enumerate(lines, 1):
            if '<style' in line:
                in_style_tag = True
                style_start = line_num
            if '</style>' in line:
                in_style_tag = False

            if in_style_tag and '{' in line and '}' not in line:
                # Check if it's a valid selector
                # Invalid if has incomplete template variable
                if re.search(r'\$\{[^}]*$', line):
                    issues.append({
                        'file': filepath,
                        'line': line_num,
                        'type': 'unclosed_template_in_selector',
                        'content': line.strip()
                    })

    except Exception as e:
        issues.append({
            'file': filepath,
            'line': 0,
            'type': 'scan_error',
            'error': str(e)
        })

    return issues

def main():
    """Scan all HTML files in the project."""
    project_root = Path(r'c:\Users\johng\Documents\oscar')
    html_files = list(project_root.glob('**/*.html'))

    all_issues = defaultdict(list)
    total_issues = 0

    print(f"Scanning {len(html_files)} HTML files for CSS syntax issues...\n")

    for html_file in sorted(html_files):
        # Skip node_modules, htmlcov, and docs
        if any(x in str(html_file) for x in ['node_modules', 'htmlcov', 'docs']):
            continue

        issues = scan_html_file(html_file)
        if issues:
            all_issues[str(html_file)] = issues
            total_issues += len(issues)

    if total_issues == 0:
        print("✅ No CSS syntax issues found!")
        return

    print(f"⚠️  Found {total_issues} potential CSS syntax issues:\n")

    for filepath, issues in sorted(all_issues.items()):
        print(f"\n📄 {filepath}")
        for issue in issues:
            print(f"  Line {issue['line']}: {issue['type']}")
            print(f"    {issue['content'][:100]}")
            if 'class_name' in issue:
                print(f"    Class: {issue['class_name']}")
            if 'error' in issue:
                print(f"    Error: {issue['error']}")

    print(f"\n\nSummary: {total_issues} issues found")
    print("\nIssue Types:")
    issue_types = defaultdict(int)
    for issues in all_issues.values():
        for issue in issues:
            issue_types[issue['type']] += 1

    for issue_type, count in sorted(issue_types.items()):
        print(f"  - {issue_type}: {count}")

if __name__ == '__main__':
    main()
