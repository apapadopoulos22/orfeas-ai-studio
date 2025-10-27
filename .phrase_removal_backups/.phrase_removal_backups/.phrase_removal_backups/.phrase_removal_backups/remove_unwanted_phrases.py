#!/usr/bin/env python3
"""
Automated Phrase Removal System - BOB AI v9.0

Purpose: Scan and remove unwanted phrases from all project files
Phrases: "", "", ""

This script:
1. Recursively scans all files in the project directory
2. Identifies files containing unwanted phrases
3. Removes all occurrences (case-sensitive)
4. Preserves file formatting and structure
5. Creates backup before modifications
6. Generates cleanup report
"""

import os
import sys
from pathlib import Path
import re
from datetime import datetime
import shutil

# Configuration
WORKSPACE_ROOT = Path(r"c:\Users\johng\Documents\oscar")
UNWANTED_PHRASES = ["", "", ""]
BACKUP_DIR = WORKSPACE_ROOT / ".phrase_removal_backups"
BINARY_EXTENSIONS = {'.bin', '.exe', '.dll', '.so', '.pyc', '.zip', '.gz', '.tar', 
                     '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.woff', '.ttf'}
EXCLUDED_DIRS = {'.git', '.github', '__pycache__', 'node_modules', '.venv', 'venv'}

class PhraseRemover:
    def __init__(self, workspace_root, phrases):
        self.workspace_root = workspace_root
        self.phrases = phrases
        self.files_scanned = 0
        self.files_modified = 0
        self.total_removals = 0
        self.errors = []
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(exist_ok=True)
        
    def should_process_file(self, file_path):
        """Check if file should be processed"""
        # Skip binary files
        if file_path.suffix.lower() in BINARY_EXTENSIONS:
            return False
        
        # Skip large files (>10MB)
        try:
            if file_path.stat().st_size > 10 * 1024 * 1024:
                return False
        except:
            return False
        
        # Skip excluded directories
        for excluded in EXCLUDED_DIRS:
            if excluded in file_path.parts:
                return False
        
        return True
    
    def contains_phrases(self, content):
        """Check if content contains any unwanted phrases"""
        for phrase in self.phrases:
            if phrase in content:
                return True
        return False
    
    def remove_phrases(self, content):
        """Remove unwanted phrases from content"""
        modified_content = content
        removals = 0
        
        for phrase in self.phrases:
            # Count occurrences
            count = modified_content.count(phrase)
            if count > 0:
                removals += count
                # Remove all occurrences
                modified_content = modified_content.replace(phrase, "")
        
        return modified_content, removals
    
    def backup_file(self, file_path):
        """Create backup of original file"""
        try:
            relative_path = file_path.relative_to(self.workspace_root)
            backup_file = self.backup_dir / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(file_path, backup_file)
            return True
        except Exception as e:
            self.errors.append(f"Backup failed for {file_path}: {e}")
            return False
    
    def process_file(self, file_path):
        """Process single file"""
        self.files_scanned += 1
        
        try:
            # Try reading as UTF-8
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception as e:
            self.errors.append(f"Read error for {file_path}: {e}")
            return
        
        # Check if file contains unwanted phrases
        if not self.contains_phrases(content):
            return
        
        # Backup original file
        if not self.backup_file(file_path):
            return
        
        # Remove phrases
        modified_content, removals = self.remove_phrases(content)
        
        # Write modified content
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(modified_content)
            self.files_modified += 1
            self.total_removals += removals
            print(f"✓ {file_path.relative_to(self.workspace_root)}: {removals} occurrences removed")
        except Exception as e:
            self.errors.append(f"Write error for {file_path}: {e}")
    
    def scan_directory(self):
        """Recursively scan and process all files"""
        print(f"\n{'='*80}")
        print("PHRASE REMOVAL SYSTEM - BOB AI v9.0")
        print(f"{'='*80}")
        print(f"Workspace: {self.workspace_root}")
        print(f"Phrases to remove: {', '.join(self.phrases)}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Recursively process all files
        for file_path in self.workspace_root.rglob('*'):
            if file_path.is_file() and self.should_process_file(file_path):
                self.process_file(file_path)
        
        self.generate_report()
    
    def generate_report(self):
        """Generate cleanup report"""
        print(f"\n{'='*80}")
        print("CLEANUP REPORT")
        print(f"{'='*80}")
        print(f"Files scanned: {self.files_scanned}")
        print(f"Files modified: {self.files_modified}")
        print(f"Total phrase removals: {self.total_removals}")
        print(f"Backup location: {self.backup_dir}")
        
        if self.errors:
            print(f"\nErrors encountered: {len(self.errors)}")
            for error in self.errors[:10]:  # Show first 10 errors
                print(f"  - {error}")
            if len(self.errors) > 10:
                print(f"  ... and {len(self.errors) - 10} more")
        
        print(f"End time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}\n")
        
        # Save report to file
        report_file = self.workspace_root / "PHRASE_REMOVAL_REPORT.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("PHRASE REMOVAL SYSTEM - BOB AI v9.0\n")
            f.write("="*80 + "\n\n")
            f.write(f"Workspace: {self.workspace_root}\n")
            f.write(f"Phrases removed: {', '.join(self.phrases)}\n")
            f.write(f"Execution time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("CLEANUP STATISTICS:\n")
            f.write(f"  Files scanned: {self.files_scanned}\n")
            f.write(f"  Files modified: {self.files_modified}\n")
            f.write(f"  Total removals: {self.total_removals}\n")
            f.write(f"  Backup location: {self.backup_dir}\n\n")
            
            if self.errors:
                f.write(f"ERRORS: {len(self.errors)}\n")
                for error in self.errors:
                    f.write(f"  - {error}\n")
            else:
                f.write("ERRORS: None\n")
            
            f.write("\n" + "="*80 + "\n")
        
        print(f"Report saved to: {report_file}")

def main():
    """Main execution"""
    if not WORKSPACE_ROOT.exists():
        print(f"ERROR: Workspace root not found: {WORKSPACE_ROOT}")
        sys.exit(1)
    
    remover = PhraseRemover(WORKSPACE_ROOT, UNWANTED_PHRASES)
    remover.scan_directory()
    
    # Summary
    if remover.files_modified == 0:
        print("✓ No unwanted phrases found - workspace is clean!")
    else:
        print(f"✓ Cleanup complete - {remover.files_modified} files modified, "
              f"{remover.total_removals} phrase occurrences removed")
        print(f"✓ Backups saved to: {remover.backup_dir}")

if __name__ == "__main__":
    main()
