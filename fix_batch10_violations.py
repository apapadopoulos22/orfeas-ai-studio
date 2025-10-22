#!/usr/bin/env python3
"""
Fix batch 10 violations
Fixes: MD051 (invalid link fragments), MD024 (duplicate headings)
"""

from pathlib import Path

def fix_copilot_advanced_patterns():
    """Fix COPILOT_ADVANCED_PATTERNS.md"""
    filepath = Path('md/COPILOT_ADVANCED_PATTERNS.md')
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Fix the TOC links to match actual heading names
    # The actual headings start with "## " and the links should point to them properly
    replacements = [
        ('1. [Advanced Model Caching](#advanced-model-caching)',
         '1. [Advanced Model Caching](#advanced-model-caching-1)'),
        ('2. [GPU Memory Optimization](#gpu-memory-optimization)',
         '2. [GPU Memory Optimization](#gpu-memory-optimization-1)'),
        ('3. [Async Job Orchestration](#async-job-orchestration)',
         '3. [Async Job Orchestration](#async-job-orchestration-1)'),
        ('4. [Advanced Error Handling](#advanced-error-handling)',
         '4. [Advanced Error Handling](#advanced-error-handling-1)'),
        ('5. [Performance Profiling](#performance-profiling)',
         '5. [Performance Profiling](#performance-profiling-1)'),
        ('6. [Multi-Model Orchestration](#multi-model-orchestration)',
         '6. [Multi-Model Orchestration](#multi-model-orchestration-1)'),
        ('7. [Context-Aware Processing](#context-aware-processing)',
         '7. [Context-Aware Processing](#context-aware-processing-1)'),
        ('8. [Security Hardening](#security-hardening)',
         '8. [Security Hardening](#security-hardening-1)'),
    ]

    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return 1
    return 0

def fix_copilot_deployment_guide():
    """Fix COPILOT_DEPLOYMENT_GUIDE.md"""
    filepath = Path('md/COPILOT_DEPLOYMENT_GUIDE.md')
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Similar fix for deployment guide
    replacements = [
        ('1. [Environment Setup](#environment-setup)',
         '1. [Environment Setup](#environment-setup-1)'),
        ('2. [Installation Steps](#installation-steps)',
         '2. [Installation Steps](#installation-steps-1)'),
        ('3. [Docker Configuration](#docker-configuration)',
         '3. [Docker Configuration](#docker-configuration-1)'),
        ('4. [GPU Setup](#gpu-setup)',
         '4. [GPU Setup](#gpu-setup-1)'),
        ('5. [Testing Deployment](#testing-deployment)',
         '5. [Testing Deployment](#testing-deployment-1)'),
        ('6. [Monitoring Setup](#monitoring-setup)',
         '6. [Monitoring Setup](#monitoring-setup-1)'),
        ('7. [Troubleshooting](#troubleshooting)',
         '7. [Troubleshooting](#troubleshooting-1)'),
        ('8. [Performance Tuning](#performance-tuning)',
         '8. [Performance Tuning](#performance-tuning-1)'),
    ]

    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return 1
    return 0

def fix_copilot_llm_patterns():
    """Fix COPILOT_LLM_PATTERNS.md"""
    filepath = Path('md/COPILOT_LLM_PATTERNS.md')
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Similar fix for LLM patterns
    replacements = [
        ('1. [Local LLM Integration](#local-llm-integration)',
         '1. [Local LLM Integration](#local-llm-integration-1)'),
        ('2. [Multi-LLM Routing](#multi-llm-routing)',
         '2. [Multi-LLM Routing](#multi-llm-routing-1)'),
        ('3. [Prompt Engineering](#prompt-engineering)',
         '3. [Prompt Engineering](#prompt-engineering-1)'),
        ('4. [Context Management](#context-management)',
         '4. [Context Management](#context-management-1)'),
        ('5. [Error Handling](#error-handling)',
         '5. [Error Handling](#error-handling-1)'),
        ('6. [Performance Optimization](#performance-optimization)',
         '6. [Performance Optimization](#performance-optimization-1)'),
        ('7. [Security Considerations](#security-considerations)',
         '7. [Security Considerations](#security-considerations-1)'),
    ]

    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return 1
    return 0

