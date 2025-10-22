#!/usr/bin/env python3
"""
Fix common Markdown offenses in-place:
 - Keep first H1; demote subsequent H1s to H2 (MD025)
 - Ensure first line is an H1; inject file-based title if missing (MD041)
 - Label unlabeled fenced code blocks as `text` (MD040)
 - Relabel disallowed fenced languages (e.g., `markdown`, `md`, `cmd`, `http`, `promql`) to `text` (MD040)
 - Collapse multiple blank lines to one (MD012)
 - Promote bold-only lines to proper headings (MD036)
 - Strip trailing punctuation from headings (MD026)
 - Normalize heading level increments to avoid jumps (MD001)
 - De-duplicate repeated headings by suffixing (MD024)
 - Enforce blank lines around headings (MD022)
 - Renumber ordered lists sequentially per nesting level (MD029)
 - Trim spaces just inside bold markers like ** text ** → **text** (MD037)
 - Normalize to UTF-8 with best-effort decoding and NFC normalization

Usage:
    python scripts/fix_markdown_offenders.py <file1.md> [file2.md ...]

Backups:
    Creates a sibling backup file with ".bak" extension before writing.
"""
from __future__ import annotations

import re
import sys
import shutil
from pathlib import Path
from typing import List, Tuple
import json

import unicodedata


