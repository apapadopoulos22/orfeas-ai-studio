#!/usr/bin/env python
"""Fix MD024 (duplicate headings) by adding component identifiers."""
import re

file_path = 'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
current_component = None
current_tier = None
fixes = []

for i, line in enumerate(lines):
    # Track tier
    if re.match(r'^### ✅ Tier \d+:', line):
        current_tier = line.strip()
        new_lines.append(line)
        continue

    # Track component (#### N. Name ✅)
    if re.match(r'^#### \d+\. .+\s✅', line):
        match = re.match(r'^#### (\d+)\. (.+?)\s✅', line)
        if match:
            current_component = match.group(2).strip()
        new_lines.append(line)
        continue

    # Rename duplicate headings by adding component context
    if line.startswith('### ') and current_component and line.strip() in ['### Features', '### Key Methods', '### Methods', '### Test Scenarios']:
        # Check if this is a duplicate
        heading = line.strip()

        # Only rename if it's one of the known duplicates
        if heading == '### Features':
            new_line = f"### Features ({current_component})\n"
            new_lines.append(new_line)
            fixes.append((i+1, heading, new_line.strip()))
        elif heading == '### Key Methods':
            new_line = f"### Key Methods ({current_component})\n"
            new_lines.append(new_line)
            fixes.append((i+1, heading, new_line.strip()))
        elif heading == '### Methods':
            new_line = f"### Methods ({current_component})\n"
            new_lines.append(new_line)
            fixes.append((i+1, heading, new_line.strip()))
        else:
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write fixed content
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

# Report
print(f"✅ Fixed {len(fixes)} duplicate headings")
for line_num, old, new in fixes[:15]:
    print(f"  Line {line_num}: {old} → {new}")

if len(fixes) > 15:
    print(f"  ... and {len(fixes) - 15} more")
