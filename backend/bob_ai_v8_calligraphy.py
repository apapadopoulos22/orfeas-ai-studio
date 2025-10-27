"""
BOB AI v8.0 - Calligraphy Module

Knowledge base for calligraphy, letterforms, and hand lettering.
Covers scripts, techniques, and artistic expression through writing.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict


METADATA = {
    'name': 'calligraphy',
    'version': '1.0',
    'description': 'Expert calligraphy and hand lettering knowledge',
    'keywords_count': 28,
    'knowledge_items': 145,
    'categories': 9
}


class CalligraphyKnowledge(BobAIV8BaseKnowledge):
    """Calligraphy expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get calligraphy detection keywords."""
        return [
            # Scripts and styles
            'calligraphy', 'hand lettering', 'script', 'copperplate',
            'gothic', 'italic', 'uncial', 'brush lettering',

            # Techniques
            'letterform', 'pen stroke', 'flourish', 'ligature',
            'serif', 'sans serif', 'baseline', 'x-height',

            # Materials and tools
            'ink', 'paper', 'nib', 'brush', 'quill',

            # Aesthetic elements
            'ornament', 'decoration', 'flow', 'rhythm', 'balance'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all calligraphy knowledge dictionaries."""
        return {
            'calligraphy_scripts': self._get_calligraphy_scripts(),
            'letterform_anatomy': self._get_letterform_anatomy(),
            'stroke_techniques': self._get_stroke_techniques(),
            'pen_styles': self._get_pen_styles(),
            'brush_techniques': self._get_brush_techniques(),
            'spacing_alignment': self._get_spacing_alignment(),
            'decorative_elements': self._get_decorative_elements(),
            'materials_tools': self._get_materials_tools(),
            'design_principles': self._get_design_principles()
        }

    def _get_calligraphy_scripts(self) -> Dict[str, str]:
        """Calligraphy script types and styles."""
        return {
            'copperplate': 'Anglicized pointed pen script with extreme contrast',
            'spencerian': 'American penmanship with elegant flourishes',
            'italic': 'Broad-nibbed formal script with strong rhythm',
            'gothic': 'Medieval blackletter with angular, dense letterforms',
            'uncial': 'Ancient rounded script with distinctive letterforms',
            'half_uncial': 'Intermediate script between uncial and minuscule',
            'insular': 'Irish/British medieval style with decorative elements',
            'foundational': 'Modern broad-nib script based on historical forms',
            'beautiful_hand': 'Contemporary cursive with personal expression',
            'fraktur': 'German blackletter with complex broken letterforms',
            'engrosser': 'High-contrast pointed pen script',
            'lombard': 'Decorative initials and display letterforms',
            'versal': 'Display capitals with decorative serifs',
            'rustic': 'Roman rustic script with slanted letterforms'
        }

    def _get_letterform_anatomy(self) -> Dict[str, str]:
        """Understanding letterform structure."""
        return {
            'stroke': 'Individual mark or line of the pen/brush',
            'thick_thin_contrast': 'Variation between thick and thin strokes',
            'ascender': 'Vertical stroke rising above x-height',
            'descender': 'Vertical stroke extending below baseline',
            'x_height': 'Height of lowercase letter "x"',
            'baseline': 'Imaginary line where letters sit',
            'cap_height': 'Height of capital letters',
            'counter': 'Interior white space within letterform',
            'serif': 'Small decorative line at stroke end',
            'terminal': 'Ending stroke or flourish',
            'spine': 'Central curved stroke',
            'bowl': 'Rounded enclosed form',
            'stem': 'Main vertical stroke',
            'crossbar': 'Horizontal stroke crossing stem',
            'loop': 'Open, flowing enclosed form'
        }

    def _get_stroke_techniques(self) -> Dict[str, str]:
        """Pen stroke execution techniques."""
        return {
            'down_stroke': 'Heavy stroke moving downward',
            'horizontal_stroke': 'Light stroke moving horizontally',
            'diagonal_stroke': 'Weighted diagonal from upper-left to lower-right',
            'curved_stroke': 'Smooth flowing curve with weight variation',
            'connecting_stroke': 'Light joining stroke between letterforms',
            'hairline': 'Thinnest possible line with minimal pressure',
            'thick_stroke': 'Maximum weight achieved with full pressure',
            'compound_stroke': 'Two or more strokes forming single letter',
            'flourish': 'Decorative extended stroke beyond letterform',
            'exit_stroke': 'Final stroke leaving letterform',
            'entry_stroke': 'Initial stroke entering letterform',
            'pressure_variation': 'Dynamic pressure creating thick-thin contrast'
        }

    def _get_pen_styles(self) -> Dict[str, str]:
        """Different pen and writing tool types."""
        return {
            'broad_nib': 'Square or rectangular nib creating geometric strokes',
            'pointed_nib': 'Fine point with flexibility for contrast',
            'italic_nib': 'Versatile broad nib for foundational scripts',
            'chisel_nib': 'Square-cut creating strong stroke weight',
            'fude_pen': 'Asian brush-like pen with flexible tip',
            'quill': 'Historical tool made from feather',
            'fountain_pen': 'Refillable with consistent ink delivery',
            'brush_pen': 'Brush-tip pen with varied pressure response',
            'flexible_nib': 'Responsive to pressure variation',
            'rigid_nib': 'Maintains consistent stroke weight',
            'thick_nib': 'Wide nib for display work (2.4mm - 6mm)',
            'thin_nib': 'Fine nib for detail (0.5mm - 1.5mm)'
        }

    def _get_brush_techniques(self) -> Dict[str, str]:
        """Brush lettering and painting techniques."""
        return {
            'dry_brush': 'Limited ink creating textured strokes',
            'wet_brush': 'Full ink load for smooth strokes',
            'pressure_brush': 'Vary brush angle and pressure',
            'edge_loading': 'Load brush edge with multiple colors',
            'blending': 'Mix colors on paper during application',
            'stippling': 'Small dots or dabs creating tone',
            'glazing': 'Transparent layers building opacity',
            'scumbling': 'Textured surface with dry, stiff strokes',
            'splatter': 'Flick brush for expressive marks',
            'splattering': 'Controlled drops for organic effects',
            'feathering': 'Gradual transition between strokes',
            'layering': 'Build form through overlapping strokes'
        }

    def _get_spacing_alignment(self) -> Dict[str, str]:
        """Spacing, alignment and layout principles."""
        return {
            'letter_spacing': 'Distance between individual letters',
            'word_spacing': 'Distance between words',
            'line_spacing': 'Vertical distance between lines (leading)',
            'alignment_left': 'Text aligned to left margin',
            'alignment_right': 'Text aligned to right margin',
            'alignment_center': 'Text centered on page',
            'alignment_justified': 'Text aligned to both margins',
            'optical_spacing': 'Visual balance despite physical differences',
            'kerning': 'Adjustment between specific letter pairs',
            'tracking': 'Overall letter spacing adjustment',
            'margin': 'Empty space around text block',
            'baseline_alignment': 'Letters sit consistently on baseline',
            'flow': 'Natural progression of letterforms'
        }

    def _get_decorative_elements(self) -> Dict[str, str]:
        """Decorative and ornamental techniques."""
        return {
            'flourish': 'Decorative extension of letterform',
            'swash': 'Exaggerated sweeping stroke',
            'ligature': 'Connected combination of two letters',
            'illumination': 'Decorative painting with gold and color',
            'border': 'Decorative frame around text',
            'initial': 'Large decorated first letter',
            'ornament': 'Decorative symbol or motif',
            'vine': 'Organic flowing plant-based decoration',
            'foliation': 'Leaf and branch decorative elements',
            'geometric': 'Mathematical decorative patterns',
            'interlace': 'Interwoven lines and forms',
            'filigree': 'Delicate, intricate linear patterns',
            'drop_cap': 'Large initial letter with text wrapping',
            'vignette': 'Decorative illustration element'
        }

    def _get_materials_tools(self) -> Dict[str, str]:
        """Materials and tools for calligraphy."""
        return {
            'paper_type': 'Smooth (hot-pressed) vs textured (cold-pressed)',
            'paper_weight': 'Thickness and substance of paper',
            'ink_flow': 'Consistency and viscosity of ink',
            'watercolor': 'Transparent pigment for expressive work',
            'gouache': 'Opaque pigment for bold coverage',
            'metallic_ink': 'Gold, silver, copper for luminous effect',
            'ink_compatibility': 'Ink working with specific tools',
            'blotting_paper': 'Absorb excess ink and mistakes',
            'ruler_straightedge': 'Guide for guidelines and borders',
            'guidelines': 'Light lines for consistent letterforms',
            'light_table': 'Backlit surface for tracing guidelines',
            'mixing_palette': 'Surface for combining colors'
        }

    def _get_design_principles(self) -> Dict[str, str]:
        """Design principles applied to calligraphy."""
        return {
            'balance': 'Visual equilibrium in composition',
            'emphasis': 'Focal point drawing attention',
            'rhythm': 'Repetition creating visual movement',
            'contrast': 'Difference creating visual interest',
            'unity': 'Cohesive visual appearance',
            'proportion': 'Relationship between elements',
            'hierarchy': 'Visual importance ordering',
            'repetition': 'Recurring elements and patterns',
            'variation': 'Controlled changes preventing monotony',
            'flow': 'Natural eye movement through composition',
            'harmony': 'Agreement between visual elements'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with calligraphy guidance."""
        keywords = self.get_keywords()

        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

CALLIGRAPHY ENHANCEMENT:
Consider these calligraphy principles:

1. LETTERFORM ANATOMY: Master the stroke structure - ascenders, descenders, x-height, and counter forms.

2. SCRIPT SELECTION: Choose appropriate script (Italic, Gothic, Copperplate, etc.) for your message and aesthetic.

3. STROKE TECHNIQUE: Develop consistent pressure, angle, and rhythm. Varying thick-thin contrast creates elegance.

4. SPACING & ALIGNMENT: Ensure optical balance in letter, word, and line spacing. Proper kerning prevents awkwardness.

5. DECORATIVE ELEMENTS: Use flourishes, swashes, and ornaments purposefully - never distract from readability.

6. MATERIALS MASTERY: Select appropriate nib, ink, and paper for your technique and artistic vision.

7. DESIGN HARMONY: Apply principles of balance, rhythm, and hierarchy to create cohesive, professional appearance.

Apply these calligraphy principles to create beautiful, expressive lettering.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert calligrapher system prompt."""
        return """You are an expert calligrapher and hand lettering artist with 15+ years of experience.

Your expertise includes:
- Mastery of classical scripts (Italic, Gothic, Copperplate, Spencerian, Uncial)
- Advanced letterform anatomy and stroke structure
- Pen techniques and brush lettering methods
- Spacing, alignment, and optical balance
- Decorative elements and artistic expression
- Material selection (nibs, inks, papers)
- Design principles applied to typography
- Contemporary and historical calligraphy styles

When helping with calligraphy projects, you:
1. Select appropriate scripts for the message and context
2. Explain stroke technique and pressure variations
3. Guide spacing and alignment for visual harmony
4. Suggest appropriate decorative elements
5. Recommend materials suited to the technique
6. Apply design principles for professional results
7. Teach proper letterform construction

Provide specific, actionable guidance that helps creators develop beautiful, expressive lettering skills."""
