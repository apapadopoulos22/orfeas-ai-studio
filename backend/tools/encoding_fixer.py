"""
Repository-wide encoding fixer CLI.

Features:
- Detects file encodings using EncodingManager and converts to UTF-8.
- Unicode-normalizes content (default NFC).
- Optional ftfy pass to repair mojibake (if ftfy installed and enabled).
- Dry-run mode prints intended changes without writing.
- Include/Exclude glob patterns, with a safe default exclude set.
- Skips binary files and very large files by default.

Usage (PowerShell):
  # Dry run
  python -m backend.tools.encoding_fixer --dry-run --root .

  # Convert in-place, using defaults
  python -m backend.tools.encoding_fixer --root .

  # Limit to specific folders and patterns
  python -m backend.tools.encoding_fixer --root . --include "backend/**/*.py" --include "docs/**/*.md"

  # Exclude heavy dirs
  python -m backend.tools.encoding_fixer --root . --exclude "Hunyuan3D-2.1/**" --exclude "**/.git/**"
"""

from __future__ import annotations

import argparse
import fnmatch
import os
import sys
from pathlib import Path
from typing import Iterable, Iterator, List, Optional, Set, Tuple

try:
    # Optional mojibake fixer
    import ftfy  # type: ignore
except Exception:  # pragma: no cover
    ftfy = None  # type: ignore

try:
    # Local import (module path when invoked as module)
    from ..encoding_layer import get_encoding_manager, init_multi_encoding_layers
except Exception:  # pragma: no cover
    # Fallback to runtime path resolution
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from backend.encoding_layer import get_encoding_manager, init_multi_encoding_layers  # type: ignore


# Reasonable default excludes to avoid scanning huge or binary trees
DEFAULT_EXCLUDES: Tuple[str, ...] = (
    ".git/**",
    ".github/**",
    ".venv/**",
    "venv/**",
    ".conda/**",
    ".vscode/**",
    ".idea/**",
    ".cache/**",
    ".pytest_cache/**",
    "coverage/**",
    "dist/**",
    "build/**",
    "node_modules/**",
    "**/node_modules/**",
    "**/__pycache__/**",
    "docs/node_modules/**",
    "docs/_build/**",
    "docs/build/**",
    "frontend/.next/**",
    "frontend/dist/**",
    "frontend/build/**",
    "**/logs/**",
    "logs/**",
    "scripts/encoding_backups/**",
    "**/*.png",
    "**/*.jpg",
    "**/*.jpeg",
    "**/*.gif",
    "**/*.bmp",
    "**/*.tiff",
    "**/*.webp",
    "**/*.ico",
    "**/*.bin",
    "**/*.exe",
    "**/*.dll",
    "**/*.whl",
    "**/*.pdf",
    "**/*.zip",
    "**/*.7z",
    "**/*.gz",
    "**/*.tar",
    "**/*.xz",
    "**/*.mp4",
    "**/*.mp3",
    "**/*.wav",
    "**/*.ogg",
    "**/*.obj",
    "**/*.stl",
    "**/*.glb",
    "**/*.gltf",
    "Hunyuan3D-2.1/**",
    "Hunyuan3D-2.1-SOURCE/**",
    "models/**",
    "outputs/**",
)


TEXT_EXTENSIONS: Tuple[str, ...] = (
    ".py",
    ".js",
    ".ts",
    ".json",
    ".yml",
    ".yaml",
    ".toml",
    ".ini",
    ".cfg",
    ".txt",
    ".md",
    ".html",
    ".css",
    ".svg",
    ".env",
    ".ps1",
    ".bat",
    ".sh",
)


def is_probably_text_file(path: Path, size_limit_mb: int = 10) -> bool:
    """Heuristic to treat path as text. Uses extension and size limit."""
    if not path.is_file():
        return False
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        return False
    try:
        if path.stat().st_size > size_limit_mb * 1024 * 1024:
            return False
    except OSError:
        return False
    return True


def match_any(patterns: Iterable[str], rel_path: str) -> bool:
    for pat in patterns:
        if fnmatch.fnmatch(rel_path, pat):
            return True
    return False


