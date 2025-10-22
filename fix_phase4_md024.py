#!/usr/bin/env python
"""Fix MD024 duplicate headings by adding component context."""
import re

file_path = 'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []

# Track current component number
component_num = None
component_name = None
seen_headings_in_component = {}

for i, line in enumerate(lines):
    # Detect component markers (#### N. Name ✅)
    if re.match(r'^#### \d+\. .+\s✅', line):
        match = re.match(r'^#### (\d+)\. (.+?)\s✅', line)
        if match:
            component_num = match.group(1)
            component_name = match.group(2).strip()
            seen_headings_in_component = {}
            new_lines.append(line)
            continue

    # Fix duplicate ### headings by adding component context
    if line.startswith('### ') and component_num:
        heading_text = line[4:].strip()

        if heading_text in seen_headings_in_component:
            # Duplicate - make unique
            new_line = f"### {heading_text} ({component_name})"
            new_lines.append(new_line)
            print(f"Line {i+1}: Fixed duplicate heading in component {component_num}")
            print(f"  From: {line}")
            print(f"  To:   {new_line}")
        else:
            seen_headings_in_component[heading_text] = True
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write fixed content
new_content = '\n'.join(new_lines)
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(new_content)

print("\n✅ All duplicate headings fixed!")
