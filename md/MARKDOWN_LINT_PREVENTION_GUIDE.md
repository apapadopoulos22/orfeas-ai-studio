# Markdown Lint Prevention Guide

## Overview

This guide provides best practices for preventing markdownlint errors in the ORFEAS AI project documentation. Following these guidelines will ensure consistent, error-free markdown files.

## Setup: Markdownlint Configuration

### Create `.markdownlint.json` in Project Root

```json
{
  "default": true,
  "MD013": {
    "line_length": 120,
    "code_blocks": false,
    "tables": false
  },
  "MD033": false,
  "MD040": {
    "allowed_languages": [
      "python",
      "javascript",
      "typescript",
      "bash",
      "powershell",
      "json",
      "yaml",
      "sql",
      "text",
      "html",
      "css",
      "dockerfile"
    ]
  },
  "MD041": true,
  "MD026": {
    "punctuation": ".,;:!?"
  }
}

```text

### Install Markdownlint CLI

```powershell

## Global installation

npm install -g markdownlint-cli

## Or project-specific

npm install --save-dev markdownlint-cli

```text

### Add Pre-commit Hook

Create `.git/hooks/pre-commit`:

```bash

#!/bin/bash

## Run markdownlint on staged markdown files

staged_md_files=$(git diff --cached --name-only --diff-filter=ACM | grep '.md$')

if [ -n "$staged_md_files" ]; then
    markdownlint $staged_md_files
    if [ $? -ne 0 ]; then
        echo "Markdownlint found errors. Please fix them before committing."
        exit 1
    fi
fi

```text

Make it executable:

```powershell
chmod +x .git/hooks/pre-commit

```text

## Common Markdownlint Errors & Solutions

### MD041: First Line Must Be H1 Heading

### Wrong

```text

 PROJECT TITLE

## Section 1

```text

### Correct

```text

## PROJECT TITLE

 PROJECT TITLE

## Section 1

```text

**Rule:** The first line of every markdown file must be a level 1 heading (`#`).

---

### MD040: Fenced Code Blocks Need Language

### Wrong

````text
```text

def hello():
    print("Hello")

```text
````text

### Correct

`````text
```python

def hello():
    print("Hello")

```text
````**Supported Languages:**

- `python`, `javascript`, `typescript`, `java`, `csharp`, `go`, `rust`
- `bash`, `powershell`, `shell`, `sh`
- `json`, `yaml`, `toml`, `xml`
- `sql`, `html`, `css`, `scss`
- `dockerfile`, `markdown`, `text`

### For Diagrams

````text
\```text

## Use 'text' for ASCII diagrams, flowcharts, or mermaid syntax

## that you want displayed as plain text

\```

`````text

---

### MD036: Don't Use Bold/Italic as Headings

### Wrong

```text

### Task 1: Setup Database

Description of the task...

```text

### Correct

```text

#### Task 1: Setup Database

Description of the task...

```text

**Rule:** Use proper heading levels (`#`, `##`, `###`, `####`) instead of bold/italic for structure.

---

### MD026: No Trailing Punctuation in Headings

### Wrong

```text

## Installation Steps

### Objectives

### Why Choose ORFEAS

```text

### Correct

```text

## Installation Steps

### Objectives

### Why Choose ORFEAS

```text

**Rule:** Remove trailing punctuation (`:`, `.`, `!`, `?`) from headings.

---

### MD022: Headings Need Blank Lines

### Wrong

```text

## Section 1

Content starts immediately

```text

### Correct

```text

## Section 1

Content starts after blank line

```text

**Rule:** Always add blank lines before and after headings.

---

### MD032: Lists Need Blank Lines

### Wrong

```text
Some text here

- Item 1
- Item 2

  More text here

```text

### Correct

```text
Some text here

- Item 1
- Item 2

More text here

```text

**Rule:** Add blank lines before and after lists.

---

### MD013: Line Length Limit

**Configuration:** Set reasonable line length (we use 120 characters).

### Tips

