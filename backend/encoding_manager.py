"""
Full-featured EncodingManager for multi-encoding detection, normalization, and conversion.

Implements robust detection with BOM, chardet, and charset-normalizer,
plus an environment-driven fallback chain. Also provides Unicode normalization
and file conversion utilities.

Environment variables honored (with sensible defaults):
- ENABLE_MULTI_ENCODING (bool)
- ENCODING_AUTO_DETECTION (bool)
- ENCODING_FALLBACK_CHAIN (comma list)
- UNICODE_NORMALIZATION (NFC/NFD/NFKC/NFKD)
- BOM_DETECTION (bool)
- ENCODING_ERROR_HANDLING (strict/ignore/replace/xmlcharrefreplace)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple, List
import os
import unicodedata

# Optional dependencies
try:  # type: ignore
    import chardet  # noqa: F401
except Exception:  # pragma: no cover - optional
    chardet = None  # type: ignore

try:  # type: ignore
    from charset_normalizer import from_bytes as cn_from_bytes  # noqa: F401
except Exception:  # pragma: no cover - optional
    cn_from_bytes = None  # type: ignore


@dataclass
class DetectionResult:
    encoding: str
    confidence: float
    method: str
    bom_present: bool = False
    fallback_position: Optional[int] = None
    error_handling: Optional[str] = None


class EncodingManager:
    """Advanced multi-encoding detection and conversion manager."""

    def __init__(self) -> None:
        self.supported_encodings: List[str] = [
            "utf-8",
            "utf-16-le",
            "utf-16-be",
            "utf-32-le",
            "utf-32-be",
            "ascii",
            "latin-1",
            "cp1252",
            "gb2312",
            "gbk",
            "big5",
            "shift-jis",
            "euc-kr",
            "iso-8859-1",
            "iso-8859-2",
            "iso-8859-15",
        ]

        self.enable_multi_encoding = self._env_bool("ENABLE_MULTI_ENCODING", True)
        self.auto_detection = self._env_bool("ENCODING_AUTO_DETECTION", True)
        self.bom_detection = self._env_bool("BOM_DETECTION", True)
        self.error_policy = os.getenv("ENCODING_ERROR_HANDLING", "replace")

        self.normalization_form = os.getenv("UNICODE_NORMALIZATION", "NFC").upper()
        if self.normalization_form not in {"NFC", "NFD", "NFKC", "NFKD"}:
            self.normalization_form = "NFC"

        self.fallback_chain = [
            s.strip() for s in os.getenv(
                "ENCODING_FALLBACK_CHAIN", "utf-8,latin-1,cp1252,ascii"
            ).split(",")
            if s.strip()
        ]

    # ----------------------------- Public API ----------------------------- #
    def detect_encoding_with_fallback(self, file_path: str) -> Dict[str, Any]:
        """Detect file encoding with intelligent fallback chain.

        Returns a dict compatible with docs under [2.8] in copilot-instructions.
        """
        # Read dynamic toggles at call-time so tests and runtime env updates take effect
        local_auto_detection = self._env_bool("ENCODING_AUTO_DETECTION", self.auto_detection)
        local_enable_multi = self._env_bool("ENABLE_MULTI_ENCODING", self.enable_multi_encoding)
        local_fallback_chain = [
            s.strip() for s in os.getenv(
                "ENCODING_FALLBACK_CHAIN", ",".join(self.fallback_chain)
            ).split(",") if s.strip()
        ] or self.fallback_chain
        try:
            with open(file_path, "rb") as f:
                raw_data = f.read()
        except Exception:
            # If file cannot be read, return UTF-8 fallback
            return DetectionResult(
                encoding="utf-8",
                confidence=0.1,
                method="default_fallback",
                bom_present=False,
                error_handling=self.error_policy,
            ).__dict__

        # 1) BOM detection (highest priority)
        if self.bom_detection:
            bom = self._detect_bom(raw_data)
            if bom:
                enc, _ = bom
                # Validate that data decodes cleanly with the BOM-claimed encoding.
                # If it fails (e.g., truncated or not really that encoding), ignore BOM and continue.
                try:
                    # [ORFEAS FIX 5] For utf-16 variants, use "utf-16" to properly handle BOM
                    decode_enc = "utf-16" if enc in ("utf-16-le", "utf-16-be") else enc
                    _ = raw_data.decode(decode_enc, errors="strict")
                    # [ORFEAS FIX 5] Normalize encoding name for consistency
                    normalized_enc = enc.replace("-le", "").replace("-be", "") if enc in ("utf-16-le", "utf-16-be") else enc
                    return DetectionResult(
                        encoding=normalized_enc,
                        confidence=1.0,
                        method="bom_detection",
                        bom_present=True,
                    ).__dict__
                except Exception:
                    # Fall through to heuristic/fallback detection
                    pass

        detection_results: List[DetectionResult] = []

        # 2) Automatic detection via optional libs
        if local_auto_detection and local_enable_multi:
            if chardet is not None:
                try:
                    ch_res = chardet.detect(raw_data)  # type: ignore[attr-defined]
                    if ch_res and ch_res.get("encoding"):
                        detected_enc = str(ch_res["encoding"]).lower()
                        # [ORFEAS FIX 5] Check if detected encoding is UTF-16 and has BOM
                        has_bom_flag = (
                            detected_enc in ("utf-16", "utf-16-le", "utf-16-be") and
                            (raw_data.startswith(b"\xff\xfe") or raw_data.startswith(b"\xfe\xff"))
                        )
                        detection_results.append(
                            DetectionResult(
                                encoding=detected_enc,
                                confidence=float(ch_res.get("confidence", 0.0)),
                                method="chardet",
                                bom_present=has_bom_flag,
                            )
                        )
                except Exception:
                    pass

            if cn_from_bytes is not None:
                try:
                    norm_best = cn_from_bytes(raw_data).best()  # type: ignore[misc]
                    if norm_best and getattr(norm_best, "encoding", None):
                        detected_enc = str(norm_best.encoding).lower()
                        # [ORFEAS FIX 5] Check if detected encoding is UTF-16 and has BOM
                        has_bom_flag = (
                            detected_enc in ("utf-16", "utf-16-le", "utf-16-be") and
                            (raw_data.startswith(b"\xff\xfe") or raw_data.startswith(b"\xfe\xff"))
                        )
                        detection_results.append(
                            DetectionResult(
                                encoding=detected_enc,
                                confidence=float(getattr(norm_best, "coherence", 0.0)),
                                method="charset_normalizer",
                                bom_present=has_bom_flag,
                            )
                        )
                except Exception:
                    pass

        # 3) Choose highest confidence result above threshold
        if detection_results:
            best = max(detection_results, key=lambda r: r.confidence)
            if best.confidence >= 0.7:
                return best.__dict__

        # 4) Fallback chain validation
        for idx, enc in enumerate(local_fallback_chain):
            if self._validate_encoding(raw_data, enc):
                # [ORFEAS FIX 5] Check if fallback-detected encoding is UTF-16 with BOM
                has_bom_flag = (
                    enc in ("utf-16", "utf-16-le", "utf-16-be") and
                    (raw_data.startswith(b"\xff\xfe") or raw_data.startswith(b"\xfe\xff"))
                )
                return DetectionResult(
                    encoding=enc,
                    confidence=0.5,
                    method="fallback_validation",
                    fallback_position=idx,
                    bom_present=has_bom_flag,
                ).__dict__

        # 5) Default to UTF-8 with configured error handling
        return DetectionResult(
            encoding="utf-8",
            confidence=0.1,
            method="default_fallback",
            error_handling=self.error_policy,
            bom_present=False,
        ).__dict__

    def convert_file_encoding(
        self, input_path: str, output_path: str, target_encoding: str = "utf-8"
    ) -> Dict[str, Any]:
        """Convert file from detected encoding to target encoding with normalization."""
        src_info = self.detect_encoding_with_fallback(input_path)
        src_enc = src_info.get("encoding", "utf-8")
        try:
            with open(input_path, "r", encoding=src_enc, errors=self.error_policy) as f:
                content = f.read()

            normalized = self.normalize_unicode(content)
            with open(output_path, "w", encoding=target_encoding, errors=self.error_policy) as fw:
                fw.write(normalized)

            return {
                "success": True,
                "source_encoding": src_enc,
                "source_confidence": src_info.get("confidence", 0.0),
                "target_encoding": target_encoding,
                "normalization_applied": True,
                "bom_present": src_info.get("bom_present", False),
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "source_encoding": src_enc,
                "target_encoding": target_encoding,
            }

    def normalize_unicode(self, text: str, form: Optional[str] = None) -> str:
        """Normalize Unicode text using configured or provided form."""
        try:
            nf = (form or self.normalization_form).upper()
            if nf not in {"NFC", "NFD", "NFKC", "NFKD"}:
                nf = "NFC"
            return unicodedata.normalize(nf, text)
        except Exception:
            return text

    # ---------------------------- Internal utils --------------------------- #
    @staticmethod
    def _env_bool(name: str, default: bool) -> bool:
        val = os.getenv(name)
        if val is None:
            return default
        return str(val).strip().lower() in {"1", "true", "yes", "on"}

    @staticmethod
    def _detect_bom(raw: bytes) -> Optional[Tuple[str, int]]:
        # Return (encoding, bom_length)
        if raw.startswith(b"\xef\xbb\xbf"):
            return ("utf-8", 3)
        if raw.startswith(b"\xff\xfe\x00\x00"):
            return ("utf-32-le", 4)
        if raw.startswith(b"\x00\x00\xfe\xff"):
            return ("utf-32-be", 4)
        if raw.startswith(b"\xff\xfe"):
            return ("utf-16-le", 2)
        if raw.startswith(b"\xfe\xff"):
            return ("utf-16-be", 2)
        return None

    @staticmethod
    def _validate_encoding(raw: bytes, encoding: str) -> bool:
        try:
            _ = raw.decode(encoding, errors="strict")
            return True
        except Exception:
            return False