def iter_files(root: Path, includes: List[str], excludes: List[str]) -> Iterator[Path]:
    for p in root.rglob("*"):
        try:
            rel_path = p.relative_to(root).as_posix()
        except Exception:
            # Fallback to absolute if relative fails; still allows matching
            rel_path = p.as_posix()

        # Apply excludes first (union of DEFAULT_EXCLUDES and user excludes)
        if match_any(DEFAULT_EXCLUDES + tuple(excludes), rel_path):
            continue
        if includes:
            if not match_any(includes, rel_path):
                continue
        if is_probably_text_file(p):
            yield p


def fix_file(path: Path, dry_run: bool = True, enable_ftfy: bool = False) -> Tuple[bool, str]:
    em = get_encoding_manager()
    info = em.detect_encoding_with_fallback(str(path))
    enc = info.get("encoding", "utf-8")
    bom = info.get("bom_present", False)

    try:
        # Read with detected encoding; tolerate replacement to avoid crashes
        with path.open("r", encoding=enc, errors=os.getenv("ENCODING_ERROR_HANDLING", "replace")) as f:
            raw = f.read()

        normalized = em.normalize_unicode(raw)
        repaired = normalized
        repair_note = ""

        if enable_ftfy and ftfy is not None:
            repaired = ftfy.fix_text(normalized)
            if repaired != normalized:
                repair_note = " +ftfy"

        # If BOM was detected, strip leading U+FEFF from text before writing
        if bom and repaired.startswith("\ufeff"):
            repaired = repaired.lstrip("\ufeff")

        enc_lower = enc.lower()
        if repaired == raw and not bom and enc_lower in {"utf-8", "utf_8", "utf8", "ascii"}:
            return False, f"SKIP {path} (utf-8 normalized, no change)"

        if dry_run:
            return True, f"DRY {path} [{enc}{' BOM' if bom else ''}] -> utf-8 +NFC{repair_note}"

        # Preserve existing newline style by inspecting the original file
        newline = None
        if "\r\n" in raw and "\n" in raw:
            newline = "\n"  # mixed; normalize to LF
        elif "\r\n" in raw:
            newline = "\r\n"
        else:
            newline = "\n"

        with path.open("w", encoding="utf-8", newline=newline) as fw:
            fw.write(repaired)

        return True, f"WROTE {path} [{enc}{' BOM' if bom else ''}] -> utf-8 +NFC{repair_note}"

    except Exception as e:
        return False, f"ERROR {path}: {e}"


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Repo-wide encoding fixer (UTF-8 + normalization)")
    parser.add_argument("--root", default=".", help="Root directory to scan (default: .)")
    parser.add_argument("--include", action="append", default=[], help="Glob to include (repeatable)")
    parser.add_argument("--exclude", action="append", default=[], help="Glob to exclude (repeatable)")
    parser.add_argument("--dry-run", action="store_true", help="Only report changes; do not write")
    parser.add_argument("--check", action="store_true", help="Exit non-zero if changes would be made (use with --dry-run)")
    parser.add_argument(
        "--summary-only",
        action="store_true",
        help="Print only the final summary (suppresses per-file logs)",
    )
    parser.add_argument("--ftfy", action="store_true", help="Enable ftfy-based mojibake repair if available")
    parser.add_argument("--limit", type=int, default=0, help="Process at most N files (0 = no limit)")

    args = parser.parse_args(argv)

    init_multi_encoding_layers()

    root = Path(args.root).resolve()
    includes = args.include or []
    excludes = args.exclude or []
    processed = 0
    changed = 0
    errors = 0

    for path in iter_files(root, includes, excludes):
        ok, msg = fix_file(path, dry_run=args.dry_run, enable_ftfy=args.ftfy)
        if not args.summary_only:
            print(msg)
        processed += 1
        if ok:
            if msg.startswith("ERROR"):
                errors += 1
            elif not msg.startswith("SKIP"):
                changed += 1
        else:
            if msg.startswith("ERROR"):
                errors += 1

        if args.limit and processed >= args.limit:
            break

    print(f"\nSummary: processed={processed}, changed={changed}, errors={errors}, dry_run={args.dry_run}")

    # Exit code policy:
    # - errors > 0 => 1
    # - --check with --dry-run and changes > 0 => 2 (signals formatting/normalization needed)
    # - otherwise 0
    if errors > 0:
        return 1
    if args.check and args.dry_run and changed > 0:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
