"""
REPLICATOR ENGINE - Advanced 3D Object Reconstruction from Multiple Images
Handles:
- Multi-angle image processing
- Ruler/scale detection and calibration
- Geometric analysis and dimension extraction
- Photogrammetry-style 3D reconstruction
- Smart photo validation and guidance
"""

import os
import json
import logging
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime
import cv2
from PIL import Image
import uuid

logger = logging.getLogger(__name__)


@dataclass
class DimensionEstimate:
    """Estimated dimension from pixel measurements"""
    pixel_length: float
    mm_per_pixel: float
    real_length_mm: float
    confidence: float
    source: str  # "ruler" or "geometry"


@dataclass
class RulerDetection:
    """Detected ruler calibration in image"""
    detected: bool
    pixels: float
    ruler_type: str  # "cm_ruler", "inch_ruler", "metric_scale", "unknown"
    mm_per_pixel: float
    position: Tuple[int, int, int, int]  # x1, y1, x2, y2
    confidence: float


@dataclass
class ObjectAnalysis:
    """Complete analysis of object from single image"""
    image_id: str
    angle: Dict[str, float]  # yaw, pitch, roll in degrees
    dimensions: Dict[str, DimensionEstimate]  # width, height, depth
    geometry_type: str  # "box", "cylinder", "sphere", "irregular"
    features: List[str]  # detected features
    cavities: List[Dict]  # detected hidden areas
    ruler_calibration: Optional[RulerDetection]
    confidence: float
    needs_additional_photos: List[str]  # list of requested angles


class RulerDetector:
    """Detect and calibrate rulers in images for scale reference"""

    def __init__(self):
        self.ruler_patterns = {
            "cm_ruler": {"pixels_per_unit": None, "unit_mm": 10},
            "inch_ruler": {"pixels_per_unit": None, "unit_mm": 25.4},
            "metric_scale": {"pixels_per_unit": None, "unit_mm": 1},
        }
        logger.info("[RULER] RulerDetector initialized")

    def detect_ruler(self, image: np.ndarray) -> RulerDetection:
        """
        Detect ruler in image using edge detection and Hough lines

        Args:
            image: Input image (BGR or RGB)

        Returns:
            RulerDetection with calibration data
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Edge detection
            edges = cv2.Canny(gray, 50, 150)

            # Find contours
            contours, _ = cv2.findContours(
                edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                logger.warning("[RULER] No contours detected")
                return RulerDetection(
                    detected=False,
                    pixels=0,
                    ruler_type="unknown",
                    mm_per_pixel=0,
                    position=(0, 0, 0, 0),
                    confidence=0,
                )

            # Find longest straight line (potential ruler)
            ruler_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(ruler_contour)

            # Estimate ruler dimensions
            ruler_length_pixels = max(w, h)

            # Try to match to known ruler types
            ruler_type = self._classify_ruler(image, ruler_contour)
            mm_per_pixel = self._calibrate_ruler(ruler_type, ruler_length_pixels)

            logger.info(
                f"[RULER] Detected: type={ruler_type}, length={ruler_length_pixels}px, "
                f"calibration={mm_per_pixel:.4f}mm/px"
            )

            return RulerDetection(
                detected=True,
                pixels=ruler_length_pixels,
                ruler_type=ruler_type,
                mm_per_pixel=mm_per_pixel,
                position=(x, y, x + w, y + h),
                confidence=0.75,
            )

        except Exception as e:
            logger.error(f"[RULER] Detection error: {e}")
            return RulerDetection(
                detected=False,
                pixels=0,
                ruler_type="unknown",
                mm_per_pixel=0,
                position=(0, 0, 0, 0),
                confidence=0,
            )

    def _classify_ruler(self, image: np.ndarray, contour) -> str:
        """Classify ruler type based on visual features"""
        # Simple classification - in production would use ML model
        area = cv2.contourArea(contour)
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / max(h, 1)

        if aspect_ratio > 5:  # Long and thin
            return "cm_ruler"
        elif 2 < aspect_ratio <= 5:
            return "metric_scale"
        else:
            return "inch_ruler"

    def _calibrate_ruler(self, ruler_type: str, pixel_length: float) -> float:
        """Calculate mm per pixel based on ruler type"""
        # Standard ruler calibrations
        calibrations = {
            "cm_ruler": {"expected_mm": 150, "typical_pixels": 500},  # 15cm ruler ~500px
            "inch_ruler": {"expected_mm": 127, "typical_pixels": 450},  # 5" ruler ~450px
            "metric_scale": {"expected_mm": 100, "typical_pixels": 400},  # 10cm ~400px
        }

        if ruler_type not in calibrations:
            return 0.1  # Default fallback

        calib = calibrations[ruler_type]
        mm_per_pixel = calib["expected_mm"] / max(pixel_length, 1)
        return mm_per_pixel


class GeometryAnalyzer:
    """Analyze geometric properties and estimate dimensions"""

    def __init__(self):
        logger.info("[GEOMETRY] GeometryAnalyzer initialized")

    def analyze_geometry(
        self, image: np.ndarray, mm_per_pixel: float = 0.1
    ) -> Dict[str, Any]:
        """
        Analyze geometric properties of object in image

        Args:
            image: Input image
            mm_per_pixel: Calibration from ruler detection

        Returns:
            Dictionary with geometry analysis
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Threshold
            _, binary = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

            # Find main object contour
            contours, _ = cv2.findContours(
                binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
            )

            if not contours:
                return {"type": "unknown", "dimensions": {}, "confidence": 0}

            # Get largest contour (object)
            obj_contour = max(contours, key=cv2.contourArea)

            # Fit ellipse and rotated rect
            if len(obj_contour) >= 5:
                ellipse = cv2.fitEllipse(obj_contour)
                rotation_rect = cv2.minAreaRect(obj_contour)
            else:
                x, y, w, h = cv2.boundingRect(obj_contour)
                return {
                    "type": "box",
                    "dimensions": {
                        "width_mm": w * mm_per_pixel,
                        "height_mm": h * mm_per_pixel,
                    },
                    "confidence": 0.6,
                }

            # Classify geometry type
            geometry_type = self._classify_geometry(obj_contour, ellipse)

            # Extract dimensions
            dimensions = self._extract_dimensions(rotation_rect, mm_per_pixel)

            logger.info(
                f"[GEOMETRY] Analyzed: type={geometry_type}, dims={dimensions}"
            )

            return {
                "type": geometry_type,
                "dimensions": dimensions,
                "confidence": 0.8,
                "contour_points": len(obj_contour),
            }

        except Exception as e:
            logger.error(f"[GEOMETRY] Analysis error: {e}")
            return {"type": "unknown", "dimensions": {}, "confidence": 0}

    def _classify_geometry(self, contour, ellipse) -> str:
        """Classify object geometry (box, cylinder, sphere, irregular)"""
        # Calculate circularity
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        circularity = 4 * np.pi * area / (perimeter**2) if perimeter > 0 else 0

        # Fit ellipse eccentricity
        if ellipse:
            (cx, cy), (w, h), angle = ellipse
            eccentricity = np.sqrt(1 - (min(w, h) / max(w, h)) ** 2)
        else:
            eccentricity = 0

        if circularity > 0.85:
            return "sphere"
        elif 0.7 < eccentricity < 0.95:
            return "cylinder"
        elif circularity < 0.6:
            return "box"
        else:
            return "irregular"

    def _extract_dimensions(
        self, rotation_rect: Tuple, mm_per_pixel: float
    ) -> Dict[str, float]:
        """Extract width, height, depth estimates from rotated rectangle"""
        (cx, cy), (w, h), angle = rotation_rect

        return {
            "width_mm": w * mm_per_pixel,
            "height_mm": h * mm_per_pixel,
            "aspect_ratio": w / max(h, 1),
        }


