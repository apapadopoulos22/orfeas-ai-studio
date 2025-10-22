import re

# Read the file
with open('PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track fixes
fixes = 0
original_lines = lines.copy()

# Fix trailing colons in headings
for i, line in enumerate(lines):
    if line.startswith('#') and ':' in line:
        # Remove trailing colon from headings
        new_line = re.sub(r'(#{1,6}\s+.+?):\s*$', r'\1\n', line)
        if new_line != line:
            print(f"Line {i+1}: Fixed trailing colon")
            print(f"  Before: {line.rstrip()[:70]}")
            print(f"  After:  {new_line.rstrip()[:70]}")
            lines[i] = new_line
            fixes += 1

# Handle duplicate headings by adding phase/section identifiers
heading_counts = {}
for i, line in enumerate(lines):
    if line.startswith('#### ') and ':' in line:
        # Extract heading text
        heading_text = line.split(':')[0].strip()

        # Count occurrences
        if heading_text not in heading_counts:
            heading_counts[heading_text] = 0
        else:
            heading_counts[heading_text] += 1
            # Make unique by adding phase identifier
            count = heading_counts[heading_text]
            new_line = f"{heading_text} (Phase {count})\n"
            print(f"Line {i+1}: Fixed duplicate heading")
            print(f"  Before: {line.rstrip()[:70]}")
            print(f"  After:  {new_line.rstrip()[:70]}")
            lines[i] = new_line
            fixes += 1

        heading_counts[heading_text] = heading_counts.get(heading_text, 0) + 1

print(f"\n✅ Total fixes: {fixes}")

# Write back
with open('PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md', 'w', encoding='utf-8') as f:
    f.writelines(lines)

print("✅ File updated successfully!")
