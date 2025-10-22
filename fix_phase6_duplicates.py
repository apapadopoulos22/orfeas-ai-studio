#!/usr/bin/env python3
"""
Fix duplicate headings in PHASE_6_IMPLEMENTATION_COMPLETE.md
"""

from pathlib import Path

filepath = Path('PHASE_6_IMPLEMENTATION_COMPLETE.md')

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Map of line patterns to fixes
# These replacements add context to duplicate headings
replacements = [
    # FIX 2 section
    ('### ✅ FIX 2: Job Status API 404 Handling (HIGH)\n\n**Status:** PASSING\n**Test:** test_get_nonexistent_job_status\n**Severity:** 🟠 HIGH - Correct HTTP semantics for missing resources\n\n### Implementation',
     '### ✅ FIX 2: Job Status API 404 Handling (HIGH)\n\n**Status:** PASSING\n**Test:** test_get_nonexistent_job_status\n**Severity:** 🟠 HIGH - Correct HTTP semantics for missing resources\n\n### Implementation (FIX 2)'),

    ('**Impact:** API now correctly returns 404 for non-existent jobs instead of 200, improving REST compliance and allowing proper client-side error handling.\n\n### Test Verification',
     '**Impact:** API now correctly returns 404 for non-existent jobs instead of 200, improving REST compliance and allowing proper client-side error handling.\n\n### Test Verification (FIX 2)'),

    # FIX 3 section
    ('### ✅ FIX 3: Rate Limiting - DoS Protection (HIGH)\n\n**Status:** PASSING\n**Test:** test_rapid_health_checks (50 rapid requests)\n**Severity:** 🟠 HIGH - Prevents denial-of-service attacks\n\n### Implementation',
     '### ✅ FIX 3: Rate Limiting - DoS Protection (HIGH)\n\n**Status:** PASSING\n**Test:** test_rapid_health_checks (50 rapid requests)\n**Severity:** 🟠 HIGH - Prevents denial-of-service attacks\n\n### Implementation (FIX 3)'),

    ('- No external dependencies (Flask-Limiter incompatible with environment)\n- Graceful failure (doesn\'t break endpoint if rate limiter fails)\n\n**Impact:** Protects health check endpoint from DoS attacks while maintaining backward compatibility.\n\n### Test Verification',
     '- No external dependencies (Flask-Limiter incompatible with environment)\n- Graceful failure (doesn\'t break endpoint if rate limiter fails)\n\n**Impact:** Protects health check endpoint from DoS attacks while maintaining backward compatibility.\n\n### Test Verification (FIX 3)'),

    # FIX 4 section
    ('### ✅ FIX 4: Model Attribute Exposure (MEDIUM)\n\n**Status:** PASSING\n**Test:** test_model_loading\n**Severity:** 🟡 MEDIUM - Test compatibility & introspection\n\n### Implementation',
     '### ✅ FIX 4: Model Attribute Exposure (MEDIUM)\n\n**Status:** PASSING\n**Test:** test_model_loading\n**Severity:** 🟡 MEDIUM - Test compatibility & introspection\n\n### Implementation (FIX 4)'),

    ('2. **Update GPU Memory Tracker Fixture** (conftest.py):\n\n   - Added \'peak_allocated_mb\' key alongside existing keys\n   - Backward compatible with both naming conventions\n\n   ```python\n   return {\n       \'peak_allocated_mb\': self.peak_allocated_mb,\n       \'peak_mb\': self.peak_allocated_mb,  # backward compat\n       \'start_mb\': self.start_mb,\n       \'end_mb\': self.end_mb,\n\n       # ... other metrics\n\n   }\n\n   ```text',
     '2. **Update GPU Memory Tracker Fixture (FIX 4)** (conftest.py):\n\n   - Added \'peak_allocated_mb\' key alongside existing keys\n   - Backward compatible with both naming conventions\n\n   ```python\n   return {\n       \'peak_allocated_mb\': self.peak_allocated_mb,\n       \'peak_mb\': self.peak_allocated_mb,  # backward compat\n       \'start_mb\': self.start_mb,\n       \'end_mb\': self.end_mb,\n\n       # ... other metrics\n\n   }\n\n   ```text'),

    ('**Impact:** Test environment can now introspect model attributes without requiring full model initialization, enabling faster test cycles.\n\n### Test Verification',
     '**Impact:** Test environment can now introspect model attributes without requiring full model initialization, enabling faster test cycles.\n\n### Test Verification (FIX 4)'),

    # FIX 5 section (already has unique test verification, but add context to Implementation if needed)
    ('### ✅ FIX 5: UTF-16 BOM Detection (MEDIUM)\n\n**Status:** PASSING\n**Test:** test_detect_encoding_bom_utf16\n**Severity:** 🟡 MEDIUM - Encoding detection accuracy\n\n### Implementation',
     '### ✅ FIX 5: UTF-16 BOM Detection (MEDIUM)\n\n**Status:** PASSING\n**Test:** test_detect_encoding_bom_utf16\n**Severity:** 🟡 MEDIUM - Encoding detection accuracy\n\n### Implementation (FIX 5)'),

    ('has_bom = raw_data.startswith(b\'\\xff\\xfe\') or raw_data.startswith(b\'\\xfe\\xff\')\n           return (validated_enc, has_bom)\n       except UnicodeDecodeError:\n           continue\n\n   ```text',
     'has_bom = raw_data.startswith(b\'\\xff\\xfe\') or raw_data.startswith(b\'\\xfe\\xff\')\n           return (validated_enc, has_bom)\n       except UnicodeDecodeError:\n           continue\n\n   ```text\n\n### Test Verification (FIX 5)'),
]

# Apply all replacements
for old, new in replacements:
    if old in content:
        content = content.replace(old, new, 1)
        print(f"✅ Fixed: {old[:50]}...")
    else:
        print(f"⚠️  Not found: {old[:50]}...")

# Write back
with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ File updated successfully")