class AngleEstimator:
    """Estimate viewing angle from image features"""

    def __init__(self):
        logger.info("[ANGLE] AngleEstimator initialized")

    def estimate_angle(self, image: np.ndarray) -> Dict[str, float]:
        """
        Estimate viewing angle (yaw, pitch, roll)

        Args:
            image: Input image

        Returns:
            Dictionary with angle estimates in degrees
        """
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Find edges
            edges = cv2.Canny(gray, 50, 150)

            # Hough lines for perspective analysis
            lines = cv2.HoughLines(edges, 1, np.pi / 180, 100)

            if lines is None:
                return {"yaw": 0, "pitch": 0, "roll": 0}

            # Analyze line angles for perspective
            angles = []
            for line in lines:
                rho, theta = line[0]
                angles.append(np.degrees(theta))

            # Estimate perspective from line distribution
            mean_angle = np.mean(angles) if angles else 0
            yaw = min(max(mean_angle - 90, -45), 45)  # -45 to +45 degrees

            # Pitch estimation (horizon line)
            horizontal_lines = [a for a in angles if 170 < a < 190 or 0 < a < 10]
            pitch = 0 if len(horizontal_lines) > len(angles) / 2 else 15

            # Roll estimation
            vertical_lines = [a for a in angles if 80 < a < 100]
            roll = 0 if len(vertical_lines) > len(angles) / 3 else 10

            logger.info(f"[ANGLE] Estimated: yaw={yaw}°, pitch={pitch}°, roll={roll}°")

            return {"yaw": yaw, "pitch": pitch, "roll": roll}

        except Exception as e:
            logger.error(f"[ANGLE] Estimation error: {e}")
            return {"yaw": 0, "pitch": 0, "roll": 0}


