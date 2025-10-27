#!/usr/bin/env python3
"""
Comprehensive HTML/CSS validation for inline styles conversion issues.
Checks for:
1. Malformed CSS class names with template variables
2. Incomplete template variables in HTML attributes
3. Missing/broken onclick handlers
4. Broken template literals in JavaScript
5. Invalid CSS selectors
"""

import os
import re
from pathlib import Path
from collections import defaultdict

def validate_html_file(filepath):
    """Validate HTML file for conversion issues."""
    issues = []
    warnings = []

    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            lines = content.split('\n')

        # Check 1: Malformed CSS class definitions
        for line_num, line in enumerate(lines, 1):
            # Look for .classname{ patterns with incomplete template vars
            if re.search(r'\.[\w-]*\$\{[^}]*$', line):  # Unclosed template var
                issues.append(('CRITICAL', line_num, 'Unclosed template variable in CSS selector', line.strip()[:80]))

            # Look for invalid class names with template vars that should be complete
            if re.search(r'class="[^"]*\$\{progre[^}]*"', line):  # The specific bug we fixed
                issues.append(('CRITICAL', line_num, 'Incomplete template variable in class attribute', line.strip()[:80]))

        # Check 2: Broken onclick handlers
        onclick_pattern = r'onclick="showSection\([\'"]?([^\'")]*)[\'"]?\)'
        for line_num, line in enumerate(lines, 1):
            if 'onclick=' in line and 'showSection' in line:
                match = re.search(onclick_pattern, line)
                if match:
                    section_id = match.group(1)
                    # Verify the section exists in the document
                    if f'id="{section_id}"' not in content and f"id='{section_id}'" not in content:
                        warnings.append(('WARNING', line_num, f'Section "{section_id}" not found in document', ''))

        # Check 3: Broken template literals in JavaScript
        js_pattern = r'\$\{[^}]*\}%"'  # Template var followed by % in a string
        for line_num, line in enumerate(lines, 1):
            if '<script' in line or re.search(r'style="\s*[^"]*\$\{', line):
                if re.search(js_pattern, line):
                    issues.append(('CRITICAL', line_num, 'Potential broken template in inline style', line.strip()[:80]))

        # Check 4: Verify showSection function exists if used
        if 'showSection(' in content:
            if 'function showSection' not in content:
                issues.append(('CRITICAL', 0, 'showSection function called but not defined', ''))

        # Check 5: CSS syntax - look for rules with missing closing braces
        in_style = False
        brace_count = 0
        style_line_start = 0
        for line_num, line in enumerate(lines, 1):
            if '<style' in line:
                in_style = True
                style_line_start = line_num
            if '</style>' in line:
                in_style = False

            if in_style:
                brace_count += line.count('{') - line.count('}')
                if brace_count < 0:
                    issues.append(('WARNING', line_num, 'Mismatched CSS braces (more closing than opening)', line.strip()[:80]))
                    brace_count = 0

    except Exception as e:
        issues.append(('ERROR', 0, f'File read error: {str(e)}', ''))

    return issues, warnings

def main():
    """Validate all HTML files in the project."""
    project_root = Path(r'c:\Users\johng\Documents\oscar')

    # Focus on production HTML files (not generated or third-party)
    production_files = [
        'orfeas-ai-studio.html',
        'synexa-style-studio.html',
        'orfeas-studio.html',
        'material-studio.html',
        'batch-studio.html',
        'camera-studio.html',
        'bob-ai-chat.html',
    ]

    all_issues = defaultdict(list)
    all_warnings = defaultdict(list)
    total_issues = 0
    total_warnings = 0

    print("=" * 70)
    print("HTML/CSS VALIDATION REPORT")
    print("=" * 70)
    print(f"\nValidating {len(production_files)} production HTML files...\n")

    for filename in production_files:
        filepath = project_root / filename
        if not filepath.exists():
            print(f"⚠️  {filename} - NOT FOUND")
            continue

        issues, warnings = validate_html_file(filepath)

        if issues or warnings:
            all_issues[filename] = issues
            all_warnings[filename] = warnings
            total_issues += len(issues)
            total_warnings += len(warnings)

            status = "🔴" if issues else "🟡"
            print(f"{status} {filename} - {len(issues)} issues, {len(warnings)} warnings")
        else:
            print(f"✅ {filename} - OK")

    # Print detailed report
    if total_issues > 0 or total_warnings > 0:
        print("\n" + "=" * 70)
        print("DETAILED ISSUES")
        print("=" * 70)

        for filename in sorted(all_issues.keys()):
            issues = all_issues[filename]
            if issues:
                print(f"\n📄 {filename}")
                for severity, line_num, message, content in issues:
                    print(f"  [{severity}] Line {line_num}: {message}")
                    if content:
                        print(f"      {content}")

        print("\n" + "=" * 70)
        print("WARNINGS")
        print("=" * 70)

        for filename in sorted(all_warnings.keys()):
            warnings = all_warnings[filename]
            if warnings:
                print(f"\n📄 {filename}")
                for severity, line_num, message, content in warnings:
                    print(f"  [{severity}] Line {line_num}: {message}")
                    if content:
                        print(f"      {content}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Total Issues: {total_issues}")
    print(f"Total Warnings: {total_warnings}")
    print(f"Files Validated: {len(production_files)}")
    print(f"Files with Issues: {len(all_issues)}")

    if total_issues == 0 and total_warnings == 0:
        print("\n✅ All files are valid!")
    else:
        print("\n⚠️  Review issues above and apply fixes as needed.")

if __name__ == '__main__':
    main()
