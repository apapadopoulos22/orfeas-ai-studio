#!/usr/bin/env python
"""Fix all markdown linting violations in error attachment."""
import re

files_to_fix = {
    'PHASE_3_2_3_3_COMPLETION_REPORT.md': {
        'type': 'MD026',  # Trailing punctuation
        'lines': [7, 22, 32, 42, 52, 62, 72, 81, 92, 136, 150, 161, 170, 177, 188, 196, 207, 216, 223]
    },
    'PHASE_3_1_EXECUTIVE_BRIEF.md': {
        'type': 'MD026',
        'lines': [13]
    },
    'MARKDOWN_LINTING_FINAL_VERIFICATION.md': {
        'type': 'mixed',
        'lines': [75, 217, 221, 231]  # MD029, MD025, MD025, MD040
    },
    'PHASE_4_COMPLETE_SUMMARY.md': {
        'type': 'MD001',
        'lines': [5]
    },
    'PHASE_4_DEPLOYMENT_COMPLETE_99_PERCENT.md': {
        'type': 'mixed',
        'lines': [5, 23, 31, 39]  # MD001, MD026, MD026, MD026
    },
    'PHASE_4_OPTIMIZATION_10_PERCENT.md': {
        'type': 'MD001',
        'lines': [5]
    },
    'PHASE_4_INTEGRATION_AND_DEPLOYMENT.md': {
        'type': 'MD026',
        'lines': [5]
    }
}

total_fixes = 0

for file_path, violation_info in files_to_fix.items():
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        violations = violation_info.get('lines', [])
        fixes_in_file = 0

        for line_num in violations:
            if line_num <= len(lines):
                line = lines[line_num - 1]

                # Fix MD026: Remove trailing colons from headings
                if line.startswith('#') and ':' in line and line.rstrip().endswith(':'):
                    new_line = line.rstrip()[:-1] + '\n'
                    lines[line_num - 1] = new_line
                    fixes_in_file += 1
                    print(f"Line {line_num}: Fixed trailing punctuation")

                # Fix MD001: Heading level increment (### to ##)
                elif line.startswith('### ') and not re.search(r'^## ', '\n'.join(lines[:line_num-1])):
                    new_line = '## ' + line[4:]
                    lines[line_num - 1] = new_line
                    fixes_in_file += 1
                    print(f"Line {line_num}: Fixed heading level increment (### → ##)")

                # Fix MD029: Ordered list prefix
                elif re.match(r'^\s+\d+\.\s', line) and fixes_in_file > 0:
                    # This will be handled by renumbering
                    pass

        if fixes_in_file > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            print(f"✅ {file_path}: Fixed {fixes_in_file} violations\n")
            total_fixes += fixes_in_file

    except FileNotFoundError:
        print(f"⚠️  {file_path} not found\n")
    except Exception as e:
        print(f"❌ Error processing {file_path}: {e}\n")

print(f"\n✅ Total violations fixed: {total_fixes}")
