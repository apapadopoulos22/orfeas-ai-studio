#!/usr/bin/env python
"""Fix all real markdown violations."""
import re
import os

def fix_duplicate_headings(filepath):
    """Fix MD024 duplicate headings by adding context."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    headings_seen = {}
    fixes = 0

    for i, line in enumerate(lines):
        if line.startswith('#'):
            heading = line.strip()

            if heading in headings_seen:
                # This is a duplicate - add section context
                # Try to find context from nearby ### lines
                context = None
                for j in range(i-1, max(0, i-20), -1):
                    if lines[j].startswith('####'):
                        context = lines[j].strip()[5:].split('✅')[0].strip()
                        break
                    elif lines[j].startswith('###'):
                        context = lines[j].strip()[4:].split('✅')[0].strip()
                        break

                if context:
                    # Extract the heading level and content
                    match = re.match(r'^(#{1,6})\s+(.+)$', heading)
                    if match:
                        level, content = match.groups()
                        new_heading = f"{level} {content} ({context})\n"
                        lines[i] = new_heading
                        fixes += 1

            headings_seen[heading] = i

    if fixes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    return fixes

def fix_list_numbering(filepath):
    """Fix MD029 list numbering issues."""
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    fixes = 0
    i = 0

    while i < len(lines):
        line = lines[i]

        # Check if this starts a numbered list
        if re.match(r'^\d+\.\s', line):
            # Find all consecutive list items
            list_start = i
            list_items = []
            j = i

            while j < len(lines) and (re.match(r'^\s*\d+\.\s', lines[j]) or lines[j].strip() == ''):
                if lines[j].strip() != '':
                    list_items.append(j)
                j += 1

            # Renumber them
            if len(list_items) > 1:
                for idx, item_line_num in enumerate(list_items, 1):
                    old_line = lines[item_line_num]
                    # Replace the number with the correct one
                    new_line = re.sub(r'^\s*\d+\.', f'{idx}.', old_line)
                    if new_line != old_line:
                        lines[item_line_num] = new_line
                        fixes += 1

            i = j
        else:
            i += 1

    if fixes > 0:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(lines)

    return fixes

# Process files
files = [
    'PHASE_3_2_3_3_COMPLETION_REPORT.md',
    'PHASE_3_1_EXECUTIVE_BRIEF.md',
    'MARKDOWN_LINTING_FINAL_VERIFICATION.md',
    'PHASE_4_COMPLETE_SUMMARY.md',
    'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md',
    'PHASE_4_OPTIMIZATION_10_PERCENT.md',
    'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md'
]

print("Fixing Markdown Violations")
print("="*70)

total_fixes = 0

for filepath in files:
    if not os.path.exists(filepath):
        continue

    dup_fixes = fix_duplicate_headings(filepath)
    list_fixes = fix_list_numbering(filepath)

    total = dup_fixes + list_fixes
    if total > 0:
        print(f"✅ {filepath}: Fixed {dup_fixes} duplicate headings, {list_fixes} list numbering issues")
        total_fixes += total

print("="*70)
print(f"✅ TOTAL VIOLATIONS FIXED: {total_fixes}")