- Break long lines at logical points
- Exception for code blocks and tables (configured to ignore)
- Use `<!-- markdownlint-disable MD013 -->` for specific sections if needed

---

### MD033: HTML in Markdown

### Avoid (unless necessary)

```text
<div style="color: red;">Text</div>

```text

### Prefer

```text

**Text** (use markdown emphasis)

```text

### When HTML is Required

```text
<!-- markdownlint-disable MD033 -->

<custom-component>...</custom-component>

<!-- markdownlint-enable MD033 -->

```text

## Best Practices for ORFEAS Documentation

### 1. Document Structure Template

```text

## Document Title

## Overview

Brief description of the document.

## Section 1

### Subsection 1.1

Content here.

#### Implementation Details

(Python code example here)

## Section 2

### Subsection 2.1

## Conclusion

Final thoughts.

```text

### 2. Code Block Guidelines

Always specify the language for code blocks.

### Python Example

```python

## Always specify the language

def calculate_metrics(data: Dict) -> float:
    """Calculate quality metrics"""
    return sum(data.values()) / len(data)

```text

### PowerShell Commands

```powershell

## Use powershell for Windows commands

cd backend
python main.py

```text

### Bash Commands

```bash

## Use bash for Linux/Mac commands

./start_server.sh

```text

### 3. Lists Formatting

```text

#### Ordered Lists

1. First step

2. Second step

3. Third step

#### Unordered Lists

- Main point

  - Sub-point (2 spaces indent)
  - Another sub-point

- Another main point

#### Task Lists

- [x] Completed task
- [ ] Pending task

```text

### 4. Tables

```text
| Column 1 | Column 2 | Column 3 |
| -------- | -------- | -------- |
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

```text

### 5. Links and References

```text

#### External Links

[Link text](https://example.com)

#### Internal Links

[See Installation Guide](./INSTALLATION.md)

#### Reference-style Links

This is [a link][1] and [another link][2].

[1]: https://example.com
[2]: https://example.org

```text

## VS Code Integration

### Install Extension

1. Open VS Code

2. Install "markdownlint" by David Anson

3. Extension will automatically lint markdown files

### Workspace Settings

Create `.vscode/settings.json`:

```json
{
  "markdownlint.config": {
    "default": true,
    "MD013": {
      "line_length": 120,
      "code_blocks": false
    },
    "MD033": false,
    "MD040": {
      "allowed_languages": [
        "python",
        "javascript",
        "bash",
        "powershell",
        "text"
      ]
    }
  },
  "markdownlint.run": "onSave",
  "editor.codeActionsOnSave": {
    "source.fixAll.markdownlint": true
  }
}

```text

### Keyboard Shortcuts

- `Ctrl+Shift+P` → "Markdown: Fix all markdownlint violations"
- Hover over warning → Click "Quick Fix"

## Automated Fixes

### Fix All Markdown Files

```powershell

## Fix all markdown files in md/ directory

markdownlint --fix "md/**/*.md"

## Fix specific file

markdownlint --fix md/OPTIMIZATION_ROADMAP_2025.md

## Check without fixing

markdownlint "md/**/*.md"

```text

### Create Fix Script

Create `fix_markdown_lint.ps1`:

```powershell

## Fix all markdown files in the project

Write-Host "Fixing markdown lint issues..." -ForegroundColor Cyan

$mdFiles = Get-ChildItem -Path "md" -Filter "*.md" -Recurse

foreach ($file in $mdFiles) {
    Write-Host "Processing: $($file.Name)" -ForegroundColor Yellow
    markdownlint --fix $file.FullName
}

Write-Host " All markdown files processed!" -ForegroundColor Green

```text

Run with:

```powershell
.\fix_markdown_lint.ps1

```text

## CI/CD Integration

### GitHub Actions Workflow

Create `.github/workflows/markdown-lint.yml`:

