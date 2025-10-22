# ORFEAS Markdown Style Guide

This guide defines how we write and validate Markdown in this repository.

## # # Scope and file placement

- All project-authored Markdown lives under `md/`.
- Third-party or generated docs may exist elsewhere but are excluded from repo-wide lint runs.

## # # Encoding and portability

- Always save files as UTF-8 (no BOM). Avoid copying special glyphs from unknown encodings.
- Prefer plain ASCII for decorative elements. If you include ASCII art, wrap it in a fenced code block with `text` language.

## # # Headings

- Exactly one H1 (`#`) per document (the title).
- Use `##`, `###`, … for sections and subsections.
- Do not use bold text as a heading substitute (violates MD036). Convert `**Title**` → `## Title`.
- Avoid decorative banners as `#` headings. Use comments or plain text instead.

## # # Code fences

- Every code block must declare a language (MD040).

  - Real code: `python`, `bash`, `powershell`, `json`, etc.
  - Non-code / ASCII art / logs: use `text`.

- Prefer fenced blocks (```), not indented blocks (MD046).

## # # Spacing and structure

- Avoid multiple consecutive blank lines (MD012).
- Use `-` for unordered lists (MD004).
- Inline HTML is allowed if necessary (MD033 disabled), but prefer Markdown where possible.
- Bare URLs are allowed (MD034 disabled); use autolink or link syntax when convenient.

## # # Exceptions and leniencies

- Line length (MD013) is disabled to keep content readable in tables and code.
- Duplicate headings are limited to within sibling sections only (MD024 `siblings_only: true`).

## # # Linting and hooks

- Configuration: see `.markdownlint.json` at the repo root.
- Exclusions: see `.markdownlintignore`.
- Local lint (ad-hoc):

```bash
npx markdownlint-cli "md/**/*.md"

```text

- Auto-fix common issues:

```bash
npx markdownlint-cli --fix "md/**/*.md"

```text

- Git pre-commit hook (staged files only):

  - Run once to enable hooks path:

```powershell
powershell -ExecutionPolicy Bypass -File .\SETUP_GIT_HOOKS.ps1

```text

The hook will auto-fix staged Markdown and block commits if violations remain.

## # # Common patterns (do / avoid)

- Do: one H1 at top, section headings with `##`/`###`.
- Do: specify languages for fences; use `text` for non-code.
- Avoid: decorative banners as `#` headings; use comments or `text` fences.
- Avoid: `**Section Title**` as a heading.

## # # Troubleshooting

- If you see garbled characters like `â`, the file likely has encoding issues. Re-save as UTF-8 and replace special glyphs.
- If `npx` is not found on Windows, install Node.js LTS or `markdownlint-cli` globally:

```powershell
npm install -g markdownlint-cli

```text
