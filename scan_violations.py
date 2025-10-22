#!/usr/bin/env python
import os
import re
import glob

violations_found = {}

# Search all markdown files
for md_file in glob.glob('*.md'):
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find trailing colons in headings
        matches = re.finditer(r'^(#{1,6}\s+[^:\r\n]+):\s*$', content, re.MULTILINE)

        if matches:
            lines = content.split('\n')
            file_violations = []

            for match in re.finditer(r'^(#{1,6}\s+[^:\r\n]+):\s*$', content, re.MULTILINE):
                # Find line number
                line_num = content[:match.start()].count('\n') + 1
                preview = match.group(0)[:60]
                file_violations.append((line_num, preview))

            if file_violations:
                violations_found[md_file] = file_violations
    except Exception as e:
        pass

if violations_found:
    print("⚠️  Found violations:")
    for file, violations in violations_found.items():
        print(f"\n{file}: {len(violations)} violations")
        for line_num, preview in violations:
            print(f"    Line {line_num}: {preview}")
else:
    print("✅ No trailing colons found in headings")

# Also check for duplicate headings
print("\n" + "="*60)
print("Checking for MD024 violations (duplicate headings)...")
print("="*60 + "\n")

dup_check = {}
for md_file in glob.glob('*.md'):
    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        headings = {}
        duplicates = []

        for i, line in enumerate(lines, 1):
            if line.startswith('#'):
                heading = line.strip()
                if heading in headings:
                    duplicates.append((heading, headings[heading], i))
                else:
                    headings[heading] = i

        if duplicates:
            dup_check[md_file] = duplicates
    except Exception as e:
        pass

if dup_check:
    print("⚠️  Found duplicate headings:")
    for file, dups in dup_check.items():
        print(f"\n{file}: {len(dups)} duplicate(s)")
        for heading, first_line, second_line in dups:
            print(f"    Lines {first_line} & {second_line}: {heading[:50]}")
else:
    print("✅ No duplicate headings found")
