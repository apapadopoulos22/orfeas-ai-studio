#!/usr/bin/env python3
"""
Final Markdown Verification - Check all files for markdownlint compliance
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Tuple

def check_file_compliance(file_path: str) -> Tuple[bool, List[str]]:
    """Check if a markdown file is compliant with markdownlint rules."""
    issues = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except Exception as e:
        return False, [f"Error reading file: {str(e)}"]

    # Check for trailing colons in headings (MD026)
    for i, line in enumerate(lines, 1):
        if re.match(r'^#{1,6}\s+.+:\s*$', line.rstrip()):
            issues.append(f"Line {i}: MD026 - Trailing punctuation in heading")

    # Check for multiple h1 headings (MD025)
    h1_count = sum(1 for line in lines if re.match(r'^#\s+', line))
    if h1_count > 1:
        for i, line in enumerate(lines, 1):
            if re.match(r'^#\s+', line):
                issues.append(f"Line {i}: MD025 - Multiple h1 headings (total: {h1_count})")

    # Check for duplicate headings (MD024)
    heading_dict = {}
    for i, line in enumerate(lines, 1):
        if re.match(r'^#{1,6}\s+', line):
            heading_text = re.sub(r'^#+\s+', '', line).strip()
            level = len(re.match(r'^#+', line).group())
            key = (level, heading_text)
            if key in heading_dict:
                issues.append(f"Line {i}: MD024 - Duplicate heading '{heading_text}' (also at line {heading_dict[key]})")
            else:
                heading_dict[key] = i

    return len(issues) == 0, issues

def main():
    """Run verification on all markdown files."""
    root_dir = Path('c:\\Users\\johng\\Documents\\oscar')
    md_files = list(root_dir.glob('**/*.md'))

    total_files = len(md_files)
    compliant_files = 0
    total_issues = 0
    problem_files = []

    print(f"[*] Scanning {total_files} markdown files for compliance...")

    for md_file in sorted(md_files):
        is_compliant, issues = check_file_compliance(str(md_file))

        if is_compliant:
            compliant_files += 1
        else:
            total_issues += len(issues)
            problem_files.append((str(md_file), issues))

    print(f"\n[+] VERIFICATION RESULTS:")
    print(f"    Total Files: {total_files}")
    print(f"    Compliant: {compliant_files}/{total_files}")
    print(f"    Compliance Rate: {(compliant_files/total_files)*100:.2f}%")
    print(f"    Total Issues Found: {total_issues}")

    if problem_files:
        print(f"\n[!] PROBLEM FILES ({len(problem_files)}):")
        for file_path, issues in sorted(problem_files):
            short_path = file_path.replace('c:\\Users\\johng\\Documents\\oscar\\', '')
            print(f"\n    {short_path}")
            for issue in issues[:5]:  # Show first 5 issues per file
                print(f"      - {issue}")
            if len(issues) > 5:
                print(f"      - ... and {len(issues) - 5} more issues")
    else:
        print("\n[SUCCESS] All markdown files are compliant!")

if __name__ == '__main__':
    main()
