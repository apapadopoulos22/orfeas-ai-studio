# ORFEAS Encoding Fixer CLI

A safe, repository-wide encoding fixer that detects encodings, converts text files to UTF-8, normalizes Unicode (NFC), and optionally repairs mojibake with ftfy.

- Location: `backend/tools/encoding_fixer.py`
- Defaults: dry-run OFF, ftfy OFF, safe default excludes (e.g., .git, node_modules, models, outputs, images, binaries)
- Uses: `EncodingManager` and activation protocols defined in Copilot instructions [2.8.4]

## Quick Start

- Dry run first (recommended):

  - PowerShell
    - `python -m backend.tools.encoding_fixer --dry-run --root .`

- Convert in place:

  - `python -m backend.tools.encoding_fixer --root .`

- Enable mojibake repair (ftfy):

  - `python -m backend.tools.encoding_fixer --root . --ftfy`

- Only process certain folders:

  - `python -m backend.tools.encoding_fixer --root . --include "backend/**/*.py" --include "docs/**/*.md"`

- Exclude additional paths:

  - `python -m backend.tools.encoding_fixer --root . --exclude "Hunyuan3D-2.1/**" --exclude "**/temp/**"`

- Limit number of files (smoke test):

  - `python -m backend.tools.encoding_fixer --root . --dry-run --limit 25`

## What it does

- Reads each candidate file using detected encoding (BOM > autodetectors > fallback chain).
- Normalizes Unicode to NFC.
- Optionally applies ftfy to fix double-encoding and mojibake patterns.
- Writes back as UTF-8 with LF endings.
- Skips files that are already UTF-8 and unchanged.

## Safety

- Always perform a dry run first.
- The tool skips large files (>10MB), binary formats, models, and heavy directories by default.
- Consider committing your work or making a backup before running in write mode.

## Environment

- Honors the following environment variables from the platform:

  - `ENABLE_MULTI_ENCODING`, `ENCODING_AUTO_DETECTION`, `ENCODING_FALLBACK_CHAIN`
  - `UNICODE_NORMALIZATION`, `BOM_DETECTION`, `ENCODING_ERROR_HANDLING`

## Troubleshooting

- If autodetection is noisy, try setting:

  - `$env:ENCODING_AUTO_DETECTION = "false"`
  - `$env:ENCODING_FALLBACK_CHAIN = "utf-8,latin-1,cp1252,ascii"`

- If you see UnicodeDecodeError on a file, re-run with `--dry-run` and inspect the reported detected encoding.
- ftfy is optional; install via `pip install ftfy` if needed.

## Notes

- This tool complements the request normalization hooks in `backend/main.py` and the activation protocols in `.github/copilot-instructions.md`.
- Extend `TEXT_EXTENSIONS` in `encoding_fixer.py` as needed for additional text types.