class CavityDetector:
    """Detect hidden cavities and suggest additional photos"""

    def __init__(self):
        logger.info("[CAVITY] CavityDetector initialized")

    def detect_cavities(self, image: np.ndarray) -> Tuple[List[Dict], List[str]]:
        """
        Detect potential hidden cavities and suggest angles to capture them

        Args:
            image: Input image

        Returns:
            Tuple of (cavities list, suggested angles)
        """
        try:
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Find sharp edges indicating cavities
            edges = cv2.Canny(gray, 100, 200)

            # Morphological operations
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
            closed = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)

            # Find contours (potential cavities)
            contours, _ = cv2.findContours(
                closed, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE
            )

            cavities = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if 100 < area < 5000:  # Likely cavity size
                    x, y, w, h = cv2.boundingRect(contour)
                    cavities.append(
                        {
                            "id": f"cavity_{i}",
                            "location": {"x": x, "y": y, "w": w, "h": h},
                            "area": area,
                            "type": "potential_hidden",
                        }
                    )

            # Suggest angles to capture hidden areas
            suggested_angles = self._suggest_angles_for_cavities(cavities)

            logger.info(
                f"[CAVITY] Detected {len(cavities)} cavities, "
                f"suggested {len(suggested_angles)} additional angles"
            )

            return cavities, suggested_angles

        except Exception as e:
            logger.error(f"[CAVITY] Detection error: {e}")
            return [], []

    def _suggest_angles_for_cavities(self, cavities: List[Dict]) -> List[str]:
        """Suggest specific angles to photograph cavities"""
        if not cavities:
            return []

        suggestions = []

        # Common cavity locations and suggested angles
        for cavity in cavities:
            x, y = cavity["location"]["x"], cavity["location"]["y"]
            # Top of image -> shoot from below
            if y < 100:
                suggestions.append("bottom_view")
            # Bottom of image -> shoot from above
            elif y > 400:
                suggestions.append("top_view")
            # Left side -> shoot from right
            elif x < 100:
                suggestions.append("right_side_view")
            # Right side -> shoot from left
            elif x > 400:
                suggestions.append("left_side_view")

        # Remove duplicates and return unique suggestions
        return list(set(suggestions))


