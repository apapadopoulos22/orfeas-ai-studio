#!/usr/bin/env python3
"""
Direct Mojibake Fixer - Repairs corrupted UTF-8 in file content
Uses ftfy library to intelligently fix common encoding issues
"""

import os
from pathlib import Path
from typing import List, Tuple

try:
    import ftfy
except ImportError:
    print(" ftfy library not found. Installing...")
    import subprocess
    subprocess.check_call(['pip', 'install', 'ftfy'])
    import ftfy

# Remaining 38 files with mojibake issues (after first fix batch)
MOJIBAKE_FILES = [
    "docker-compose.production.yml",
    "orfeas-3d-engine-hybrid.js",
    "run_baseline_profiling.py",
    "backend/generate_test_images.py",
    "backend/gpu_manager.py",
    "backend/validate_phase2_2.py",
    "backend/validate_phase2_3.py",
    "backend/validate_phase2_4.py",
    "docs/.github/CONTRIBUTING.md",
    "docs/content/site-policy/site-policy-deprecated/github-enterprise-subscription-agreement.md",
    "docs/src/graphql/data/fpt/schema.json",
    "docs/src/graphql/data/ghec/schema.json",
    "md/COPILOT_INSTRUCTIONS_COMPARISON.md",
    "md/IMMEDIATE_IMPLEMENTATION_GUIDE.md",
    "md/MOJIBAKE_SCAN_QUICKREF.md",
    "md/PHASE_2_TESTING_REPORT.md",
    "md/PROJECT_SCAN_SUMMARY.md",
    "md/TASK8_VALIDATION_COMPLETE.md",
    "md/TOTAL_OPTIMIZATION_SUMMARY.md",
    "md/TQM_VISUAL_DASHBOARD.md",
    "md/UTILS_MODULE_SUCCESS_REPORT.md",
    "monitoring/rules/orfeas_alerts.yml",
    "ps1/ACTIVATE_REAL_3D_GENERATION.ps1",
    "ps1/FORCE_REFRESH_DIAGNOSTICS.ps1",
    "ps1/START_REAL_3D.ps1",
    "ps1/TEST_PHASE4.ps1",
    "scripts/find_encoding_issues.py",
    "scripts/fix_root_files_encoding.py",
    "txt/CODE_QUALITY_IMPROVEMENT_REPORT.txt",
    "txt/EMERGENCY_FIX_IN_PROGRESS.txt",
    "txt/EREVUS_DEUSVULT_REMOVAL_BANNER.txt",
    "txt/ONE_CLICK_AUTOMATIC.txt",
    "txt/PHASE1_COMPLETE_SUMMARY.txt",
    "txt/VISUAL_START_GUIDE.txt",
    "txt/VISUAL_SUMMARY.txt",
]
def fix_file_mojibake(file_path: str) -> Tuple[bool, str]:
    """
    Fix mojibake in a single file using ftfy

    Args:
        file_path: Path to file to fix

    Returns:
        Tuple of (success, message)
    """
    try:
        # Read file content
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            original_content = f.read()

        # Apply ftfy to fix mojibake
        fixed_content = ftfy.fix_text(original_content)

        # Check if anything changed
        if original_content == fixed_content:
            return True, "No changes needed"

        # Create backup
        backup_path = f"{file_path}.mojibake_backup"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original_content)

        # Write fixed content
        with open(file_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(fixed_content)

        # Count fixes
        changes = sum(1 for a, b in zip(original_content, fixed_content) if a != b)

        return True, f"Fixed {changes} characters"

    except Exception as e:
        return False, f"Error: {str(e)}"


def main():
    """Main execution"""
    print("=" * 80)
    print("DIRECT MOJIBAKE FIXER")
    print("=" * 80)
    print(f"\nFixing {len(MOJIBAKE_FILES)} files with ftfy...\n")

    root_dir = Path(__file__).parent

    fixed_count = 0
    no_change_count = 0
    error_count = 0

    for file_path in MOJIBAKE_FILES:
        full_path = root_dir / file_path

        if not full_path.exists():
            print(f"  SKIP: {file_path} (not found)")
            error_count += 1
            continue

        success, message = fix_file_mojibake(str(full_path))

        if success:
            if "No changes" in message:
                print(f"  OK: {file_path} ({message})")
                no_change_count += 1
            else:
                print(f" FIXED: {file_path} ({message})")
                fixed_count += 1
        else:
            print(f" ERROR: {file_path} ({message})")
            error_count += 1

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f" Fixed: {fixed_count} files")
    print(f"  No changes needed: {no_change_count} files")
    print(f" Errors: {error_count} files")
    print(f" Total processed: {len(MOJIBAKE_FILES)} files")

    if fixed_count > 0:
        print("\n Mojibake fixes applied!")
        print(" Backups created with .mojibake_backup extension")
        print("\n Next steps:")
        print("   1. Review changes in fixed files")
        print("   2. Run: python scan_project_issues.py")
        print("   3. Verify mojibake count reduced")
    else:
        print("\n  No files were changed. This might mean:")
        print("   - Files are already fixed")
        print("   - Mojibake is in a format ftfy doesn't recognize")
        print("   - File encoding issues prevent reading")


if __name__ == '__main__':
    main()
