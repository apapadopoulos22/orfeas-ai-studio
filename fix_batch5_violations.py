#!/usr/bin/env python3
"""
Comprehensive fixer for batch 5 violations (45 issues)
Fixes: MD026 (trailing punctuation), MD024 (duplicates), MD001 (heading levels)
"""

import re
from pathlib import Path

class BatchFixer:
    def __init__(self):
        self.files_fixed = 0
        self.violations_fixed = 0

    def fix_file(self, filepath, fixes):
        """Apply list of (old, new) fixes to a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            count = 0

            for old, new in fixes:
                if old in content:
                    content = content.replace(old, new, 1)
                    count += 1

            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_fixed += 1
                self.violations_fixed += count
                return True, count

            return False, 0

        except Exception as e:
            print(f"❌ Error: {e}")
            return False, 0

    def run(self):
        """Apply all fixes"""
        print("=" * 73)
        print("BATCH 5: COMPREHENSIVE MARKDOWN VIOLATION FIXER (45 VIOLATIONS)")
        print("=" * 73)

        files_and_fixes = [
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

            # PROJECT_REVIEW_AND_RECOMMENDATIONS.md - lines 116, 124, 134 MD026 + MD024
            ('PROJECT_REVIEW_AND_RECOMMENDATIONS.md', [
                ('## Key Recommendations:', '## Key Recommendations'),
                ('## Implementation Timeline:', '## Implementation Timeline (Phase Overview)'),
                ('## Resource Requirements:', '## Resource Requirements (Teams & Skills)'),
            ]),

            # PROJECT_REVIEW_AND_ROADMAP.md - 9 MD024 duplicates
            ('PROJECT_REVIEW_AND_ROADMAP.md', [
                ('## Key Findings (Executive Summary)\n\n### Phase Analysis (Lines 369-430)\n\n#### FIX 1\n\n### Overview',
                 '## Key Findings (Executive Summary)\n\n### Phase Analysis (Lines 369-430)\n\n#### FIX 1\n\n### Overview (FIX 1)'),
                ('#### FIX 2\n\n### Overview',
                 '#### FIX 2\n\n### Overview (FIX 2)'),
                ('#### FIX 3\n\n### Overview',
                 '#### FIX 3\n\n### Overview (FIX 3)'),
                ('#### FIX 4\n\n### Overview',
                 '#### FIX 4\n\n### Overview (FIX 4)'),
                ('#### FIX 5\n\n### Overview',
                 '#### FIX 5\n\n### Overview (FIX 5)'),
                ('#### FIX 6\n\n### Overview',
                 '#### FIX 6\n\n### Overview (FIX 6)'),
                ('#### FIX 7\n\n### Overview',
                 '#### FIX 7\n\n### Overview (FIX 7)'),
                ('#### FIX 8\n\n### Overview',
                 '#### FIX 8\n\n### Overview (FIX 8)'),
                ('#### FIX 9\n\n### Overview',
                 '#### FIX 9\n\n### Overview (FIX 9)'),
            ]),

            # QUICK_DEPLOY_REFERENCE.md - line 5 MD026
            ('QUICK_DEPLOY_REFERENCE.md', [
                ('## Quick Deploy Guide:', '## Quick Deploy Guide'),
            ]),

            # REVIEW_SUMMARY_AND_RECOMMENDATION.md - lines 55, 73, 86, 228 MD026 + MD024
            ('REVIEW_SUMMARY_AND_RECOMMENDATION.md', [
                ('## Strategic Recommendations:', '## Strategic Recommendations'),
                ('## Implementation Path:', '## Implementation Path'),
                ('## Team Readiness:', '## Team Readiness (Assessment)'),
                ('## Quality Metrics:', '## Quality Metrics'),
            ]),

            # SESSION_SUMMARY_2025_10_20.md - lines 15, 31, 47 MD026 + MD024
            ('SESSION_SUMMARY_2025_10_20.md', [
                ('## Session Overview:', '## Session Overview'),
                ('## Key Achievements:', '## Key Achievements'),
                ('## Recommendations:', '## Recommendations (Next Actions)'),
            ]),

            # SESSION_SUMMARY_6C.md - lines 22, 31, 43, 51, 62, 78, 87, 96 MD026 + MD024
            ('SESSION_SUMMARY_6C.md', [
                ('## Session Overview:', '## Session Overview'),
                ('## Key Metrics:', '## Key Metrics'),
                ('## Deliverables:', '## Deliverables (5 Components)'),
                ('## Technical Highlights:', '## Technical Highlights (Architecture)'),
                ('## Quality Results:', '## Quality Results'),
                ('## Next Steps:', '## Next Steps'),
                ('## Code Quality:', '## Code Quality (Analysis)'),
                ('## Deployment Checklist:', '## Deployment Checklist'),
            ]),

            # THREE_PATHS_TO_90_PERCENT.md - lines 242, 250 MD026
            ('THREE_PATHS_TO_90_PERCENT.md', [
                ('## Path Comparison Summary:', '## Path Comparison Summary'),
                ('## Final Recommendation!', '## Final Recommendation'),
            ]),

            # TQM_FINAL_CHECKLIST.md - lines 112, 161, 169, 227, 234 MD026 + MD024
            ('TQM_FINAL_CHECKLIST.md', [
                ('## Phase 6 Quality Checklist:', '## Phase 6 Quality Checklist'),
                ('## Documentation:', '## Documentation (Complete)'),
                ('## Testing:', '## Testing'),
                ('## Deployment:', '## Deployment (Readiness)'),
                ('## Final Sign-off:', '## Final Sign-off (Release)'),
            ]),
        ]

        for filename, fixes in files_and_fixes:
            filepath = Path(filename)
            if filepath.exists():
                fixed, count = self.fix_file(str(filepath), fixes)
                if fixed:
                    print(f"✅ {filename}: Fixed {count} violations")
                else:
                    print(f"⏭️  {filename}: No changes needed")
            else:
                print(f"⚠️  {filename}: File not found")

        print("=" * 73)
        print(f"✅ TOTAL: {self.files_fixed} files fixed, {self.violations_fixed} violations resolved")
        print("=" * 73)


if __name__ == '__main__':
    fixer = BatchFixer()
    fixer.run()
