"""Fix markdown lint issues in MARKDOWN_LINT_PREVENTION_GUIDE.md"""
import re

file_path = r"c:\Users\johng\Documents\oscar\md\MARKDOWN_LINT_PREVENTION_GUIDE.md"

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace all ```markdown with ```text
content = re.sub(r'```markdown', '```text', content)

# Replace all ````markdown with ````text
content = re.sub(r'````markdown', '````text', content)

# Replace all `````markdown with `````text
content = re.sub(r'`````markdown', '`````text', content)

# Fix the heading level issue - add H3 before H4
# Find the section with #### Python Example and add H3 above it
content = re.sub(
    r'(### 2\. Code Block Guidelines\n\n)(```text\n#### Python Example)',
    r'\1### Examples\n\n\2',
    content
)

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f" Fixed markdown lint issues in {file_path}")
print("  - Replaced 'markdown' language tag with 'text'")
print("  - Fixed heading hierarchy")
