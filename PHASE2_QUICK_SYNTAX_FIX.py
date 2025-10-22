#!/usr/bin/env python3
"""
ORFEAS AI - Quick Syntax Fix for Phase 2 Completion
==================================================
"""

import re
from pathlib import Path

def fix_duplicate_try_statements(content):
    """Fix duplicate try statements from regex damage"""
    # Remove duplicate try statements
    content = re.sub(r'(\s+)try:(\s+)try:', r'\1try:', content, flags=re.MULTILINE)
    return content

def fix_indentation_issues(content):
    """Fix basic indentation issues"""
    lines = content.split('\n')
    fixed_lines = []
    
    for i, line in enumerate(lines):
        # Fix common indentation problems
        if line.strip().startswith('try:') and i > 0:
            prev_line = lines[i-1]
            if prev_line.strip() and not prev_line.startswith('#'):
                # Ensure proper indentation for try block
                indent = len(prev_line) - len(prev_line.lstrip())
                line = ' ' * indent + line.strip()
        
        fixed_lines.append(line)
    
    return '\n'.join(fixed_lines)

def quick_fix_file(file_path):
    """Apply quick fixes to a file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Apply fixes
        content = fix_duplicate_try_statements(content)
        content = fix_indentation_issues(content)
        
        if content != original_content:
            # Backup original
            backup_path = file_path.with_suffix(file_path.suffix + '.quickfix_backup')
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            
            # Write fixed version
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f" Fixed: {file_path}")
            return True
        else:
            print(f"ℹ No changes needed: {file_path}")
            return False
            
    except Exception as e:
        print(f" Error fixing {file_path}: {e}")
        return False

def main():
    """Quick fix main files"""
    backend_dir = Path("backend")
    target_files = [
        backend_dir / "main.py",
        backend_dir / "validation.py", 
        backend_dir / "hunyuan_integration.py"
    ]
    
    print(" ORFEAS AI - Quick Syntax Fix")
    print("=" * 35)
    
    fixed_count = 0
    for file_path in target_files:
        if file_path.exists():
            if quick_fix_file(file_path):
                fixed_count += 1
        else:
            print(f" File not found: {file_path}")
    
    print(f"\n Fixed {fixed_count} files")
    print(" Run PHASE2_VALIDATION.py to check syntax")

if __name__ == "__main__":
    main()
