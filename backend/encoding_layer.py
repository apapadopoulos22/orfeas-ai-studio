"""
Compatibility wrapper that provides a stable activation API for encoding/i18n.

This module preserves the existing main.py import contract while delegating to
the full implementations in encoding_manager.py and i18n_manager.py when
available. If those modules cannot be imported for any reason, it falls back to
minimal internal stubs to keep the app running.
"""
from __future__ import annotations

import os
from typing import Optional

try:
    # Prefer full-featured implementations
    from .encoding_manager import EncodingManager  # type: ignore
except Exception:  # pragma: no cover - safety fallback
    # Minimal inline stub
    import unicodedata
    from typing import Any, Dict

    class EncodingManager:  # type: ignore
        def __init__(self) -> None:
            self.normalization_form = os.getenv("UNICODE_NORMALIZATION", "NFC").upper()
            if self.normalization_form not in {"NFC", "NFD", "NFKC", "NFKD"}:
                self.normalization_form = "NFC"

        def normalize_unicode(self, text: str, form: Optional[str] = None) -> str:
            try:
                nf = (form or self.normalization_form).upper()
                if nf not in {"NFC", "NFD", "NFKC", "NFKD"}:
                    nf = "NFC"
                return unicodedata.normalize(nf, text)
            except Exception:
                return text

        def detect_encoding_with_fallback(self, file_path: Optional[str] = None) -> Dict[str, Any]:
            return {
                "encoding": "utf-8",
                "confidence": 0.1,
                "method": "default_fallback",
                "bom_present": False,
            }

try:
    from .i18n_manager import InternationalizationManager  # type: ignore
except Exception:  # pragma: no cover - safety fallback
    from typing import Any, Dict

    class InternationalizationManager:  # type: ignore
        def __init__(self) -> None:
            self.default_language = os.getenv("DEFAULT_LANGUAGE", "en-US")

        def detect_content_language(self, text: str) -> Dict[str, Any]:
            return {
                "language": self.default_language,
                "confidence": 0.1,
                "method": "fallback",
                "supported": True,
            }


# --- Simple singletons to align with initialization snippet semantics ---
_encoding_mgr: Optional[EncodingManager] = None
_i18n_mgr: Optional[InternationalizationManager] = None


def init_multi_encoding_layers() -> None:
    """Initialize encoding and i18n layers once at startup."""
    global _encoding_mgr, _i18n_mgr
    if _encoding_mgr is None:
        _encoding_mgr = EncodingManager()
    if _i18n_mgr is None:
        _i18n_mgr = InternationalizationManager()


def get_encoding_manager() -> EncodingManager:
    global _encoding_mgr
    if _encoding_mgr is None:
        _encoding_mgr = EncodingManager()
    return _encoding_mgr


def get_i18n_manager() -> InternationalizationManager:
    global _i18n_mgr
    if _i18n_mgr is None:
        _i18n_mgr = InternationalizationManager()
    return _i18n_mgr
