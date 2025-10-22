"""
[ORFEAS] ORFEAS EMERGENCY FIX: Patch Diffusers Library
Fixes cached_download import error in diffusers package
"""

import os
import sys
from pathlib import Path

print("\n+==============================================================================â•—")
print("| [WARRIOR] ORFEAS DIFFUSERS PATCH - SUCCESS! [WARRIOR]                             |")
print("+==============================================================================\n")

# Find diffusers installation
try:
    import diffusers
    diffusers_path = Path(diffusers.__file__).parent
    print(f"[OK] Found diffusers at: {diffusers_path}")
except ImportError:
    print("[FAIL] diffusers not installed!")
    sys.exit(1)

# Patch the dynamic_modules_utils.py file
patch_file = diffusers_path / "utils" / "dynamic_modules_utils.py"

if not patch_file.exists():
    print(f"[FAIL] File not found: {patch_file}")
    sys.exit(1)

print(f"[EDIT] Reading: {patch_file}")

# Read current content
with open(patch_file, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if already patched
if 'ORFEAS PATCH' in content:
    print("[OK] File already patched - no changes needed")
    sys.exit(0)

# Find the problematic import line
old_import = "from huggingface_hub import cached_download, hf_hub_download, model_info"

if old_import not in content:
    print(f"[WARN] Expected import line not found")
    print(f"   Looking for: {old_import}")
    print("   File may have been updated - manual patching required")
    sys.exit(1)

# Create the patched import
new_import = """# [ORFEAS] ORFEAS PATCH: Fix cached_download compatibility issue
try:
    from huggingface_hub import cached_download, hf_hub_download, model_info
except ImportError:
    # cached_download was removed in huggingface_hub >= 0.20.0
    from huggingface_hub import hf_hub_download, model_info
    # Create compatibility alias
    cached_download = hf_hub_download
    print("[WARN] ORFEAS: Using hf_hub_download as cached_download fallback")
"""

# Apply patch
content = content.replace(old_import, new_import)

# Backup original file
backup_file = patch_file.with_suffix('.py.ORFEAS_backup')
print(f" Creating backup: {backup_file}")

with open(backup_file, 'w', encoding='utf-8') as f:
    f.write(content.replace(new_import, old_import))  # Write original content to backup

# Write patched content
print(f" Writing patched file...")

with open(patch_file, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n+==============================================================================â•—")
print("| [OK] DIFFUSERS PATCHED SUCCESSFULLY - SUCCESS! [OK]                          |")
print("+==============================================================================\n")

print(" Changes made:")
print(f"   [OK] Patched: {patch_file}")
print(f"   [OK] Backup: {backup_file}")
print("\n[TARGET] Next step: Run test_real_3d_generation.py to verify")
