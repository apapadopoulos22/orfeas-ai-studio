#!/usr/bin/env python
"""Fix duplicate headings by adding context/component identifiers."""
import re

file_path = 'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track sections and their components
current_component = None
heading_counts = {}
fixes_made = []

new_lines = []
for i, line in enumerate(lines):
    # Track current component (#### X. ComponentName)
    if line.startswith('#### '):
        # Extract component name
        match = re.search(r'####\s+\d+\.\s+([^✅]+)', line)
        if match:
            current_component = match.group(1).strip()

    # Fix duplicate headings
    if line.startswith('### ') and current_component:
        heading_key = (line.strip(), current_component)

        if heading_key in heading_counts:
            heading_counts[heading_key] += 1
            # Add component identifier
            original_heading = line.rstrip()
            new_heading = f"{original_heading} - {current_component}\n"
            new_lines.append(new_heading)
            fixes_made.append(f"Line {i+1}: Made '{line.strip()[:40]}' unique by adding context")
        else:
            heading_counts[heading_key] = 1
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write fixed content
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"✅ Fixed {len(fixes_made)} duplicate headings in PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md")
for fix in fixes_made[:10]:  # Show first 10
    print(f"  {fix}")
if len(fixes_made) > 10:
    print(f"  ... and {len(fixes_made) - 10} more")
