#!/usr/bin/env python3
"""
Targeted Duplicate Heading Fixer for Remaining Issues
"""

import re
from pathlib import Path

def fix_duplicate_singleton_headings():
    """Fix duplicate 'Singleton' headings by adding context"""
    filepath = Path('PHASE_4_OPTIMIZATION_10_PERCENT.md')
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find all 'Singleton' headings
    singleton_positions = []
    for i, line in enumerate(lines):
        if re.match(r'^## Singleton\s*$', line):
            singleton_positions.append(i)

    # Update each duplicate (keep first, rename others)
    fixed_count = 0
    for idx, pos in enumerate(singleton_positions[1:], 1):  # Skip first
        # Get context from surrounding code
        context = None
        for j in range(pos - 1, max(0, pos - 20), -1):
            if 'DistributedCacheManager' in lines[j]:
                context = 'Distributed Cache Manager'
                break
            elif 'Hunyuan' in lines[j]:
                context = 'Hunyuan Model'
                break

        if context:
            lines[pos] = f'## Singleton ({context})\n'
            fixed_count += 1
        else:
            lines[pos] = f'## Singleton Pattern {idx + 1}\n'
            fixed_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return fixed_count

def fix_duplicate_enterprise_standards():
    """Fix duplicate 'Enterprise Standards' heading"""
    filepath = Path('MARKDOWN_LINTING_FINAL_VERIFICATION.md')
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find all 'Enterprise Standards' headings
    heading_positions = []
    for i, line in enumerate(lines):
        if re.match(r'^### Enterprise Standards\s*$', line):
            heading_positions.append(i)

    # Update duplicates
    fixed_count = 0
    for idx, pos in enumerate(heading_positions[1:], 1):  # Skip first
        # Get context
        context = None
        for j in range(pos - 1, max(0, pos - 15), -1):
            if 'Quality' in lines[j]:
                context = 'Quality Assurance'
                break
            elif 'Compliance' in lines[j]:
                context = 'ISO Compliance'
                break

        if context:
            lines[pos] = f'### Enterprise Standards ({context})\n'
        else:
            lines[pos] = f'### Enterprise Standards {idx + 1}\n'
        fixed_count += 1

    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(lines)

    return fixed_count

if __name__ == '__main__':
    print("Fixing remaining duplicate headings...")
    count1 = fix_duplicate_singleton_headings()
    print(f"✅ Fixed {count1} 'Singleton' duplicates in PHASE_4_OPTIMIZATION_10_PERCENT.md")

    count2 = fix_duplicate_enterprise_standards()
    print(f"✅ Fixed {count2} 'Enterprise Standards' duplicates in MARKDOWN_LINTING_FINAL_VERIFICATION.md")

    print(f"\n✅ TOTAL: {count1 + count2} duplicate headings fixed")
