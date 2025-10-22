
# ORFEAS Encoding & Internationalization Reference

## Overview

This document describes the encoding and internationalization (i18n) systems in the ORFEAS platform, including:

- Multi-encoding detection and normalization
- Unicode and BOM handling
- Internationalization and language detection
- File conversion and multilingual pipeline setup

## Key Concepts

- **Encoding Detection:** Uses BOM, chardet, and charset-normalizer to detect file encoding. Fallback chain is configurable via environment.
- **Unicode Normalization:** Applies NFC/NFD/NFKC/NFKD normalization to all text, defaulting to NFC.
- **BOM Handling:** Detects and respects BOM for UTF-8/16/32, with validation.
- **Internationalization:** Language detection via langdetect (if available), with fallback to configured default language.
- **Environment Driven:** All toggles and fallback chains are controlled by environment variables (see below).

## Implementation Summary

### EncodingManager (`backend/encoding_manager.py`)

- Detects encoding using BOM, chardet, charset-normalizer, and fallback chain.
- Converts files to target encoding with normalization.
- Normalizes Unicode text using configured form.
- All toggles (multi-encoding, auto-detection, fallback chain, normalization, BOM, error handling) are environment-driven.

#### Example Usage

```python
from encoding_manager import EncodingManager
mgr = EncodingManager()
result = mgr.detect_encoding_with_fallback('file.txt')
mgr.convert_file_encoding('file.txt', 'file-utf8.txt', target_encoding='utf-8')
text = mgr.normalize_unicode('Café – 例')

```text

### InternationalizationManager (`backend/i18n_manager.py`)

- Detects language using langdetect (if available), else falls back to default.
- Maps detected language to supported set or closest match.
- Plans multilingual processing pipeline (encoding normalization, language detection, segmentation, NLP, translation prep).

#### Example Usage

```python
from i18n_manager import InternationalizationManager
i18n = InternationalizationManager()
lang_info = i18n.detect_content_language('Bonjour le monde!')
pipeline = i18n.setup_multilingual_processing('Hello world!', target_languages=['fr', 'de'])

```text

## Environment Variables

- `ENABLE_MULTI_ENCODING` (default: true)
- `ENCODING_AUTO_DETECTION` (default: true)
- `ENCODING_FALLBACK_CHAIN` (default: utf-8,latin-1,cp1252,ascii)
- `UNICODE_NORMALIZATION` (default: NFC)
- `BOM_DETECTION` (default: true)
- `ENCODING_ERROR_HANDLING` (default: replace)
- `DEFAULT_LANGUAGE` (default: en-US)
- `SUPPORTED_LANGUAGES` (default: en,es,fr,de,it,pt,ja,ko,zh-cn,zh-tw,ru,ar,hi)

## Usage Patterns

### Detecting and Converting File Encodings

```python
mgr = EncodingManager()
info = mgr.detect_encoding_with_fallback('input.txt')
mgr.convert_file_encoding('input.txt', 'output.txt', target_encoding='utf-8')

```text

### Unicode Normalization

```python
text = mgr.normalize_unicode('Café – 例')

```text

### Language Detection and Multilingual Pipeline

```python
i18n = InternationalizationManager()
lang = i18n.detect_content_language('Привет мир!')
pipeline = i18n.setup_multilingual_processing('Hola mundo!', target_languages=['en', 'fr'])

```text

## References

- See `.github/copilot-instructions.md` for full encoding/i18n patterns and advanced usage.
- See `backend/encoding_manager.py` and `backend/i18n_manager.py` for implementation details.
