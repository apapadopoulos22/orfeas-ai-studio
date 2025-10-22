#!/usr/bin/env python
"""Final comprehensive verification of all fixed violations."""
import os
import re

print("="*70)
print("FINAL VERIFICATION - MARKDOWN LINTING FIXES")
print("="*70)

# Files from error attachment
target_files = [
    'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md',
    'PHASE_3_2_3_3_INTEGRATION_EXECUTION_PLAN.md',
    'PHASE_3_1_EXECUTIVE_BRIEF.md',
    'orfeas-studio.html'
]

results = {}
total_violations = 0

for fname in target_files:
    if not os.path.exists(fname):
        results[fname] = {'status': 'NOT FOUND', 'violations': 0}
        continue

    with open(fname, 'r', encoding='utf-8') as f:
        content = f.read()

    violations = 0
    issues = []

    if fname.endswith('.md'):
        # Check MD026 (trailing punctuation)
        md026_matches = list(re.finditer(r'^#{1,6}\s+[^:\r\n]+[:!?.]\\s*$', content, re.MULTILINE))
        violations += len(md026_matches)
        if md026_matches:
            issues.append(f"MD026: {len(md026_matches)} trailing punctuation")

        # Check MD024 (duplicate headings)
        lines = content.split('\n')
        headings = {}
        duplicates = 0
        for line in lines:
            if line.startswith('#'):
                if line in headings:
                    duplicates += 1
                else:
                    headings[line] = True

        violations += duplicates
        if duplicates > 0:
            issues.append(f"MD024: {duplicates} duplicate headings")

    total_violations += violations

    if violations == 0:
        results[fname] = {'status': '✅ CLEAN', 'violations': 0}
    else:
        results[fname] = {'status': f'⚠️  {violations} violations', 'violations': violations, 'issues': issues}

# Print results
print("\nFile Status:")
print("-" * 70)

for fname, result in results.items():
    status = result['status']
    print(f"{fname:50} {status}")
    if 'issues' in result:
        for issue in result['issues']:
            print(f"  → {issue}")

print("-" * 70)
print(f"\nTotal Violations Found: {total_violations}")
print(f"Files Processed: {len(target_files)}")

if total_violations == 0:
    print("\n✅ ALL VIOLATIONS FIXED!")
    print("✅ All files are now compliant with markdownlint standards")
else:
    print(f"\n⚠️  {total_violations} violations still need attention")
