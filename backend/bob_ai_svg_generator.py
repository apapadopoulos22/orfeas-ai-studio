"""
Bob AI Text-to-Vector & SVG Generation Module
=============================================
Handles AI-powered SVG generation and manipulation for 2.5D Studio

Features:
- Text-to-SVG generation using local LLM (Mistral)
- Vector enhancement (simplify, complexify, stylize, custom)
- SVG path manipulation and optimization
- Design style application
- Complexity level handling
"""

import os
import json
import logging
import tempfile
import uuid
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
from dataclasses import dataclass
import re

# SVG and vector processing
try:
    import svgwrite
    SVGWRITE_AVAILABLE = True
except ImportError:
    SVGWRITE_AVAILABLE = False

try:
    from svgpathtools import parse_path, svg2paths
    SVGPATHTOOLS_AVAILABLE = True
except ImportError:
    SVGPATHTOOLS_AVAILABLE = False

# LLM integration
from llm_local_integration import get_ollama_manager

logger = logging.getLogger(__name__)


@dataclass
class SVGGenerationConfig:
    """Configuration for SVG generation"""
    style: str  # geometric, organic, abstract, decorative, technical, artistic
    complexity: str  # simple, medium, complex
    path_count_target: int  # estimated number of paths
    width: int = 800
    height: int = 600
    stroke_width: float = 2.0


