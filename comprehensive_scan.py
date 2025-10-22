#!/usr/bin/env python
"""Comprehensive scan of all files mentioned in error attachment."""
import re
import os

files_to_scan = [
    'PHASE_3_2_3_3_COMPLETION_REPORT.md',
    'PHASE_3_1_EXECUTIVE_BRIEF.md',
    'MARKDOWN_LINTING_FINAL_VERIFICATION.md',
    'PHASE_4_COMPLETE_SUMMARY.md',
    'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md',
    'PHASE_4_OPTIMIZATION_10_PERCENT.md',
    'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md'
]

print("COMPREHENSIVE VIOLATION SCAN")
print("="*70)

total_violations = 0

for filepath in files_to_scan:
    if not os.path.exists(filepath):
        print(f"\n❌ {filepath}: FILE NOT FOUND")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')
    violations = []

    # Check for MD026 (trailing punctuation in headings)
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            # Check for trailing colons/punctuation
            if re.search(r'[!:?.]\\s*$', line):
                violations.append((i, 'MD026', f"Trailing punctuation: {line[:50]}"))

    # Check for MD001 (heading increment)
    for i, line in enumerate(lines):
        if line.startswith('###') and not line.startswith('####'):
            # Check if ### comes before ##
            has_h2_before = any(l.startswith('##') and not l.startswith('###') for l in lines[:i])
            if not has_h2_before:
                violations.append((i+1, 'MD001', f"Heading increment violation: {line[:50]}"))

    # Check for MD024 (duplicate headings)
    headings = {}
    for i, line in enumerate(lines, 1):
        if line.startswith('#'):
            if line in headings:
                violations.append((i, 'MD024', f"Duplicate heading: {line[:50]}"))
            else:
                headings[line] = i

    # Check for MD025 (multiple h1)
    h1_count = sum(1 for line in lines if line.startswith('# ') and not line.startswith('##'))
    if h1_count > 1:
        violations.append((0, 'MD025', f"Multiple h1 headings: {h1_count}"))

    # Check for MD029 (list numbering)
    list_nums = []
    for i, line in enumerate(lines, 1):
        if re.match(r'^\s*\d+\.\s', line):
            match = re.match(r'^\s*(\d+)\.', line)
            if match:
                list_nums.append((i, int(match.group(1))))

    # Check list numbering consistency
    for i in range(len(list_nums) - 1):
        curr_line, curr_num = list_nums[i]
        next_line, next_num = list_nums[i + 1]
        if next_num != curr_num + 1:
            violations.append((next_line, 'MD029', f"List numbering: expected {curr_num + 1}, got {next_num}"))

    # Check for MD040 (code block language)
    for i, line in enumerate(lines, 1):
        if line.strip().startswith('```') and not any(lang in line for lang in ['python', 'bash', 'text', 'markdown', 'javascript', 'json', 'yaml', 'html', 'sql', '```']):
            if line.strip() == '```':
                violations.append((i, 'MD040', "Code block without language"))

    if violations:
        print(f"\n⚠️  {filepath}: {len(violations)} violations")
        for line_num, rule, msg in violations[:10]:
            print(f"    Line {line_num}: {rule} - {msg}")
        if len(violations) > 10:
            print(f"    ... and {len(violations) - 10} more")
        total_violations += len(violations)
    else:
        print(f"\n✅ {filepath}: CLEAN")

print("\n" + "="*70)
print(f"TOTAL VIOLATIONS FOUND: {total_violations}")

if total_violations == 0:
    print("\n✅ ALL FILES ARE NOW COMPLIANT!")
