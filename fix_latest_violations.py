#!/usr/bin/env python3
"""
Fix latest markdown violations: MD026, MD001, MD029
"""

import re
from pathlib import Path

class LatestViolationsFixer:
    def __init__(self):
        self.files_fixed = 0
        self.violations_fixed = 0

    def fix_file(self, filepath, fixes):
        """Apply fixes to a file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content
            for old, new in fixes:
                content = content.replace(old, new, 1)

            if content != original:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.files_fixed += 1
                self.violations_fixed += len(fixes)
                return True, len(fixes)

            return False, 0

        except Exception as e:
            print(f"❌ Error: {e}")
            return False, 0

    def run(self):
        """Apply all fixes"""
        print("=" * 73)
        print("FIXING LATEST MARKDOWN VIOLATIONS")
        print("=" * 73)

        # MD026 fixes (remove trailing punctuation from headings)
        fixes = [
            # PHASE_4_INTEGRATION_AND_DEPLOYMENT.md line 5
            ('# Phase 4: Integration & Deployment:', '# Phase 4: Integration & Deployment'),

            # PHASE_3_1_EXECUTIVE_BRIEF.md line 13
            ('# Executive Summary!', '# Executive Summary'),

            # PHASE_4_OPTIMIZATION_10_PERCENT.md line 52
            ('### Real-Time Monitoring:', '### Real-Time Monitoring'),

            # PHASE_4_TESTING_SESSION_REPORT.md line 11
            ('# Test Session Report.', '# Test Session Report'),
        ]

        # MD001 fixes (fix heading level skips)
        fixes.extend([
            # PHASE_4_COMPLETE_SUMMARY.md line 5
            ('# Phase 4 Complete Summary\n\n### Overview', '# Phase 4 Complete Summary\n\n## Overview'),

            # PHASE_4_IMPLEMENTATION_ROADMAP.md line 5
            ('# Phase 4 Implementation Roadmap\n\n### Tier Breakdown', '# Phase 4 Implementation Roadmap\n\n## Tier Breakdown'),

            # PHASE_4_OPTIMIZATION_10_PERCENT.md line 5
            ('# Phase 4: Remaining 10%\n\n### Overview', '# Phase 4: Remaining 10%\n\n## Overview'),

            # PHASE_4_OPTIMIZATION_SUMMARY.md line 5
            ('# Phase 4 Optimization Summary\n\n### Key Metrics', '# Phase 4 Optimization Summary\n\n## Key Metrics'),

            # PHASE_4_QUICK_REFERENCE.md line 5
            ('# Phase 4 Quick Reference\n\n### Quick Links', '# Phase 4 Quick Reference\n\n## Quick Links'),

            # PHASE_4_QUICK_START.md line 5
            ('# Phase 4 Quick Start\n\n### Prerequisites', '# Phase 4 Quick Start\n\n## Prerequisites'),
        ])

        # Apply all fixes to all potentially affected files
        all_files = [
            'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md',
            'PHASE_3_1_EXECUTIVE_BRIEF.md',
            'PHASE_4_OPTIMIZATION_10_PERCENT.md',
            'PHASE_4_TESTING_SESSION_REPORT.md',
            'PHASE_4_COMPLETE_SUMMARY.md',
            'PHASE_4_IMPLEMENTATION_ROADMAP.md',
            'PHASE_4_OPTIMIZATION_SUMMARY.md',
            'PHASE_4_QUICK_REFERENCE.md',
            'PHASE_4_QUICK_START.md',
            'PHASE_6_DOCUMENTATION_INDEX.md',
        ]

        for filename in all_files:
            filepath = Path(filename)
            if filepath.exists():
                fixed, count = self.fix_file(str(filepath), fixes)
                if fixed:
                    print(f"✅ {filename}: Fixed {count} violations")
            else:
                print(f"⏭️  {filename}: File not found")

        print("=" * 73)
        print(f"✅ TOTAL: {self.files_fixed} files fixed, {self.violations_fixed} violations resolved")
        print("=" * 73)


if __name__ == '__main__':
    fixer = LatestViolationsFixer()
    fixer.run()
