#!/usr/bin/env python3
"""
Fix remaining MD024 duplicate headings (12 violations)
"""

from pathlib import Path

fixes = [
    # PROJECT_REVIEW_AND_RECOMMENDATIONS.md
    ('PROJECT_REVIEW_AND_RECOMMENDATIONS.md', [
        ('## Integration Challenges\n\n### Likely Causes',
         '## Integration Challenges\n\n### Likely Causes (Infrastructure)'),
        ('## Evidence',
         '## Evidence (Technical Details)'),
    ]),

    # PROJECT_REVIEW_AND_ROADMAP.md - 9 duplicates
    ('PROJECT_REVIEW_AND_ROADMAP.md', [
        ('## Phase Analysis\n\n### PHASE 3.1 - AGGRESSIVE ERROR HANDLING PUSH (90-91%)\n\n### Objectives',
         '## Phase Analysis\n\n### PHASE 3.1 - AGGRESSIVE ERROR HANDLING PUSH (90-91%)\n\n### Objectives (Phase 3.1)'),
        ('### Deliverables\n\n**Implementation:**',
         '### Deliverables (Phase 3.1)\n\n**Implementation:**'),
        ('### Success Criteria\n\n**Duration:** ~30 minutes',
         '### Success Criteria (Phase 3.1)\n\n**Duration:** ~30 minutes'),
        ('### PHASE 3.2 - LLM ROUTER ROLLOUT (91-92%)\n\n### Objectives',
         '### PHASE 3.2 - LLM ROUTER ROLLOUT (91-92%)\n\n### Objectives (Phase 3.2)'),
        ('### Deliverables\n\n**Implementation:**\n\n- llm_router.py',
         '### Deliverables (Phase 3.2)\n\n**Implementation:**\n\n- llm_router.py'),
        ('### Success Criteria\n\n**Duration:** ~30 minutes\n\n**Verification:**',
         '### Success Criteria (Phase 3.2)\n\n**Duration:** ~30 minutes\n\n**Verification:**'),
        ('### PHASE 3.3 - FINAL POLISH (92-93%)\n\n### Objectives',
         '### PHASE 3.3 - FINAL POLISH (92-93%)\n\n### Objectives (Phase 3.3)'),
        ('### Deliverables\n\n**Implementation:**\n\n- Complete error handling',
         '### Deliverables (Phase 3.3)\n\n**Implementation:**\n\n- Complete error handling'),
        ('### Success Criteria\n\n**Duration:** ~15 minutes\n\n**Exit Criteria:**',
         '### Success Criteria (Phase 3.3)\n\n**Duration:** ~15 minutes\n\n**Exit Criteria:**'),
    ]),

    # REVIEW_SUMMARY_AND_RECOMMENDATION.md
    ('REVIEW_SUMMARY_AND_RECOMMENDATION.md', [
        ('## Error Handling\n\n### Features',
         '## Error Handling\n\n### Features (Error Management)'),
    ]),

    # SESSION_SUMMARY_2025_10_20.md
    ('SESSION_SUMMARY_2025_10_20.md', [
        ('## Session Review\n\n### We discovered',
         '## Session Review\n\n### We discovered (Key Findings)'),
    ]),

    # SESSION_SUMMARY_6C.md
    ('SESSION_SUMMARY_6C.md', [
        ('## Deliverables Overview\n\n### Components',
         '## Deliverables Overview\n\n### Components (5 Total)'),
        ('### Validation\n\n**Framework:**',
         '### Validation (Tests)\n\n**Framework:**'),
        ('## Code Quality\n\n### Validation',
         '## Code Quality\n\n### Validation (Assessment)'),
    ]),

    # TQM_FINAL_CHECKLIST.md
    ('TQM_FINAL_CHECKLIST.md', [
        ('## Phase 6B\n\n### Deliverables',
         '## Phase 6B\n\n### Deliverables (API Documentation)'),
        ('## Phase 6D\n\n### Deliverables',
         '## Phase 6D\n\n### Deliverables (Performance Optimization)'),
        ('### Next Steps',
         '### Next Steps (Phase 6D)'),
    ]),
]

print("=" * 73)
print("FIXING REMAINING MD024 DUPLICATE HEADINGS (12 VIOLATIONS)")
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
        else:
            print(f"⚠️  Pattern not found in {filename}: {old[:40]}...")

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {filename}: Fixed {count} violations")
        total_fixed += count
    else:
        print(f"⏭️  {filename}: No changes needed")

print("=" * 73)
print(f"✅ TOTAL: {total_fixed} violations fixed")
print("=" * 73)
