# MARKDOWN AUTOMATION - QUICK REFERENCE

Quick access guide for ORFEAS AI markdown linting automation

## Three-Tier Defense

| Level | Tool | Action | When |
|-------|------|--------|------|
| **1** | VS Code | Auto-fix on save | Real-time editing |
| **2** | Git Hook | Block bad commits | `git commit` |
| **3** | GitHub Actions | Block PR merge | Push/PR to main |

## Quick Commands

### Lint Single File

```powershell
markdownlint README.md

```text

### Fix Single File

```powershell
markdownlint --fix README.md

```text

### Batch Fix All Files

```powershell
.\fix_markdown_lint.ps1

```text

### Test Git Hook

```powershell
git add test.md
git commit -m "test: verify lint hook"

## Hook runs automatically

```text

### Bypass Hook (Emergency)

```powershell
git commit --no-verify

```text

## Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.markdownlint.json` | Project rules | Root directory |
| `.vscode/settings.json` | VS Code config | `.vscode/` directory |
| `.git/hooks/pre-commit` | Git hook | `.git/hooks/` directory |
| `.github/workflows/markdown-lint.yml` | CI/CD | `.github/workflows/` |

## Common Rules

| Rule | Description | Setting |
|------|-------------|---------|
| MD041 | H1 first line required |  Enabled |
| MD040 | Code block language required |  Enabled (21 languages) |
| MD036 | No bold as headings |  Enabled |
| MD013 | Line length limit |  Disabled |
| MD033 | Allow HTML |  Allowed |

## Quick Fixes

### Problem: Auto-fix not working

```powershell

## Reload VS Code

Ctrl+Shift+P → "Reload Window"

```text

### Problem: Git hook not running

```bash

## Make executable (Git Bash)

chmod +x .git/hooks/pre-commit

```text

### Problem: CLI not found

```powershell

## Reinstall

npm install -g markdownlint-cli

```text

## Documentation

- **Full Guide:** `md/MARKDOWN_AUTOMATION_SETUP_COMPLETE.md`
- **Prevention Guide:** `md/MARKDOWN_LINT_PREVENTION_GUIDE.md`
- **Roadmap:** `md/OPTIMIZATION_ROADMAP_2025.md`

## Validation Checklist

- [ ] VS Code extension installed (v0.60.0)
- [ ] markdownlint-cli installed (v0.45.0)
- [ ] Auto-fix on save working
- [ ] Pre-commit hook blocking bad commits
- [ ] CI/CD workflow ready
- [ ] All production docs have 0 errors

## Status

**Current Status:**  FULLY OPERATIONAL

All automation components installed, configured, and tested successfully.

---

**Last Updated:** 2025-01-24
**Version:** 1.0
**Maintainer:** ORFEAS AI Development Team
