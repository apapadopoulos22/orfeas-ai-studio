#!/usr/bin/env python3
"""
Comprehensive Project Scanner for Mojibake and Linting Issues
Scans all project files for encoding problems and code quality issues
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict

# Common mojibake patterns to detect
MOJIBAKE_PATTERNS = [
    (r'â€™', "'"),  # Smart apostrophe
    (r'â€œ', '"'),  # Left double quote
    (r'â€\x9d', '"'),  # Right double quote
    (r'â€"', '—'),  # Em dash
    (r'â€"', '–'),  # En dash
    (r'Ã©', 'é'),   # e with acute
    (r'Ã¨', 'è'),   # e with grave
    (r'Ã ', 'à'),   # a with grave
    (r'Ã§', 'ç'),   # c with cedilla
    (r'âœ"', ''),  # Check mark
    (r'âœ—', ''),  # X mark
    (r'â€¢', '•'),  # Bullet
    (r'Â°', '°'),   # Degree symbol
    (r'Â©', '©'),   # Copyright
    (r'Â®', '®'),   # Registered trademark
]

# Exclude directories
EXCLUDE_DIRS = {
    'node_modules', '.venv', '.conda', '__pycache__', '.git',
    'build', 'dist', '.pytest_cache', 'htmlcov', '.mypy_cache',
    'scripts/encoding_backups', 'ARCHIVE', '.vscode'
}

# File extensions to scan
SCAN_EXTENSIONS = {
    '.py', '.ps1', '.md', '.js', '.html', '.css', '.json',
    '.yml', '.yaml', '.txt', '.sh', '.bat'
}

class ProjectScanner:
    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.mojibake_issues = defaultdict(list)
        self.linting_issues = defaultdict(list)
        self.encoding_issues = defaultdict(list)

    def should_scan_file(self, file_path: Path) -> bool:
        """Check if file should be scanned"""
        # Check if in excluded directory
        for part in file_path.parts:
            if part in EXCLUDE_DIRS:
                return False

        # Check file extension
        return file_path.suffix in SCAN_EXTENSIONS

    def detect_mojibake(self, content: str, file_path: Path) -> List[Tuple[int, str, str]]:
        """Detect mojibake patterns in content"""
        issues = []
        lines = content.split('\n')

        for line_num, line in enumerate(lines, 1):
            for pattern, correct in MOJIBAKE_PATTERNS:
                if re.search(pattern, line):
                    issues.append((
                        line_num,
                        pattern,
                        line.strip()[:100]  # First 100 chars
                    ))

        return issues

    def check_encoding(self, file_path: Path) -> List[str]:
        """Check file encoding issues"""
        issues = []

        try:
            # Try reading as UTF-8
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check for BOM
            with open(file_path, 'rb') as f:
                start = f.read(4)
                if start.startswith(b'\xef\xbb\xbf'):
                    issues.append("UTF-8 BOM detected")
                elif start.startswith(b'\xff\xfe'):
                    issues.append("UTF-16 LE BOM detected")
                elif start.startswith(b'\xfe\xff'):
                    issues.append("UTF-16 BE BOM detected")

            # Check for mixed line endings
            if '\r\n' in content and '\n' in content.replace('\r\n', ''):
                issues.append("Mixed line endings (CRLF and LF)")

        except UnicodeDecodeError:
            issues.append("Cannot decode as UTF-8")
        except Exception as e:
            issues.append(f"Read error: {str(e)}")

        return issues

    def scan_python_file(self, file_path: Path) -> List[str]:
        """Basic Python linting checks"""
        issues = []

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            lines = content.split('\n')

            for line_num, line in enumerate(lines, 1):
                # Check for common issues
                if line.rstrip() != line.rstrip('\t '):
                    if line.endswith('\t') or line.endswith(' '):
                        issues.append(f"Line {line_num}: Trailing whitespace")

                # Check line length (PEP 8 recommends 79)
                if len(line) > 120:
                    issues.append(f"Line {line_num}: Line too long ({len(line)} > 120)")

                # Check for tabs (PEP 8 recommends spaces)
                if '\t' in line:
                    issues.append(f"Line {line_num}: Tab character detected")

        except Exception as e:
            issues.append(f"Scan error: {str(e)}")

        return issues

    def scan_file(self, file_path: Path):
        """Scan a single file for all issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()

            # Check for mojibake
            mojibake = self.detect_mojibake(content, file_path)
            if mojibake:
                self.mojibake_issues[str(file_path)] = mojibake

            # Check encoding
            encoding_issues = self.check_encoding(file_path)
            if encoding_issues:
                self.encoding_issues[str(file_path)] = encoding_issues

            # Python-specific checks
            if file_path.suffix == '.py':
                lint_issues = self.scan_python_file(file_path)
                if lint_issues:
                    self.linting_issues[str(file_path)] = lint_issues[:10]  # First 10

        except Exception as e:
            self.encoding_issues[str(file_path)] = [f"Scan failed: {str(e)}"]

    def scan_project(self):
        """Scan entire project"""
        print(f"Scanning project: {self.root_dir}")
        print(f"Excluded directories: {', '.join(EXCLUDE_DIRS)}")
        print(f"Scanning extensions: {', '.join(SCAN_EXTENSIONS)}")
        print()

        scanned_count = 0
        for root, dirs, files in os.walk(self.root_dir):
            # Remove excluded directories
            dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

            for file in files:
                file_path = Path(root) / file

                if self.should_scan_file(file_path):
                    self.scan_file(file_path)
                    scanned_count += 1

                    if scanned_count % 500 == 0:
                        print(f"Scanned {scanned_count} files...")

        print(f"\nTotal files scanned: {scanned_count}")

    def generate_report(self) -> str:
        """Generate comprehensive report"""
        report = []
        report.append("=" * 80)
        report.append("PROJECT SCAN REPORT - MOJIBAKE & LINTING ISSUES")
        report.append("=" * 80)
        report.append("")

        # Summary
        report.append("SUMMARY:")
        report.append(f"  Files with mojibake issues: {len(self.mojibake_issues)}")
        report.append(f"  Files with encoding issues: {len(self.encoding_issues)}")
        report.append(f"  Files with linting issues: {len(self.linting_issues)}")
        report.append("")

        # Mojibake Issues
        if self.mojibake_issues:
            report.append("=" * 80)
            report.append("MOJIBAKE ISSUES:")
            report.append("=" * 80)
            report.append("")

            for file_path, issues in sorted(self.mojibake_issues.items())[:20]:  # First 20
                report.append(f"FILE: {file_path}")
                for line_num, pattern, line_content in issues[:5]:  # First 5 per file
                    report.append(f"  Line {line_num}: Pattern '{pattern}' found")
                    report.append(f"    Content: {line_content}")
                if len(issues) > 5:
                    report.append(f"  ... and {len(issues) - 5} more issues")
                report.append("")

        # Encoding Issues
        if self.encoding_issues:
            report.append("=" * 80)
            report.append("ENCODING ISSUES:")
            report.append("=" * 80)
            report.append("")

            for file_path, issues in sorted(self.encoding_issues.items())[:20]:  # First 20
                report.append(f"FILE: {file_path}")
                for issue in issues:
                    report.append(f"  - {issue}")
                report.append("")

        # Linting Issues
        if self.linting_issues:
            report.append("=" * 80)
            report.append("LINTING ISSUES (Python files):")
            report.append("=" * 80)
            report.append("")

            for file_path, issues in sorted(self.linting_issues.items())[:10]:  # First 10
                report.append(f"FILE: {file_path}")
                for issue in issues[:5]:  # First 5 per file
                    report.append(f"  - {issue}")
                if len(issues) > 5:
                    report.append(f"  ... and {len(issues) - 5} more issues")
                report.append("")

        # Statistics by file type
        report.append("=" * 80)
        report.append("STATISTICS BY FILE TYPE:")
        report.append("=" * 80)
        report.append("")

        file_types = defaultdict(lambda: {'mojibake': 0, 'encoding': 0, 'linting': 0})

        for file_path in self.mojibake_issues.keys():
            ext = Path(file_path).suffix
            file_types[ext]['mojibake'] += 1

        for file_path in self.encoding_issues.keys():
            ext = Path(file_path).suffix
            file_types[ext]['encoding'] += 1

        for file_path in self.linting_issues.keys():
            ext = Path(file_path).suffix
            file_types[ext]['linting'] += 1

        for ext, counts in sorted(file_types.items()):
            report.append(f"{ext}:")
            report.append(f"  Mojibake: {counts['mojibake']} files")
            report.append(f"  Encoding: {counts['encoding']} files")
            report.append(f"  Linting:  {counts['linting']} files")
            report.append("")

        return "\n".join(report)

    def save_json_report(self, output_path: str):
        """Save detailed JSON report"""
        report = {
            'summary': {
                'mojibake_files': len(self.mojibake_issues),
                'encoding_files': len(self.encoding_issues),
                'linting_files': len(self.linting_issues),
            },
            'mojibake_issues': {
                k: [{'line': i[0], 'pattern': i[1], 'content': i[2]} for i in v]
                for k, v in self.mojibake_issues.items()
            },
            'encoding_issues': dict(self.encoding_issues),
            'linting_issues': dict(self.linting_issues),
        }

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\nDetailed JSON report saved to: {output_path}")


if __name__ == '__main__':
    scanner = ProjectScanner('.')

    print("Starting comprehensive project scan...")
    print()

    scanner.scan_project()

    # Generate and print report
    report = scanner.generate_report()
    print(report)

    # Save detailed JSON report
    scanner.save_json_report('project_scan_report.json')

    # Save text report
    with open('project_scan_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    print("Text report saved to: project_scan_report.txt")