def read_text_best_effort(p: Path) -> Tuple[str, str]:
    """Read file bytes and decode with best-effort to UTF-8.

    Returns: (text, used_encoding)
    """
    raw = p.read_bytes()
    tried = []

    # Try straightforward UTF-8 family first
    for enc in ("utf-8", "utf-8-sig"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError as e:
            tried.append((enc, str(e)))

    # Optional: charset-normalizer if installed
    try:
        from charset_normalizer import from_bytes  # type: ignore

        best = from_bytes(raw).best()
        if best and best.encoding:
            return str(best), str(best.encoding)
    except Exception:
        pass

    # Fallbacks commonly helpful for mojibake
    for enc in ("cp1252", "latin-1"):
        try:
            return raw.decode(enc), enc
        except UnicodeDecodeError as e:
            tried.append((enc, str(e)))

    # Last resort: replace errors
    return raw.decode("utf-8", errors="replace"), "utf-8-replace"


H1_RE = re.compile(r"^(#) +(.+?)\s*$")
BOLD_ONLY_RE = re.compile(r"^\s*\*\*(.+?)\*\*\s*$")
# Flexible fence open matcher: captures delimiter of backticks or tildes (length >= 3)
FENCE_OPEN_RE = re.compile(r"^(?P<delim>`{3,}|~{3,})\s*(?P<lang>[a-zA-Z0-9_+\.-]+)?\s*$")
# Legacy simple patterns (kept for compatibility in some passes)
FENCE_RE = re.compile(r"^```(\s*)$")  # exactly ``` optionally with spaces
FENCE_WITH_LANG_RE = re.compile(r"^```\s*([a-zA-Z0-9_+-]+)\s*$")

# Generic heading pattern + helpers for advanced fixes
HEAD_RE = re.compile(r"^(?P<hashes>#{1,6})\s+(?P<text>.+?)\s*$")
TRAIL_PUNCT_RE = re.compile(r"[\s\t]*[\:\.;,!\?]+$")

# Patterns for ordered list items and emphasis trimming
OL_ITEM_RE = re.compile(r"^(?P<indent>\s*)(?P<num>\d+)\.(?P<rest>\s+.*)$")
# Unordered list item pattern for MD007/MD032 fixes
UL_ITEM_RE = re.compile(r"^(?P<indent>\s*)(?P<bullet>[\-\+\*])\s+(?P<rest>.+)$")
BOLD_SPAN_RE = re.compile(r"(\*\*)(.+?)(\*\*)")
UNDERSCORE_BOLD_SPAN_RE = re.compile(r"(__)(.+?)(__)")


def fix_markdown(text: str, file_title: str | None = None) -> Tuple[str, dict]:
    lines = text.splitlines()

    inside_fence = False
    fence_open_line = -1
    fence_delim: str | None = None  # tracks the exact delimiter used for closing
    first_h1_seen = False

    demoted_h1 = 0
    labeled_fences = 0
    blanks_collapsed = 0
    bold_promoted = 0
    fixed_heading_punct = 0
    normalized_heading_level = 0
    dedup_headings = 0
    fence_lang_relabelled = 0
    ol_renumbered = 0
    ul_indent_normalized = 0
    added_blank_lines_lists = 0
    fixed_atx_space = 0
    post_demoted_h1 = 0
    added_blank_lines_headings = 0
    inserted_top_h1 = 0

    # Track heading level progression and duplicates
    last_heading_level = 0
    seen_headings: dict[tuple[int, str], int] = {}

    fixed_lines: List[str] = []

    i = 0
    while i < len(lines):
        line = lines[i]

        # Track code fences; only process headings outside fences
        if not inside_fence:
            # Start of fence (supports ``` or ~~~ with length >=3) and optional language
            m_fence_open = FENCE_OPEN_RE.match(line)
            if m_fence_open:
                fence_delim = m_fence_open.group("delim")
                lang = m_fence_open.group("lang")
                # If no language specified, label as text (MD040)
                if not lang or not lang.strip():
                    line = f"{fence_delim}text"
                    labeled_fences += 1
                else:
                    l = lang.strip().lower()
                    # Relabel known disallowed/noisy languages to `text` (MD040)
                    if l in {"markdown", "md", "cmd", "http", "https", "promql", "txt", "batch", "nginx", "hcl"}:
                        line = f"{fence_delim}text"
                        fence_lang_relabelled += 1
                    else:
                        # keep original language but normalize spacing
                        line = f"{fence_delim}{l}"
                inside_fence = True
                fence_open_line = i
                fixed_lines.append(line)
                i += 1
                continue

            # Promote bold-only line to heading level-2 (avoid inside fences)
            m_bold = BOLD_ONLY_RE.match(line)
            if m_bold:
                content = m_bold.group(1).strip()
                line = f"## {content}"
                bold_promoted += 1

            # MD018: Ensure a space after ATX hashes for headings like '##Heading' -> '## Heading'
            if re.match(r"^(#{1,6})(?=\S)", line):
                # Insert a single space after the hash sequence
                line = re.sub(r"^(#{1,6})(?=\S)", lambda m: m.group(1) + " ", line)
                fixed_atx_space += 1

            # MD037: trim spaces just inside bold markers (** text ** -> **text**)
            def _trim_bold_spans(s: str) -> str:
                def _replacer(m: re.Match) -> str:
                    return f"**{m.group(2).strip()}**"
                def _replacer_us(m: re.Match) -> str:
                    return f"__{m.group(2).strip()}__"
                s2 = BOLD_SPAN_RE.sub(_replacer, s)
                s2 = UNDERSCORE_BOLD_SPAN_RE.sub(_replacer_us, s2)
                return s2
            new_line = _trim_bold_spans(line)
            if new_line != line:
                line = new_line

            # Demote subsequent H1s
            m = H1_RE.match(line)
            if m:
                if not first_h1_seen:
                    first_h1_seen = True
                else:
                    # Convert single # Heading → ## Heading
                    line = f"## {m.group(2).strip()}"
                    demoted_h1 += 1

            # Advanced heading processing: MD026, MD001, MD024
            m_head = HEAD_RE.match(line)
            if m_head:
                hashes = m_head.group("hashes")
                text_part = m_head.group("text").strip()

                # MD026: strip trailing punctuation
                new_text = TRAIL_PUNCT_RE.sub("", text_part)
                if new_text != text_part:
                    fixed_heading_punct += 1
                    text_part = new_text

                # MD001: normalize level increments (avoid jumps)
                level = len(hashes)
                if last_heading_level > 0 and level > last_heading_level + 1:
                    level = last_heading_level + 1
                    normalized_heading_level += 1
                # Update last seen level
                last_heading_level = level

                # MD024: deduplicate same-level headings by suffixing
                key = (level, text_part.lower())
                count = seen_headings.get(key, 0)
                if count:
                    dedup_headings += 1
                    text_part = f"{text_part} ({count + 1})"
                seen_headings[key] = count + 1

                line = f"{'#' * level} {text_part}"

            fixed_lines.append(line)
        else:
            # Inside fence: leave lines as-is until closing fence matching the opening delimiter
            if fence_delim is not None and line.strip() == fence_delim:
                inside_fence = False
                fence_delim = None
            fixed_lines.append(line)

        i += 1

    # Ensure there is a top-level heading at the beginning (MD041)
    def _derive_title_from_first_content(ls: List[str]) -> str:
        # Prefer filename-provided title
        if file_title:
            return file_title
        # Fallback to first non-empty line text stripped of non-word chars
        for L in ls:
            if L.strip():
                t = re.sub(r"[`#*_~>\-]+", " ", L).strip()
                return t if t else "Document"
        return "Document"

    # Insert top H1 if first non-empty line isn't a heading
    first_non_empty_idx = next((idx for idx, ln in enumerate(fixed_lines) if ln.strip() != ""), None)
    if first_non_empty_idx is None:
        # Empty file; insert a default heading
        fixed_lines = [f"# {file_title or 'Document'}", ""]
        inserted_top_h1 += 1
    else:
        if not HEAD_RE.match(fixed_lines[first_non_empty_idx]):
            title = _derive_title_from_first_content(fixed_lines)
            fixed_lines = [f"# {title}", ""] + fixed_lines
            inserted_top_h1 += 1

    # Pass: Renumber ordered lists (MD029) outside fences
    final_lines_ol: List[str] = []
    inside_fence = False
    fence_delim = None
    # Stack of (indent_len, next_number)
    ol_stack: List[Tuple[int, int]] = []
    for idx, ln in enumerate(fixed_lines):
        m_open = (not inside_fence) and FENCE_OPEN_RE.match(ln)
        if m_open:
            inside_fence = True
            fence_delim = m_open.group("delim")
            final_lines_ol.append(ln)
            continue
        if inside_fence and fence_delim is not None and ln.strip() == fence_delim:
            inside_fence = False
            fence_delim = None
            final_lines_ol.append(ln)
            continue

        if not inside_fence:
            m_ol = OL_ITEM_RE.match(ln)
            if m_ol:
                indent = len(m_ol.group("indent"))
                # Adjust stack based on indent
                while ol_stack and indent < ol_stack[-1][0]:
                    ol_stack.pop()
                if not ol_stack or indent > ol_stack[-1][0]:
                    ol_stack.append((indent, 1))
                # Use current expected number
                current_indent, expected = ol_stack[-1]
                # Replace number if different
                old_num = int(m_ol.group("num"))
                if old_num != expected:
                    ln = f"{m_ol.group('indent')}{expected}.{m_ol.group('rest')}"
                    ol_renumbered += 1
                # Increment expected for this level
                ol_stack[-1] = (current_indent, expected + 1)
            else:
                # Reset on blank line
                if ln.strip() == "":
                    ol_stack.clear()
        final_lines_ol.append(ln)

    # Pass: Ensure blank lines around headings (MD022) and lists (MD032), and normalize UL indent (MD007)
    final_lines_bl: List[str] = []
    inside_fence = False
    fence_delim = None
    # Helper to check if a line is a list item (UL or OL)
    def _is_list_item(s: str) -> bool:
        return bool(UL_ITEM_RE.match(s) or OL_ITEM_RE.match(s))

    idx = 0
    while idx < len(final_lines_ol):
        ln = final_lines_ol[idx]
        m_open = (not inside_fence) and FENCE_OPEN_RE.match(ln)
        if m_open:
            inside_fence = True
            fence_delim = m_open.group("delim")
            final_lines_bl.append(ln)
            idx += 1
            continue
        if inside_fence and fence_delim is not None and ln.strip() == fence_delim:
            inside_fence = False
            fence_delim = None
            final_lines_bl.append(ln)
            idx += 1
            continue

        if not inside_fence and HEAD_RE.match(ln):
            # Ensure a blank line before
            if final_lines_bl and final_lines_bl[-1].strip() != "":
                final_lines_bl.append("")
                added_blank_lines_headings += 1
            final_lines_bl.append(ln)
            # Ensure a blank line after (look ahead)
            nxt = final_lines_ol[idx + 1] if idx + 1 < len(final_lines_ol) else None
            if nxt is not None and nxt.strip() != "" and not HEAD_RE.match(nxt):
                # but don't insert before a fence start
                if not FENCE_OPEN_RE.match(nxt):
                    final_lines_bl.append("")
                    added_blank_lines_headings += 1
            idx += 1
            continue

        if not inside_fence and _is_list_item(ln):
            # Start of a list block - ensure a blank line before (MD032)
            if final_lines_bl and final_lines_bl[-1].strip() != "":
                final_lines_bl.append("")
                added_blank_lines_lists += 1

            # Consume the entire list block to normalize UL indents and preserve content
            # Determine the base indent from the first list item in the block
            base_indent = 0
            m0_ul = UL_ITEM_RE.match(final_lines_ol[idx])
            if m0_ul:
                base_indent = len(m0_ul.group("indent"))
            else:
                m0_ol = OL_ITEM_RE.match(final_lines_ol[idx])
                if m0_ol:
                    base_indent = len(m0_ol.group("indent"))

            while idx < len(final_lines_ol) and _is_list_item(final_lines_ol[idx]):
                cur = final_lines_ol[idx]
                m_ul = UL_ITEM_RE.match(cur)
                if m_ul:
                    indent_len = len(m_ul.group("indent"))
                    # Normalize unordered list indent relative to base item so top-level is column 0
                    relative = max(0, indent_len - base_indent)
                    normalized = (relative // 2) * 2
                    if normalized != indent_len:
                        new_indent = " " * normalized
                        cur = f"{new_indent}{m_ul.group('bullet')} {m_ul.group('rest')}"
                        ul_indent_normalized += 1
                final_lines_bl.append(cur)
                idx += 1

            # After list block, ensure one blank line if next is not EOF or closing delimiter (MD032)
            nxt = final_lines_ol[idx] if idx < len(final_lines_ol) else None
            if nxt is not None and nxt.strip() != "" and not HEAD_RE.match(nxt) and not FENCE_OPEN_RE.match(nxt):
                final_lines_bl.append("")
                added_blank_lines_lists += 1
            continue

        # Default path
        final_lines_bl.append(ln)
        idx += 1

    # Collapse multiple blank lines to at most one
    fixed_text = "\n".join(final_lines_bl)
    before = fixed_text
    fixed_text = re.sub(r"\n{3,}", "\n\n", fixed_text)
    if fixed_text != before:
        # rough count of collapsed groups
        blanks_collapsed = len(re.findall(r"\n{3,}", before))

    # Post-pass: After optional insertion of a top H1, ensure all subsequent H1s are demoted (MD025)
    lines2 = fixed_text.splitlines()
    inside_fence = False
    fence_delim = None
    saw_h1 = False
    for idx, ln in enumerate(lines2):
        m_open = (not inside_fence) and FENCE_OPEN_RE.match(ln)
        if m_open:
            inside_fence = True
            fence_delim = m_open.group("delim")
            continue
        if inside_fence and fence_delim is not None and ln.strip() == fence_delim:
            inside_fence = False
            fence_delim = None
            continue
        if not inside_fence:
            m_h1 = re.match(r"^#\s+(.+)$", ln)
            if m_h1:
                if not saw_h1:
                    saw_h1 = True
                else:
                    lines2[idx] = f"## {m_h1.group(1).strip()}"
                    post_demoted_h1 += 1
    fixed_text = "\n".join(lines2)

    # Normalize Unicode (NFC)
    fixed_text = unicodedata.normalize("NFC", fixed_text)

    stats = {
        "demoted_h1": demoted_h1,
        "labeled_fences": labeled_fences,
        "blanks_collapsed": blanks_collapsed,
        "bold_promoted": bold_promoted,
        "fixed_heading_punct": fixed_heading_punct,
        "normalized_heading_level": normalized_heading_level,
        "dedup_headings": dedup_headings,
        "fence_lang_relabelled": fence_lang_relabelled,
        "renumbered_ol": ol_renumbered,
        "added_blank_lines_headings": added_blank_lines_headings,
        "added_blank_lines_lists": added_blank_lines_lists,
        "inserted_top_h1": inserted_top_h1,
        "ul_indent_normalized": ul_indent_normalized,
        "fixed_atx_space": fixed_atx_space,
        "post_demoted_h1": post_demoted_h1,
    }
    return fixed_text + ("\n" if not fixed_text.endswith("\n") else ""), stats


def process_file(p: Path, json_output: bool = False) -> None:
    original_text, used_enc = read_text_best_effort(p)
    # Derive a readable title from filename for MD041
    title = p.stem.replace("_", " ").replace("-", " ").strip()
    title = re.sub(r"\s+", " ", title).title() if title else "Document"
    fixed_text, stats = fix_markdown(original_text, file_title=title)

    if fixed_text != original_text:
        backup = p.with_suffix(p.suffix + ".bak")
        shutil.copy2(p, backup)
        p.write_text(fixed_text, encoding="utf-8", newline="\n")
        if json_output:
            print(json.dumps({
                "path": str(p).replace("\\", "/"),
                "status": "fixed",
                "enc": used_enc,
                "stats": stats,
                "backup": backup.name
            }))
        else:
            print(f"[fixed] {p} | enc={used_enc} | stats={stats} | backup={backup.name}")
    else:
        if json_output:
            print(json.dumps({
                "path": str(p).replace("\\", "/"),
                "status": "clean",
                "enc": used_enc,
                "stats": stats,
                "backup": None
            }))
        else:
            print(f"[clean] {p} | enc={used_enc} | no changes")


def main(argv: List[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    # Simple flag handling: --json enables machine-readable output
    args = argv[1:]
    json_output = False
    if args and args[0] == "--json":
        json_output = True
        args = args[1:]

    for arg in args:
        p = Path(arg)
        if not p.exists():
            print(f"[skip] not found: {p}")
            continue
        if p.is_dir():
            print(f"[skip] directory: {p}")
            continue
        process_file(p, json_output=json_output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
