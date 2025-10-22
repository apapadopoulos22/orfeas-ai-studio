#!/usr/bin/env python3
"""
Fix batch 6 violations (16 total)
Fixes: MD026 (trailing punctuation), MD001 (heading levels)
"""

from pathlib import Path

fixes = [
    # PHASE_3_1_EXECUTIVE_BRIEF.md - line 13 MD026
    ('PHASE_3_1_EXECUTIVE_BRIEF.md', [
        ('## Files 1-2 of Phase 3.1 (LLM Integration) are already implemented!',
         '## Files 1-2 of Phase 3.1 (LLM Integration) are already implemented'),
    ]),

    # PHASE_4_COMPLETE_SUMMARY.md - line 5 MD001
    ('PHASE_4_COMPLETE_SUMMARY.md', [
        ('# ✅ PHASE 4 COMPLETE - COMPREHENSIVE DOCUMENTATION PACKAGE\n\n## Everything You Need to Optimize the Remaining 10%\n\n---\n\n## 📦 DELIVERABLES SUMMARY\n\n### Documentation Package Created',
         '# ✅ PHASE 4 COMPLETE - COMPREHENSIVE DOCUMENTATION PACKAGE\n\n## Everything You Need to Optimize the Remaining 10%\n\n---\n\n## 📦 DELIVERABLES SUMMARY\n\n## Documentation Package Created'),
    ]),

    # PHASE_4_OPTIMIZATION_10_PERCENT.md - line 52 MD026
    ('PHASE_4_OPTIMIZATION_10_PERCENT.md', [
        ('### Real-Time Monitoring:', '### Real-Time Monitoring'),
    ]),

    # PHASE_6_IMPLEMENTATION_SUMMARY.md - line 89 MD026
    ('PHASE_6_IMPLEMENTATION_SUMMARY.md', [
        ('### Artifacts Generated:', '### Artifacts Generated'),
    ]),

    # PHASE_6_TEST_RESULTS_SUMMARY.md - line 39 MD026
    ('PHASE_6_TEST_RESULTS_SUMMARY.md', [
        ('### Current State:', '### Current State'),
    ]),

    # PHASE_6C_IMPLEMENTATION_PLAN.md - line 55 MD026
    ('PHASE_6C_IMPLEMENTATION_PLAN.md', [
        ('### Architecture Design:', '### Architecture Design'),
    ]),

    # PHASE_6C_PROGRESS_REPORT.md - line 25 MD026
    ('PHASE_6C_PROGRESS_REPORT.md', [
        ('### Implementation Status:', '### Implementation Status'),
    ]),

    # PROJECT_COMPLETION_SUMMARY.md - line 3 MD001
    ('PROJECT_COMPLETION_SUMMARY.md', [
        ('# PROJECT COMPLETION SUMMARY\n\n### Executive Overview',
         '# PROJECT COMPLETION SUMMARY\n\n## Executive Overview'),
    ]),

    # PROJECT_FIXES_COMPLETE.md - line 106 MD026
    ('PROJECT_FIXES_COMPLETE.md', [
        ('### All Production Components Ready!',
         '### All Production Components Ready'),
    ]),

    # README_FINAL_DELIVERY.md - line 73 MD026
    ('README_FINAL_DELIVERY.md', [
        ('## Enterprise Production Status:', '## Enterprise Production Status'),
    ]),

    # REVIEW_HANDOFF_SUMMARY.md - line 11 MD026
    ('REVIEW_HANDOFF_SUMMARY.md', [
        ('## Project Status Summary.',
         '## Project Status Summary'),
    ]),

    # THREE_PATHS_TO_90_PERCENT.md - lines 242, 250 MD026
    ('THREE_PATHS_TO_90_PERCENT.md', [
        ('## Path Comparison Summary:', '## Path Comparison Summary'),
        ('## Final Recommendation!', '## Final Recommendation'),
    ]),

    # TQM_PHASE_6_EXECUTIVE_SUMMARY.md - lines 30, 38, 44 MD026
    ('TQM_PHASE_6_EXECUTIVE_SUMMARY.md', [
        ('## Phase 6A Results:', '## Phase 6A Results'),
        ('## Phase 6B Results:', '## Phase 6B Results'),
        ('## Phase 6D Results:', '## Phase 6D Results'),
    ]),
]

print("=" * 73)
print("BATCH 6: TRAILING PUNCTUATION & HEADING LEVEL FIXES (16 VIOLATIONS)")
print("=" * 73)

total_fixed = 0

for filename, file_fixes in fixes:
    filepath = Path(filename)
    if not filepath.exists():
        print(f"❌ {filename}: File not found")
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    count = 0

    for old, new in file_fixes:
        if old in content:
            content = content.replace(old, new, 1)
            count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename}: Fixed {count} violations")
        total_fixed += count
    else:
        print(f"⏭️  {filename}: No changes needed or pattern not found")

print("=" * 73)
print(f"✅ TOTAL: {total_fixed} violations fixed")
print("=" * 73)
