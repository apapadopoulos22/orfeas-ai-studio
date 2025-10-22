UTF-8 Normalization Enforcement
================================

This repository enforces UTF-8 encoding with Unicode NFC normalization for text files.

Components:

- Pre-commit hook using `backend.tools.encoding_fixer` in `--dry-run --check` mode.
- GitHub Actions workflow `.github/workflows/utf8-normalization.yml` that fails PRs when files need normalization.

Usage

-----

Install pre-commit locally:

1. Install pre-commit (optional):

   - `pip install pre-commit`

2. Install hooks:

   - `pre-commit install`

Run checks manually:

```powershell
python -m backend.tools.encoding_fixer --root . --dry-run --check --summary-only

```text

Apply fixes:

```powershell
python -m backend.tools.encoding_fixer --root .

```text

Options and environment toggles are documented in `md/ENCODING_FIXER_USAGE.md` and the Copilot instructions section [2.8.4] Encoder Activation Protocols.
