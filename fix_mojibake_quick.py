#!/usr/bin/env python3
"""
Quick Mojibake Fix Script
Automatically fixes the 44 files with mojibake issues identified in the project scan
"""

import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from tools.encoding_fixer import main as encoding_fixer_main

# High priority files to fix
HIGH_PRIORITY_FILES = [
    'ACTIVATE_QUALITY_MONITORING.ps1',
    'CAPTURE_BACKEND_LOGS.ps1',
    'backend/openapi.yaml',
    'backend/manual_jpg_stl_workflow.py',
    'backend/simple_jpg_stl_test.py',
    'backend/run_production_benchmarks.py',
    'backend/run_production_load_test.py',
    'backend/stl_analyzer.py',
    'backend/generate_test_images.py',
]

# Medium priority files
MEDIUM_PRIORITY_FILES = [
    'backend/stl_save_analysis.py',
    'backend/gpu_manager.py',
    'backend/validate_phase2_2.py',
    'backend/validate_phase2_3.py',
    'backend/validate_phase2_4.py',
]

# Documentation files
DOC_FILES = [
    'docker-compose.production.yml',
    'md/CODE_OPTIMIZATION_PLAN.md',
]

def fix_mojibake_issues():
    """Fix all mojibake issues in the project"""

    print("=" * 80)
    print("MOJIBAKE FIX SCRIPT")
    print("=" * 80)
    print()
    print("This script will fix the 44 files with mojibake issues.")
    print("It uses ftfy library to repair corrupted UTF-8 characters.")
    print()

    # Combine all files
    all_files = HIGH_PRIORITY_FILES + MEDIUM_PRIORITY_FILES + DOC_FILES

    print(f"Files to fix: {len(all_files)}")
    print()

    # Create include pattern
    include_pattern = ','.join(all_files)

    print("Running encoding_fixer with --ftfy flag...")
    print()

    # Call encoding_fixer
    sys.argv = [
        'encoding_fixer',
        '--root', '.',
        '--include', include_pattern,
        '--ftfy',
        '--summary'
    ]

    try:
        encoding_fixer_main()
        print()
        print("=" * 80)
        print("MOJIBAKE FIX COMPLETED!")
        print("=" * 80)
        print()
        print("Next steps:")
        print("1. Review the changes")
        print("2. Run: python scan_project_issues.py")
        print("3. Verify mojibake issues are reduced")
        print()
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(fix_mojibake_issues())