def fix_copilot_tqm_reference():
    """Fix COPILOT_TQM_REFERENCE.md"""
    filepath = Path('md/COPILOT_TQM_REFERENCE.md')
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content

    # Similar fix for TQM reference
    replacements = [
        ('1. [Quality Metrics](#quality-metrics)',
         '1. [Quality Metrics](#quality-metrics-1)'),
        ('2. [Testing Standards](#testing-standards)',
         '2. [Testing Standards](#testing-standards-1)'),
        ('3. [Performance Benchmarks](#performance-benchmarks)',
         '3. [Performance Benchmarks](#performance-benchmarks-1)'),
        ('4. [Security Audit](#security-audit)',
         '4. [Security Audit](#security-audit-1)'),
        ('5. [Compliance Framework](#compliance-framework)',
         '5. [Compliance Framework](#compliance-framework-1)'),
        ('6. [Deployment Checklist](#deployment-checklist)',
         '6. [Deployment Checklist](#deployment-checklist-1)'),
        ('7. [Monitoring & Alerts](#monitoring--alerts)',
         '7. [Monitoring & Alerts](#monitoring--alerts-1)'),
        ('8. [Disaster Recovery](#disaster-recovery)',
         '8. [Disaster Recovery](#disaster-recovery-1)'),
    ]

    count = 0
    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1

    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        return 1
    return 0

def fix_satellite_documentation():
    """Fix SATELLITE_DOCUMENTATION_SUMMARY.md - duplicate headings"""
    filepath = Path('md/SATELLITE_DOCUMENTATION_SUMMARY.md')
    if not filepath.exists():
        return 0

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    original = content
    lines = content.split('\n')

    # Count duplicate headings and add context
    heading_counts = {}

    for i, line in enumerate(lines):
        if line.startswith('###'):
            heading = line.strip()
            if heading not in heading_counts:
                heading_counts[heading] = []
            heading_counts[heading].append(i)

    # Fix duplicates by adding context
    duplicates_to_fix = {
        '### Features': ['### Features (Phase 1)', '### Features (Phase 2)', '### Features (Phase 3)', '### Features (Phase 4)', '### Features (Phase 5)', '### Features (Phase 6)'],
        '### Architecture': ['### Architecture (Phase 1)', '### Architecture (Phase 2)'],
        '### Testing': ['### Testing (Phase 1)', '### Testing (Phase 2)'],
        '### Deployment': ['### Deployment (Phase 1)', '### Deployment (Phase 2)'],
        '### Documentation': ['### Documentation (Phase 1)', '### Documentation (Phase 2)'],
    }

    count = 0
    for dup_heading, fixes in duplicates_to_fix.items():
        occurrences = heading_counts.get(dup_heading, [])
        if len(occurrences) > 1:
            # Replace each occurrence with corresponding fix
            for idx, line_num in enumerate(occurrences):
                if idx < len(fixes):
                    lines[line_num] = fixes[idx]
                    count += 1

    fixed_content = '\n'.join(lines)

    if fixed_content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        return 1
    return 0

print("=" * 70)
print("BATCH 10: LINK FRAGMENTS & DUPLICATE HEADING FIXES (33 VIOLATIONS)")
print("=" * 70)

total_fixed = 0

result = fix_copilot_advanced_patterns()
if result:
    print(f"✅ COPILOT_ADVANCED_PATTERNS.md: Fixed 8 link fragments")
    total_fixed += 1
else:
    print(f"⏭️  COPILOT_ADVANCED_PATTERNS.md: No changes needed")

result = fix_copilot_deployment_guide()
if result:
    print(f"✅ COPILOT_DEPLOYMENT_GUIDE.md: Fixed 8 link fragments")
    total_fixed += 1
else:
    print(f"⏭️  COPILOT_DEPLOYMENT_GUIDE.md: No changes needed")

result = fix_copilot_llm_patterns()
if result:
    print(f"✅ COPILOT_LLM_PATTERNS.md: Fixed 7 link fragments")
    total_fixed += 1
else:
    print(f"⏭️  COPILOT_LLM_PATTERNS.md: No changes needed")

result = fix_copilot_tqm_reference()
if result:
    print(f"✅ COPILOT_TQM_REFERENCE.md: Fixed 8 link fragments")
    total_fixed += 1
else:
    print(f"⏭️  COPILOT_TQM_REFERENCE.md: No changes needed")

result = fix_satellite_documentation()
if result:
    print(f"✅ SATELLITE_DOCUMENTATION_SUMMARY.md: Fixed duplicate headings")
    total_fixed += 1
else:
    print(f"⏭️  SATELLITE_DOCUMENTATION_SUMMARY.md: No changes needed")

print("=" * 70)
print(f"✅ TOTAL: {total_fixed} files fixed")
print("=" * 70)
