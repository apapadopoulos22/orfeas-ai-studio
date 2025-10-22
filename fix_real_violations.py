#!/usr/bin/env python
"""Scan and fix real markdown violations."""
import re
import os

def fix_file(filepath):
    """Fix violations in a markdown file."""
    if not os.path.exists(filepath):
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixes = 0

    for i, line in enumerate(lines):
        original = line

        # MD026: Remove trailing punctuation from headings
        if line.startswith('#') and re.search(r'[!:?.]\\s*$', line):
            line = re.sub(r'([^!:?.])\s*[!:?.]\\s*$', r'\1\n', line)
            if line != original:
                fixes += 1
                lines[i] = line
                print(f"  Line {i+1}: Fixed MD026 trailing punctuation")

        # MD001: Fix heading increment (### to ## if no previous ##)
        if line.startswith('###') and not line.startswith('####'):
            # Check if there's a ## before it
            has_h2 = any(l.startswith('##') for l in lines[:i])
            if not has_h2:
                new_line = '##' + line[2:]
                if new_line != original:
                    fixes += 1
                    lines[i] = new_line
                    print(f"  Line {i+1}: Fixed MD001 heading increment")

    if fixes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    return fixes

# Files with violations
files = [
    'PHASE_3_2_3_3_COMPLETION_REPORT.md',
    'PHASE_3_1_EXECUTIVE_BRIEF.md',
    'MARKDOWN_LINTING_FINAL_VERIFICATION.md',
    'PHASE_4_COMPLETE_SUMMARY.md',
    'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md',
    'PHASE_4_OPTIMIZATION_10_PERCENT.md',
    'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md'
]

total = 0
for f in files:
    if os.path.exists(f):
        fixes = fix_file(f)
        if fixes > 0:
            print(f"✅ {f}: Fixed {fixes} violations\n")
            total += fixes

print(f"\n✅ TOTAL VIOLATIONS FIXED: {total}")
