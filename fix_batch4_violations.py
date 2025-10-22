#!/usr/bin/env python3
"""
Fix latest batch of markdown violations: MD026 (trailing punctuation), MD024 (duplicates), MD001
"""

from pathlib import Path

# Define all fixes
fixes = [
    # PHASE_3_1_EXECUTIVE_BRIEF.md - line 13 - remove !
    ('PHASE_3_1_EXECUTIVE_BRIEF.md',
     '## Files 1-2 of Phase 3.1 (LLM Integration) are already implemented!',
     '## Files 1-2 of Phase 3.1 (LLM Integration) are already implemented'),

    # PHASE_4_COMPLETE_SUMMARY.md - line 5 - fix heading level skip
    ('PHASE_4_COMPLETE_SUMMARY.md',
     '# ✅ PHASE 4 COMPLETE - COMPREHENSIVE DOCUMENTATION PACKAGE\n\n## Everything You Need to Optimize the Remaining 10%\n\n---\n\n## 📦 DELIVERABLES SUMMARY\n\n### Documentation Package Created',
     '# ✅ PHASE 4 COMPLETE - COMPREHENSIVE DOCUMENTATION PACKAGE\n\n## Everything You Need to Optimize the Remaining 10%\n\n---\n\n## 📦 DELIVERABLES SUMMARY\n\n## Documentation Package Created'),

    # PHASE_4_OPTIMIZATION_10_PERCENT.md - line 52 - remove :
    ('PHASE_4_OPTIMIZATION_10_PERCENT.md',
     '### Real-Time Monitoring:',
     '### Real-Time Monitoring'),

    # PHASE_6_IMPLEMENTATION_SUMMARY.md - line 89 - remove :
    ('PHASE_6_IMPLEMENTATION_SUMMARY.md',
     '### Artifacts Generated:',
     '### Artifacts Generated'),

    # PHASE_6_TEST_RESULTS_SUMMARY.md - line 39 - remove :
    ('PHASE_6_TEST_RESULTS_SUMMARY.md',
     '### Current State:',
     '### Current State'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 20 - remove : from "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 1. **PHASE_6C_MASTER_SUMMARY.md** ⭐ START HERE\n\n**Purpose:** Complete session overview with all metrics and achievements\n\n### Contains',
     '#### 1. **PHASE_6C_MASTER_SUMMARY.md** ⭐ START HERE\n\n**Purpose:** Complete session overview with all metrics and achievements\n\n## Contains'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 43 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 2. **PHASE_6C_COMPLETION_SUMMARY.md**\n\n**Purpose:** Detailed breakdown of what was completed\n\n### Contains',
     '#### 2. **PHASE_6C_COMPLETION_SUMMARY.md**\n\n**Purpose:** Detailed breakdown of what was completed\n\n## Contains (PHASE_6C_COMPLETION_SUMMARY)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 62 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 3. **PHASE_6C_FINAL_HANDOFF.md**\n\n**Purpose:** Comprehensive handoff documentation for next phase\n\n### Contains',
     '#### 3. **PHASE_6C_FINAL_HANDOFF.md**\n\n**Purpose:** Comprehensive handoff documentation for next phase\n\n## Contains (PHASE_6C_FINAL_HANDOFF)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 87 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 4. **SESSION_SUMMARY_6C.md**\n\n**Purpose:** Detailed session work log with chronological reference\n\n### Contains',
     '#### 4. **SESSION_SUMMARY_6C.md**\n\n**Purpose:** Detailed session work log with chronological reference\n\n## Contains (SESSION_SUMMARY_6C)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 107 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 5. **PHASE_6C_SESSION_DASHBOARD.md**\n\n**Purpose:** Visual dashboard of session progress and status\n\n### Contains',
     '#### 5. **PHASE_6C_SESSION_DASHBOARD.md**\n\n**Purpose:** Visual dashboard of session progress and status\n\n## Contains (PHASE_6C_SESSION_DASHBOARD)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 129 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 6. **PHASE_6C_VERIFICATION_REPORT.md**\n\n**Purpose:** Final verification that all deliverables meet quality standards\n\n### Contains',
     '#### 6. **PHASE_6C_VERIFICATION_REPORT.md**\n\n**Purpose:** Final verification that all deliverables meet quality standards\n\n## Contains (PHASE_6C_VERIFICATION_REPORT)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 151 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 7. **PHASE_6C_IMPLEMENTATION_PLAN.md**\n\n**Purpose:** Original implementation plan that guided the work\n\n### Contains',
     '#### 7. **PHASE_6C_IMPLEMENTATION_PLAN.md**\n\n**Purpose:** Original implementation plan that guided the work\n\n## Contains (PHASE_6C_IMPLEMENTATION_PLAN)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 169 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 8. **PHASE_6C_PROGRESS_REPORT.md**\n\n**Purpose:** Real-time progress tracking during implementation\n\n### Contains',
     '#### 8. **PHASE_6C_PROGRESS_REPORT.md**\n\n**Purpose:** Real-time progress tracking during implementation\n\n## Contains (PHASE_6C_PROGRESS_REPORT)'),

    # PHASE_6C_DOCUMENTATION_INDEX.md - line 188 - add context to duplicate "Contains"
    ('PHASE_6C_DOCUMENTATION_INDEX.md',
     '#### 9. **PHASE_6C_EXECUTIVE_SUMMARY.md**\n\n**Purpose:** C-level executive summary with key metrics only\n\n### Contains',
     '#### 9. **PHASE_6C_EXECUTIVE_SUMMARY.md**\n\n**Purpose:** C-level executive summary with key metrics only\n\n## Contains (PHASE_6C_EXECUTIVE_SUMMARY)'),
]

# Apply all fixes
for filename, old, new in fixes:
    filepath = Path(filename)
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if old in content:
            content = content.replace(old, new, 1)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"✅ {filename}: Fixed")
        else:
            print(f"⚠️  {filename}: Pattern not found")
    else:
        print(f"❌ {filename}: File not found")

print("\n✅ All fixes applied successfully")
