"""
InternationalizationManager: language detection and multilingual pipeline planning

Uses langdetect if available; otherwise, falls back to DEFAULT_LANGUAGE.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional


class InternationalizationManager:
    def __init__(self) -> None:
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "en-US")
        supported = os.getenv(
            "SUPPORTED_LANGUAGES",
            "en,es,fr,de,it,pt,ja,ko,zh-cn,zh-tw,ru,ar,hi",
        )
        self.supported_languages = [s.strip() for s in supported.split(",") if s.strip()]

        # Optional dependency
        self._langdetect = None
        try:
            # langdetect exposes: detect, detect_langs
            import langdetect  # type: ignore

            self._langdetect = langdetect
        except Exception:
            pass

    def detect_content_language(self, text: str) -> Dict[str, Any]:
        if not text:
            return {
                "language": self.default_language,
                "confidence": 0.1,
                "method": "fallback",
                "supported": True,
            }

        if self._langdetect is not None:
            try:
                detected = self._langdetect.detect(text)
                langs = self._langdetect.detect_langs(text)
                conf = float(langs[0].prob) if langs else 0.6
                mapped = self._map_to_supported(detected)
                return {
                    "language": mapped,
                    "original_detection": detected,
                    "confidence": conf if mapped == detected else conf * 0.8,
                    "method": "langdetect" if mapped == detected else "langdetect_mapped",
                    "supported": True,
                }
            except Exception:
                # fall through to fallback
                pass

        return {
            "language": self.default_language,
            "confidence": 0.1,
            "method": "fallback",
            "supported": True,
        }

    def setup_multilingual_processing(
        self, content: str, target_languages: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        det = self.detect_content_language(content)
        targets = target_languages or self.supported_languages
        return {
            "source_language": det["language"],
            "target_languages": targets,
            "processing_steps": [
                "encoding_normalization",
                "language_detection",
                "text_segmentation",
                "nlp_processing",
                "translation_preparation",
            ],
            "language_specific_processors": {lang: {"enabled": True} for lang in targets},
        }

    def _map_to_supported(self, lang: str) -> str:
        # If detected code already supported, return it, else fallback to default
        if lang in self.supported_languages:
            return lang
        # Heuristics: normalize some variants
        lower = lang.lower()
        if lower.startswith("zh"):
            return "zh-cn" if "cn" in lower or "hans" in lower else "zh-tw"
        if lower.startswith("en"):
            return "en"
        return self.default_language
"""
Full-featured InternationalizationManager for language detection and pipeline setup.

Uses langdetect if available and safely falls back to configured default language.
"""
from __future__ import annotations

from typing import Any, Dict, List
import os

try:
    from langdetect import detect, detect_langs  # type: ignore
except Exception:  # pragma: no cover - optional
    detect = None  # type: ignore
    detect_langs = None  # type: ignore


class InternationalizationManager:
    """Advanced i18n manager with optional language detection support."""

    def __init__(self) -> None:
        self.default_language = os.getenv("DEFAULT_LANGUAGE", "en-US")
        self.supported_languages = [
            s.strip()
            for s in os.getenv(
                "SUPPORTED_LANGUAGES",
                "en,es,fr,de,it,pt,ja,ko,zh-cn,zh-tw,ru,ar,hi",
            ).split(",")
            if s.strip()
        ]

    def detect_content_language(self, text: str) -> Dict[str, Any]:
        """Detect language of text content with safe fallbacks."""
        if not text:
            return {
                "language": self.default_language,
                "confidence": 0.1,
                "method": "fallback",
                "supported": True,
            }

        # Try langdetect if available
        if detect and detect_langs:
            try:
                lang = detect(text)  # e.g., 'en'
                candidates = detect_langs(text)
                confidence = float(candidates[0].prob) if candidates else 0.5

                if lang in self.supported_languages:
                    return {
                        "language": lang,
                        "confidence": confidence,
                        "method": "langdetect",
                        "supported": True,
                    }
                else:
                    # map to closest supported language if possible (simple heuristic)
                    mapped = self._map_to_supported(lang)
                    return {
                        "language": mapped,
                        "original_detection": lang,
                        "confidence": confidence * 0.8,
                        "method": "langdetect_mapped",
                        "supported": True,
                    }
            except Exception:
                pass

        # Fallback to default language
        return {
            "language": self.default_language,
            "confidence": 0.1,
            "method": "fallback",
            "supported": True,
        }

    def setup_multilingual_processing(
        self, content: str, target_languages: List[str] | None = None
    ) -> Dict[str, Any]:
        """Create a pipeline plan for multilingual processing (metadata only)."""
        src = self.detect_content_language(content)
        targets = target_languages or self.supported_languages

        pipeline = {
            "source_language": src["language"],
            "target_languages": targets,
            "processing_steps": [
                "encoding_normalization",
                "language_detection",
                "text_segmentation",
                "nlp_processing",
                "translation_preparation",
            ],
        }
        return pipeline

    def _map_to_supported(self, lang: str) -> str:
        # Basic mapping to handle variants (e.g., en-US -> en)
        base = lang.lower().split("-")[0]
        if base in self.supported_languages:
            return base
        # default
        return self.default_language