class BobAISVGGenerator:
    """Main SVG generation engine powered by local LLM"""

    def __init__(self):
        self.ollama = get_ollama_manager()
        self.output_dir = Path("downloads")
        self.output_dir.mkdir(exist_ok=True)

        # Style definitions
        self.style_definitions = self._load_style_definitions()

        # Complexity mappings
        self.complexity_mapping = {
            "simple": {"min_paths": 10, "max_paths": 50, "detail_level": 1},
            "medium": {"min_paths": 50, "max_paths": 150, "detail_level": 2},
            "complex": {"min_paths": 150, "max_paths": 300, "detail_level": 3}
        }

        logger.info("[BOB AI] SVG Generator initialized")

    def _load_style_definitions(self) -> Dict[str, Dict]:
        """Load design style definitions"""
        return {
            "geometric": {
                "description": "Clean lines, mathematical precision, symmetry",
                "keywords": "geometric symmetric precise mathematical clean grid pattern",
                "svg_elements": ["circles", "rectangles", "polygons", "lines"],
                "stroke_style": "solid"
            },
            "organic": {
                "description": "Flowing curves, natural feel, smooth transitions",
                "keywords": "organic flowing curves natural smooth wavy fluid",
                "svg_elements": ["bezier curves", "circles", "ellipses"],
                "stroke_style": "rounded"
            },
            "abstract": {
                "description": "Artistic interpretation, expressive forms",
                "keywords": "abstract artistic expressive creative interpretation",
                "svg_elements": ["irregular paths", "organic shapes", "varied curves"],
                "stroke_style": "varied"
            },
            "decorative": {
                "description": "Ornamental elements, borders, frames",
                "keywords": "decorative ornamental embellished border frame pattern",
                "svg_elements": ["repeated patterns", "flourishes", "borders"],
                "stroke_style": "ornate"
            },
            "technical": {
                "description": "Mechanical precision, technical specs, components",
                "keywords": "technical mechanical precise component schematic blueprint",
                "svg_elements": ["lines", "rectangles", "crosses", "grid"],
                "stroke_style": "solid"
            },
            "artistic": {
                "description": "Expressive, mixed techniques, creative freedom",
                "keywords": "artistic expressive creative mixed techniques style",
                "svg_elements": ["varied shapes", "mixed curves", "freeform"],
                "stroke_style": "mixed"
            }
        }

    def generate_from_text(self, prompt: str, style: str = "geometric",
                           complexity: str = "medium") -> Dict[str, Any]:
        """
        Generate SVG from text prompt using local LLM

        Args:
            prompt: Design description (e.g., "Celtic knot pattern")
            style: Design style (geometric, organic, abstract, decorative, technical, artistic)
            complexity: Complexity level (simple, medium, complex)

        Returns:
            Dict with svg_data, path_count, download_url
        """
        try:
            # Validate inputs
            if not prompt or not prompt.strip():
                return {"success": False, "error": "Prompt is required"}

            if style not in self.style_definitions:
                return {"success": False, "error": f"Unknown style: {style}"}

            if complexity not in self.complexity_mapping:
                return {"success": False, "error": f"Unknown complexity: {complexity}"}

            logger.info(f"[BOB AI] Generating SVG: prompt='{prompt}', style={style}, complexity={complexity}")

            # Create config
            config = SVGGenerationConfig(
                style=style,
                complexity=complexity,
                path_count_target=self.complexity_mapping[complexity]["max_paths"]
            )

            # Generate SVG using LLM
            svg_data = self._generate_svg_with_llm(prompt, config)

            if not svg_data:
                return {"success": False, "error": "Failed to generate SVG"}

            # Count paths in generated SVG
            path_count = self._count_paths(svg_data)

            # Save to file
            file_id = str(uuid.uuid4())[:8]
            filename = f"vector_{file_id}.svg"
            filepath = self.output_dir / filename

            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(svg_data)

            logger.info(f"[BOB AI] SVG generated: {path_count} paths, saved to {filename}")

            return {
                "success": True,
                "svgData": svg_data,
                "pathCount": path_count,
                "downloadUrl": f"/downloads/{filename}",
                "style": style,
                "complexity": complexity
            }

        except Exception as e:
            logger.error(f"[BOB AI] SVG generation error: {e}")
            return {"success": False, "error": str(e)}

    def _generate_svg_with_llm(self, prompt: str, config: SVGGenerationConfig) -> Optional[str]:
        """
        Use local LLM (Mistral) to generate SVG code

        Args:
            prompt: User's design description
            config: SVG generation configuration

        Returns:
            SVG string or None if generation fails
        """
        try:
            # Get style details
            style_info = self.style_definitions[config.style]
            complexity_info = self.complexity_mapping[config.complexity]

            # Build LLM prompt for SVG generation
            system_prompt = """You are an expert SVG designer. Generate valid SVG code for design requests.

IMPORTANT REQUIREMENTS:
1. Return ONLY valid SVG code, no explanations
2. Use <svg viewBox="0 0 800 600"> as wrapper
3. Use <path> elements with d attribute for curves
4. Use <circle>, <rect>, <polygon> for shapes
5. Always include proper stroke and fill attributes
6. Keep SVG size under 100KB
7. Don't use CSS or style tags - use inline attributes only
8. Make sure SVG is valid and renders correctly"""

            user_prompt = f"""Generate an SVG design with these requirements:

DESIGN REQUEST: {prompt}

STYLE: {config.style}
- Description: {style_info['description']}
- Keywords: {style_info['keywords']}

COMPLEXITY: {config.complexity}
- Target paths: {complexity_info['min_paths']}-{complexity_info['max_paths']}
- Detail level: {complexity_info['detail_level']}/3

Return ONLY the SVG code, nothing else. Start with <svg and end with </svg>."""

            # Call local LLM
            if not self.ollama:
                logger.error("[BOB AI] Ollama manager not available")
                return self._generate_svg_fallback(prompt, config)

            # Generate using Mistral (synchronous call)
            try:
                response = self.ollama.generate_text(
                    prompt=user_prompt,
                    system=system_prompt,
                    model="mistral",
                    temperature=0.7,
                    max_tokens=2000
                )
            except Exception as e:
                logger.warning(f"[BOB AI] Ollama sync call error, trying with timeout: {e}")
                response = None

            if not response:
                logger.warning("[BOB AI] LLM generation failed, using fallback")
                return self._generate_svg_fallback(prompt, config)

            # Extract SVG from response
            svg_code = self._extract_svg(response)

            if not svg_code:
                logger.warning("[BOB AI] Failed to extract SVG from LLM response")
                return self._generate_svg_fallback(prompt, config)

            # Validate SVG
            if self._is_valid_svg(svg_code):
                logger.info("[BOB AI] SVG generated successfully by LLM")
                return svg_code
            else:
                logger.warning("[BOB AI] Generated SVG is invalid, using fallback")
                return self._generate_svg_fallback(prompt, config)

        except Exception as e:
            logger.error(f"[BOB AI] LLM generation error: {e}")
            return self._generate_svg_fallback(prompt, config)

    def _generate_svg_fallback(self, prompt: str, config: SVGGenerationConfig) -> str:
        """
        Fallback SVG generation using basic shapes
        Used when LLM is unavailable
        """
        try:
            if not SVGWRITE_AVAILABLE:
                # Manual SVG construction
                return self._build_svg_manually(prompt, config)

            # Use svgwrite library
            dwg = svgwrite.Drawing(size=(f"{config.width}px", f"{config.height}px"))
            dwg.viewbox(0, 0, config.width, config.height)

            # Extract keywords from prompt for style hints
            keywords = prompt.lower().split()

            # Simple geometric fallback
            if "circle" in keywords or "round" in keywords:
                for i in range(3):
                    dwg.add(dwg.circle(
                        center=(150 + i*200, 300),
                        r=80,
                        fill="none",
                        stroke="black",
                        stroke_width=2
                    ))
            elif "square" in keywords or "rectangle" in keywords:
                for i in range(2):
                    dwg.add(dwg.rect(
                        (50 + i*300, 100),
                        (300, 400),
                        fill="none",
                        stroke="black",
                        stroke_width=2
                    ))
            else:
                # Default: decorative pattern
                self._add_pattern_to_svg(dwg, config)

            svg_string = dwg.tostring()
            logger.info("[BOB AI] Fallback SVG generated using svgwrite")
            return svg_string

        except Exception as e:
            logger.warning(f"[BOB AI] Fallback generation error: {e}")
            return self._build_svg_manually(prompt, config)

    def _build_svg_manually(self, prompt: str, config: SVGGenerationConfig) -> str:
        """
        Build SVG manually without external libraries
        This is the ultimate fallback
        """
        svg_lines = [
            f'<svg viewBox="0 0 {config.width} {config.height}" xmlns="http://www.w3.org/2000/svg">',
            '<style>rect { fill: none; stroke: #333; stroke-width: 2; }</style>',
        ]

        # Add geometric shapes based on complexity
        complexity_info = self.complexity_mapping[config.complexity]

        if config.complexity == "simple":
            # 3-5 simple shapes
            svg_lines.extend([
                f'<circle cx="200" cy="200" r="80" fill="none" stroke="black" stroke-width="2"/>',
                f'<rect x="350" y="100" width="200" height="200" fill="none" stroke="black" stroke-width="2"/>',
            ])
        elif config.complexity == "medium":
            # 5-10 shapes with pattern
            svg_lines.extend([
                f'<circle cx="200" cy="150" r="60" fill="none" stroke="black" stroke-width="2"/>',
                f'<circle cx="400" cy="150" r="60" fill="none" stroke="black" stroke-width="2"/>',
                f'<circle cx="600" cy="150" r="60" fill="none" stroke="black" stroke-width="2"/>',
                f'<path d="M 100 300 Q 200 400 300 300 Q 400 200 500 300" fill="none" stroke="black" stroke-width="2"/>',
                f'<polygon points="50,450 150,350 250,450" fill="none" stroke="black" stroke-width="2"/>',
            ])
        else:  # complex
            # Multiple overlapping shapes
            for i in range(8):
                x = 100 + i * 80
                y = 150 + (i % 3) * 100
                svg_lines.append(f'<circle cx="{x}" cy="{y}" r="40" fill="none" stroke="black" stroke-width="1.5" opacity="0.7"/>')

            # Add some paths
            svg_lines.extend([
                f'<path d="M 50 400 Q 200 350 350 400 Q 500 450 650 400" fill="none" stroke="black" stroke-width="2"/>',
                f'<path d="M 100 450 L 200 350 L 300 450 L 400 350 L 500 450" fill="none" stroke="black" stroke-width="1.5"/>',
            ])

        svg_lines.append('</svg>')

        svg_data = '\n'.join(svg_lines)
        logger.info("[BOB AI] SVG built manually without external libraries")
        return svg_data

    def _add_pattern_to_svg(self, dwg, config: SVGGenerationConfig):
        """Add decorative pattern to SVG drawing"""
        # Add grid pattern
        for x in range(0, config.width, 100):
            dwg.add(dwg.line(
                start=(x, 0),
                end=(x, config.height),
                stroke="lightgray",
                stroke_width=1
            ))

        for y in range(0, config.height, 100):
            dwg.add(dwg.line(
                start=(0, y),
                end=(config.width, y),
                stroke="lightgray",
                stroke_width=1
            ))

        # Add decorative circles
        for i in range(2):
            for j in range(2):
                dwg.add(dwg.circle(
                    center=(200 + i*400, 200 + j*200),
                    r=100,
                    fill="none",
                    stroke="black",
                    stroke_width=2
                ))

    def enhance_vector(self, svg_data: str, enhancement_type: str,
                       **kwargs) -> Dict[str, Any]:
        """
        Enhance existing SVG vector

        Args:
            svg_data: Current SVG content
            enhancement_type: "simplify", "complexify", "stylize", or "custom"
            **kwargs: Additional parameters (prompt for custom, target paths for simplify/complexify)

        Returns:
            Dict with enhanced svg_data, metrics
        """
        try:
            current_path_count = self._count_paths(svg_data)
            logger.info(f"[BOB AI] Enhancing vector: type={enhancement_type}, current_paths={current_path_count}")

            if enhancement_type == "simplify":
                target = kwargs.get("targetPathCount", 50)
                enhanced_svg = self._simplify_svg(svg_data, target)
                new_path_count = self._count_paths(enhanced_svg)
                reduction = ((current_path_count - new_path_count) / current_path_count * 100) if current_path_count > 0 else 0

                return {
                    "success": True,
                    "svgData": enhanced_svg,
                    "pathCount": new_path_count,
                    "reductionPercent": round(reduction, 1),
                    "enhancement": "simplify"
                }

            elif enhancement_type == "complexify":
                target = kwargs.get("targetPathCount", 200)
                enhanced_svg = self._complexify_svg(svg_data, target)
                new_path_count = self._count_paths(enhanced_svg)
                increase = ((new_path_count - current_path_count) / current_path_count * 100) if current_path_count > 0 else 0

                return {
                    "success": True,
                    "svgData": enhanced_svg,
                    "pathCount": new_path_count,
                    "increasePercent": round(increase, 1),
                    "enhancement": "complexify"
                }

            elif enhancement_type == "stylize":
                prompt = kwargs.get("prompt", "Add artistic styling")
                enhanced_svg = self._stylize_svg(svg_data, prompt)
                new_path_count = self._count_paths(enhanced_svg)

                return {
                    "success": True,
                    "svgData": enhanced_svg,
                    "pathCount": new_path_count,
                    "enhancement": "stylize"
                }

            elif enhancement_type == "custom":
                prompt = kwargs.get("prompt")
                if not prompt:
                    return {"success": False, "error": "Custom prompt is required"}

                enhanced_svg = self._custom_enhance_svg(svg_data, prompt)
                new_path_count = self._count_paths(enhanced_svg)

                return {
                    "success": True,
                    "svgData": enhanced_svg,
                    "pathCount": new_path_count,
                    "enhancement": "custom"
                }

            else:
                return {"success": False, "error": f"Unknown enhancement type: {enhancement_type}"}

        except Exception as e:
            logger.error(f"[BOB AI] Vector enhancement error: {e}")
            return {"success": False, "error": str(e)}

    def _simplify_svg(self, svg_data: str, target_paths: int) -> str:
        """Simplify SVG by reducing path count"""
        try:
            # Use LLM to generate simplified version
            prompt = f"""Simplify this SVG to approximately {target_paths} paths. Keep the main design visible but remove fine details.

Return ONLY the simplified SVG code:

{svg_data}"""

            if self.ollama:
                try:
                    response = self.ollama.generate_text(
                        prompt=prompt,
                        model="mistral",
                        temperature=0.5,
                        max_tokens=2000
                    )

                    if response:
                        simplified_svg = self._extract_svg(response)
                        if simplified_svg and self._is_valid_svg(simplified_svg):
                            return simplified_svg
                except Exception as e:
                    logger.warning(f"[BOB AI] LLM simplify error: {e}")

            # Fallback: use regex to remove details
            return self._remove_fine_details(svg_data, target_paths)

        except Exception as e:
            logger.warning(f"[BOB AI] Simplify error: {e}")
            return svg_data

    def _complexify_svg(self, svg_data: str, target_paths: int) -> str:
        """Add complexity to SVG by increasing path count"""
        try:
            prompt = f"""Add details and complexity to this SVG to approximately {target_paths} paths. Keep the same overall design but add more intricate details, patterns, and decorative elements.

Return ONLY the enhanced SVG code:

{svg_data}"""

            if self.ollama:
                try:
                    response = self.ollama.generate_text(
                        prompt=prompt,
                        model="mistral",
                        temperature=0.7,
                        max_tokens=2000
                    )

                    if response:
                        complex_svg = self._extract_svg(response)
                        if complex_svg and self._is_valid_svg(complex_svg):
                            return complex_svg
                except Exception as e:
                    logger.warning(f"[BOB AI] LLM complexify error: {e}")

            # Fallback: add decorative elements
            return self._add_decorative_elements(svg_data)

        except Exception as e:
            logger.warning(f"[BOB AI] Complexify error: {e}")
            return svg_data

    def _stylize_svg(self, svg_data: str, style_prompt: str) -> str:
        """Apply artistic styling to SVG"""
        try:
            prompt = f"""Apply artistic styling to this SVG based on this description: {style_prompt}

Modify colors, strokes, patterns, and decorative elements to match the style. Keep the core design recognizable.

Return ONLY the styled SVG code:

{svg_data}"""

            if self.ollama:
                try:
                    response = self.ollama.generate_text(
                        prompt=prompt,
                        model="mistral",
                        temperature=0.7,
                        max_tokens=2000
                    )

                    if response:
                        styled_svg = self._extract_svg(response)
                        if styled_svg and self._is_valid_svg(styled_svg):
                            return styled_svg
                except Exception as e:
                    logger.warning(f"[BOB AI] LLM stylize error: {e}")

            return svg_data

        except Exception as e:
            logger.warning(f"[BOB AI] Stylize error: {e}")
            return svg_data

    def _custom_enhance_svg(self, svg_data: str, custom_prompt: str) -> str:
        """Apply custom modifications to SVG based on user prompt"""
        try:
            prompt = f"""Modify this SVG according to this request: {custom_prompt}

Apply the requested changes while keeping the design recognizable and valid SVG.

Return ONLY the modified SVG code:

{svg_data}"""

            if self.ollama:
                try:
                    response = self.ollama.generate_text(
                        prompt=prompt,
                        model="mistral",
                        temperature=0.7,
                        max_tokens=2000
                    )

                    if response:
                        custom_svg = self._extract_svg(response)
                        if custom_svg and self._is_valid_svg(custom_svg):
                            return custom_svg
                except Exception as e:
                    logger.warning(f"[BOB AI] LLM custom enhance error: {e}")

            return svg_data

        except Exception as e:
            logger.warning(f"[BOB AI] Custom enhance error: {e}")
            return svg_data

    def _extract_svg(self, response: str) -> Optional[str]:
        """Extract SVG code from LLM response"""
        # Look for SVG tags
        svg_start = response.find('<svg')
        svg_end = response.rfind('</svg>') + len('</svg>')

        if svg_start != -1 and svg_end > svg_start:
            return response[svg_start:svg_end]

        return None

    def _is_valid_svg(self, svg_data: str) -> bool:
        """Check if SVG is valid"""
        try:
            # Basic validation
            if not svg_data.strip().startswith('<svg'):
                return False
            if not svg_data.strip().endswith('</svg>'):
                return False
            if '<' not in svg_data or '>' not in svg_data:
                return False

            # Count opening and closing tags
            open_count = svg_data.count('<')
            close_count = svg_data.count('>')

            return open_count > 0 and open_count == close_count

        except Exception:
            return False

    def _count_paths(self, svg_data: str) -> int:
        """Count number of path elements in SVG"""
        try:
            # Count <path> tags
            path_count = svg_data.count('<path')
            # Count other shape elements
            path_count += svg_data.count('<circle')
            path_count += svg_data.count('<rect')
            path_count += svg_data.count('<polygon')
            path_count += svg_data.count('<line')
            path_count += svg_data.count('<polyline')
            path_count += svg_data.count('<ellipse')

            return max(1, path_count)  # At least 1

        except Exception:
            return 1

    def _remove_fine_details(self, svg_data: str, target_paths: int) -> str:
        """Remove fine details from SVG (fallback simplification)"""
        # This is a simple heuristic - removes small paths and opacity effects
        lines = svg_data.split('\n')
        kept_lines = []
        path_count = 0
        max_paths = target_paths

        for line in lines:
            # Keep structural tags
            if '<svg' in line or '</svg>' in line or 'viewBox' in line or 'xmlns' in line or '<style' in line or '</style>' in line or '<defs' in line or '</defs>' in line:
                kept_lines.append(line)
            # Skip very small elements
            elif 'r="[0-5]"' in line or 'stroke-width="0' in line:
                continue
            # Skip high opacity (transparency)
            elif 'opacity="0.' in line:
                continue
            # Keep major paths
            elif '<path' in line or '<circle' in line or '<rect' in line or '<polygon' in line:
                if path_count < max_paths:
                    kept_lines.append(line)
                    path_count += 1
            else:
                kept_lines.append(line)

        return '\n'.join(kept_lines)

    def _add_decorative_elements(self, svg_data: str) -> str:
        """Add decorative elements to SVG (fallback complexification)"""
        # Find the closing </svg> tag and insert decorative elements before it
        svg_end = svg_data.rfind('</svg>')

        if svg_end == -1:
            return svg_data

        # Extract viewBox to determine dimensions
        viewbox_match = re.search(r'viewBox="0 0 (\d+) (\d+)"', svg_data)
        if not viewbox_match:
            width, height = 800, 600
        else:
            width = int(viewbox_match.group(1))
            height = int(viewbox_match.group(2))

        # Add decorative elements
        decorative = [
            f'<!-- Decorative Elements -->',
            f'<g opacity="0.5">',
            f'  <circle cx="{width//4}" cy="{height//4}" r="30" fill="none" stroke="black" stroke-width="1"/>',
            f'  <circle cx="{3*width//4}" cy="{3*height//4}" r="30" fill="none" stroke="black" stroke-width="1"/>',
            f'  <path d="M {width//4} 0 L {width//4} {height}" stroke="lightgray" stroke-width="1" opacity="0.3"/>',
            f'  <path d="M 0 {height//4} L {width} {height//4}" stroke="lightgray" stroke-width="1" opacity="0.3"/>',
            f'</g>',
        ]

        return svg_data[:svg_end] + '\n'.join(decorative) + '\n</svg>'


# Singleton instance
_generator = None

def get_bob_ai_svg_generator() -> BobAISVGGenerator:
    """Get or create singleton SVG generator instance"""
    global _generator
    if _generator is None:
        _generator = BobAISVGGenerator()
    return _generator