```yaml
name: Markdown Lint

on:
  pull_request:
    paths:

      - "**.md"

  push:
    branches:

      - main

    paths:

      - "**.md"

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:

      - uses: actions/checkout@v3

      - name: Setup Node.js

        uses: actions/setup-node@v3
        with:
          node-version: "18"

      - name: Install markdownlint-cli

        run: npm install -g markdownlint-cli

      - name: Run markdownlint

        run: markdownlint "md/**/*.md" --config .markdownlint.json

      - name: Comment on PR

        if: failure()
        uses: actions/github-script@v6
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: ' Markdown lint errors found. Please fix them before merging.'
            })

```text

## Quick Reference

### Essential Markdownlint Rules

| Rule  | Description                        | Fix                         |
| ----- | ---------------------------------- | --------------------------- |
| MD041 | First line must be H1              | Add `# Title` as first line |
| MD040 | Code blocks need language          | Add language after ` ``` `  |
| MD036 | Don't use bold as heading          | Use `##` instead of `**`    |
| MD026 | No trailing punctuation in heading | Remove `:` `.` `!` `?`      |
| MD022 | Headings need blank lines          | Add blank line before/after |
| MD032 | Lists need blank lines             | Add blank line before/after |
| MD013 | Line length limit                  | Break long lines            |

### Common Language Identifiers

```text
python javascript typescript java csharp go rust php swift kotlin
bash powershell shell sh zsh
json yaml toml xml html css scss sass
sql graphql
dockerfile makefile
text markdown

```text

## Additional Resources

### Official Documentation

- [Markdownlint Rules](https://github.com/DavidAnson/markdownlint/blob/main/doc/Rules.md)
- [Markdownlint CLI](https://github.com/igorshubovych/markdownlint-cli)
- [VS Code Extension](https://marketplace.visualstudio.com/items?itemName=DavidAnson.vscode-markdownlint)

### ORFEAS-Specific Guidelines

- Place all `.md` files in the `md/` directory (per ORFEAS standards)
- Use H1 (`#`) only once per document (document title)
- Use H2 (`##`) for main sections
- Use H3 (`###`) and H4 (`####`) for subsections
- Include code examples with proper language tags
- Maintain consistent formatting across all documentation

## Checklist Before Committing

- [ ] File starts with H1 heading (`# Title`)
- [ ] All code blocks have language specified
- [ ] No bold/italic used as headings
- [ ] No trailing punctuation in headings
- [ ] Blank lines before/after headings and lists
- [ ] Line length under 120 characters (except code/tables)
- [ ] Run `markdownlint --fix` before committing
- [ ] No lint errors in VS Code Problems panel
- [ ] File saved in `md/` directory (ORFEAS standard)

## Troubleshooting

### "Mermaid is not allowed" Error

**Problem:** MD040 error for mermaid diagrams

**Solution:** Use `text` language tag instead:

````text
\```text

## Mermaid diagram syntax here

## It will still render correctly in GitHub and other platforms

\```

````text

### Cannot Fix Certain Rules

Some rules cannot be auto-fixed:

- MD041 (first line heading) - manually add H1
- MD036 (emphasis as heading) - manually convert to proper heading
- MD040 (code language) - manually add language tag

### Disable Specific Rules

For specific sections:

```text
<!-- markdownlint-disable MD013 MD033 -->

Very long line or HTML content here

<!-- markdownlint-enable MD013 MD033 -->

```text

For entire file, add at top:

```text
<!-- markdownlint-disable MD013 -->

## Rest of document

```text

## Summary

### Key Takeaways

1. Always start markdown files with H1 heading

2. Specify language for all code blocks

3. Use proper heading levels, not bold/italic

4. Remove trailing punctuation from headings
5. Add blank lines around headings and lists
6. Configure markdownlint for your project
7. Use VS Code extension for real-time feedback
8. Run `markdownlint --fix` before committing
9. Follow ORFEAS documentation standards

### Prevention is Better Than Fixing

- Set up markdownlint in your editor
- Use pre-commit hooks
- Review lint warnings as you write
- Follow the ORFEAS markdown template

**Last Updated:** October 17, 2025
**Version:** 1.0
**Maintained by:** ORFEAS AI Documentation Team
