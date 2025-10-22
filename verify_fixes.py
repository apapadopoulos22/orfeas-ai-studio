import re

file_path = 'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md'

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Scanning PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md for duplicate headings:")
print()

# Track headings
headings = {}
for i, line in enumerate(lines, 1):
    if line.startswith('###'):
        heading = line.strip()
        if heading not in headings:
            headings[heading] = []
        headings[heading].append(i)

# Find duplicates
duplicates = {h: line_nums for h, line_nums in headings.items() if len(line_nums) > 1}

if duplicates:
    print(f"Found {len(duplicates)} duplicate heading types:")
    for heading, line_nums in sorted(duplicates.items()):
        print(f"{heading}")
        print(f"  Lines: {line_nums}")
        print()
else:
    print("✅ No duplicate ### headings found")

# Also check PHASE_3_2_3_3 and PHASE_3_1
print("\n" + "="*60)
print("Checking other files...")
print("="*60)

for fname in ['PHASE_3_2_3_3_INTEGRATION_EXECUTION_PLAN.md', 'PHASE_3_1_EXECUTIVE_BRIEF.md']:
    print(f"\n{fname}:")
    try:
        with open(fname, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for MD026 (trailing colons)
        matches = list(re.finditer(r'^(#{1,6}\s+[^:\r\n]+):\s*$', content, re.MULTILINE))
        if matches:
            print(f"  ⚠️  {len(matches)} trailing colons in headings")
            for match in matches[:3]:
                print(f"    {match.group(0)[:50]}")
        else:
            print(f"  ✅ No trailing colons in headings")
    except:
        pass