class ReplicatorEngine:
    """Main replicator engine orchestrating 3D reconstruction"""

    def __init__(self):
        self.ruler_detector = RulerDetector()
        self.geometry_analyzer = GeometryAnalyzer()
        self.angle_estimator = AngleEstimator()
        self.cavity_detector = CavityDetector()
        self.session_id = str(uuid.uuid4())[:8]
        self.images_database = {}
        logger.info(f"[REPLICATOR] Engine initialized (session: {self.session_id})")

    def process_image(
        self, image_path: str, angle_hint: Optional[str] = None
    ) -> ObjectAnalysis:
        """
        Process single image for 3D reconstruction

        Args:
            image_path: Path to image file
            angle_hint: Optional hint about viewing angle

        Returns:
            ObjectAnalysis with all extracted data
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Cannot load image: {image_path}")

            image_id = str(uuid.uuid4())[:8]
            logger.info(f"[REPLICATOR] Processing image: {image_id}")

            # Step 1: Detect ruler for calibration
            ruler_detection = self.ruler_detector.detect_ruler(image)
            mm_per_pixel = (
                ruler_detection.mm_per_pixel if ruler_detection.detected else 0.1
            )

            logger.info(
                f"[REPLICATOR] Ruler calibration: {mm_per_pixel:.4f} mm/pixel"
            )

            # Step 2: Analyze geometry
            geometry = self.geometry_analyzer.analyze_geometry(image, mm_per_pixel)

            # Step 3: Estimate viewing angle
            angle = self.angle_estimator.estimate_angle(image)

            # Step 4: Detect cavities and hidden areas
            cavities, suggested_angles = self.cavity_detector.detect_cavities(image)

            # Step 5: Extract dimensions with confidence
            dimensions = self._extract_dimensions(
                geometry, ruler_detection, mm_per_pixel
            )

            # Create analysis object
            analysis = ObjectAnalysis(
                image_id=image_id,
                angle=angle,
                dimensions=dimensions,
                geometry_type=geometry.get("type", "unknown"),
                features=self._extract_features(image),
                cavities=cavities,
                ruler_calibration=ruler_detection,
                confidence=0.75 if ruler_detection.detected else 0.60,
                needs_additional_photos=suggested_angles,
            )

            # Store in database
            self.images_database[image_id] = {
                "image_path": image_path,
                "analysis": asdict(analysis),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"[REPLICATOR] Image analysis complete: {image_id}")
            return analysis

        except Exception as e:
            logger.error(f"[REPLICATOR] Processing error: {e}", exc_info=True)
            raise

    def _extract_dimensions(
        self,
        geometry: Dict,
        ruler_detection: RulerDetection,
        mm_per_pixel: float,
    ) -> Dict[str, DimensionEstimate]:
        """Extract and estimate dimensions from geometry"""
        dimensions = {}

        for key, value in geometry.get("dimensions", {}).items():
            if isinstance(value, (int, float)):
                dimensions[key] = DimensionEstimate(
                    pixel_length=value / mm_per_pixel if mm_per_pixel > 0 else 0,
                    mm_per_pixel=mm_per_pixel,
                    real_length_mm=value,
                    confidence=(
                        0.9 if ruler_detection.detected else 0.65
                    ),
                    source="ruler" if ruler_detection.detected else "geometry",
                )

        return dimensions

    def _extract_features(self, image: np.ndarray) -> List[str]:
        """Extract visible features from image"""
        features = []

        # Basic feature detection
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Detect corners (sharp features)
        corners = cv2.cornerHarris(gray, 2, 3, 0.04)
        if np.any(corners > 0.01 * corners.max()):
            features.append("sharp_edges")

        # Detect texture
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        if laplacian.std() > 50:
            features.append("textured_surface")

        # Detect color variation
        if len(cv2.imread(image.tobytes())) > 0:
            features.append("colored")

        return features

    def process_multiple_images(
        self, image_paths: List[str], angle_hints: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Process multiple images for comprehensive 3D reconstruction

        Args:
            image_paths: List of image file paths
            angle_hints: Optional list of angle hints

        Returns:
            Comprehensive analysis combining all images
        """
        analyses = []
        all_suggested_angles = set()

        logger.info(
            f"[REPLICATOR] Processing {len(image_paths)} images "
            f"for 3D reconstruction"
        )

        for i, image_path in enumerate(image_paths):
            angle_hint = angle_hints[i] if angle_hints and i < len(angle_hints) else None
            try:
                analysis = self.process_image(image_path, angle_hint)
                analyses.append(asdict(analysis))
                all_suggested_angles.update(analysis.needs_additional_photos)
            except Exception as e:
                logger.warning(f"[REPLICATOR] Failed to process {image_path}: {e}")
                continue

        # Compute statistics
        stats = self._compute_reconstruction_stats(analyses)

        logger.info(
            f"[REPLICATOR] Multi-image analysis complete: "
            f"{len(analyses)} images, confidence={stats['avg_confidence']:.2f}"
        )

        return {
            "session_id": self.session_id,
            "num_images": len(analyses),
            "analyses": analyses,
            "statistics": stats,
            "suggested_angles": list(all_suggested_angles),
            "next_steps": self._generate_next_steps(stats, all_suggested_angles),
        }

    def _compute_reconstruction_stats(self, analyses: List[Dict]) -> Dict[str, Any]:
        """Compute statistics from multiple analyses"""
        if not analyses:
            return {}

        confidences = [a.get("confidence", 0) for a in analyses]
        dimensions_data = [
            d for a in analyses for d in a.get("dimensions", {}).values()
        ]

        return {
            "avg_confidence": np.mean(confidences),
            "num_cavities": sum(len(a.get("cavities", [])) for a in analyses),
            "geometry_types": list(set(a.get("geometry_type") for a in analyses)),
            "avg_dimension_confidence": (
                np.mean([d.get("confidence", 0) for d in dimensions_data])
                if dimensions_data
                else 0
            ),
        }

    def _generate_next_steps(
        self, stats: Dict[str, Any], suggested_angles: set
    ) -> List[str]:
        """Generate next steps based on analysis"""
        steps = []

        if stats.get("avg_confidence", 0) < 0.7:
            steps.append("Improve lighting and capture additional reference images")

        if suggested_angles:
            steps.append(
                f"Capture missing angles: {', '.join(sorted(suggested_angles))}"
            )

        if stats.get("num_cavities", 0) > 0:
            steps.append("Verify detected cavities with detailed close-up photos")

        steps.append("Export 3D model and review accuracy")

        return steps

    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of current session"""
        return {
            "session_id": self.session_id,
            "images_processed": len(self.images_database),
            "timestamp": datetime.now().isoformat(),
            "images": list(self.images_database.keys()),
        }


# Module initialization
def get_replicator_engine() -> ReplicatorEngine:
    """Get or create replicator engine singleton"""
    if not hasattr(get_replicator_engine, "_instance"):
        get_replicator_engine._instance = ReplicatorEngine()
    return get_replicator_engine._instance
