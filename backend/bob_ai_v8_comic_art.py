"""
BOB AI v8.0 - Comic Art Knowledge Module

Comprehensive knowledge base for comic art expertise including visual storytelling,
panel layouts, character design, inking, coloring, lettering, and sequential narrative.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge


class ComicArtKnowledge(BobAIV8BaseKnowledge):
    """Comic art domain knowledge and expertise."""

    METADATA = {
        'discipline': 'Comic Art',
        'version': '1.0',
        'author': 'BOB AI v8.0',
        'category': 'Visual Arts & Storytelling',
        'knowledge_items': 180,
        'keywords_count': 52,
        'expertise_level': 'Professional (10+ years comic creation)',
        'primary_use': 'Comic creation, illustration, sequential narrative design',
        'secondary_uses': ['manga creation', 'graphic novels', 'comic instruction', 'storyboarding', 'character design'],
        'domain_keywords': ['comic', 'panel', 'sequential', 'art', 'illustration']
    }

    def get_keywords(self) -> list:
        """Return comic art domain keywords."""
        return [
            'comic', 'comic art', 'art', 'panel', 'sequential',
            'illustration', 'character', 'character design', 'ink', 'inking',
            'color', 'coloring', 'lettering', 'dialogue', 'balloon',
            'layout', 'composition', 'panel layout', 'pacing', 'visual',
            'storytelling', 'narrative', 'manga', 'graphic novel',
            'action', 'perspective', 'anatomy', 'drawing', 'style',
            'pencil', 'pen', 'digital art', 'graphic tablet',
            'sound effects', 'line weight', 'shading', 'hatching',
            'background', 'foreground', 'depth', 'framing',
            'transition', 'sequence', 'expression', 'pose'
        ]

    def get_knowledge_dictionaries(self) -> dict:
        """Return all comic art knowledge dictionaries."""
        return {
            'visual_storytelling': self._get_visual_storytelling(),
            'panel_layout': self._get_panel_layout(),
            'composition': self._get_composition(),
            'character_design': self._get_character_design(),
            'inking_techniques': self._get_inking_techniques(),
            'coloring_methods': self._get_coloring_methods(),
            'lettering': self._get_lettering(),
            'dialogue_balloons': self._get_dialogue_balloons(),
            'pacing': self._get_pacing(),
            'sequential_narrative': self._get_sequential_narrative(),
            'comic_genres': self._get_comic_genres(),
            'manga_specific': self._get_manga_specific(),
            'art_fundamentals': self._get_art_fundamentals(),
            'industry_knowledge': self._get_industry_knowledge()
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with comic art context if applicable."""
        comic_keywords = self.get_keywords()
        prompt_lower = prompt.lower()

        if any(kw in prompt_lower for kw in comic_keywords):
            knowledge_items = []

            if any(kw in prompt_lower for kw in ['layout', 'panel', 'page']):
                knowledge_items.extend(list(self._get_panel_layout().values())[:3])

            if any(kw in prompt_lower for kw in ['character', 'design', 'figure']):
                knowledge_items.extend(list(self._get_character_design().values())[:3])

            if any(kw in prompt_lower for kw in ['color', 'ink', 'technique']):
                knowledge_items.extend(list(self._get_coloring_methods().values())[:3])

            if any(kw in prompt_lower for kw in ['story', 'narrative', 'sequential']):
                knowledge_items.extend(list(self._get_sequential_narrative().values())[:3])

            if knowledge_items:
                context = '\n'.join(f'• {item}' for item in knowledge_items[:6])
                return f"{prompt}\n\n[COMIC ART CONTEXT]\n{context}"

        return prompt

    def generate_system_prompt(self) -> str:
        """Generate expert comic artist system prompt."""
        return """You are a professional comic artist and writer with 10+ years of experience creating
sequential art, graphic novels, and manga. Your expertise spans from concept through finished publication-ready artwork.

KEY RESPONSIBILITIES:
1. Guide comic creation from concept to finished product
2. Explain visual storytelling principles and techniques
3. Provide composition and layout advice
4. Teach character design and development
5. Share inking, coloring, and lettering techniques
6. Help with pacing and narrative flow
7. Address technical and creative challenges
8. Support artists across skill levels and styles

EXPERTISE AREAS:
• Visual storytelling: Conveying narrative through images
• Panel layout: Grid design, gutters, spatial relationships
• Composition: Balance, focal points, visual flow
• Character design: Silhouette, proportion, distinctive features
• Inking: Line weight, texture, depth communication
• Coloring: Color theory, mood, separation, printing
• Lettering: Font choice, balloon placement, hierarchy
• Dialogue: Natural speech, subtext, character voice
• Pacing: Scene pacing, beat timing, rhythm
• Sequential narrative: Page structure, transitions, timing
• Manga specific: Right-to-left reading, visual conventions
• Genre conventions: Superhero, realistic, experimental
• Art fundamentals: Anatomy, perspective, light, shadow
• Industry standards: Comics, manga, graphic novels, webcomics

TEACHING APPROACH:
• Practical: Include specific techniques and workflows
• Progressive: From concept to final production
• Referenced: Draw from industry best practices
• Encouraging: Acknowledge growth and experimentation
• Technical: Explain mechanical and software aspects
• Creative: Support artistic vision and style development

COMMON MISCONCEPTIONS TO ADDRESS:
• Comics are simplified drawings (actually highly refined technique)
• Manga requires specific art style (manga is format, many styles exist)
• Colored comics are easier than black/white (different not easier)
• Digital art is less skilled than traditional (same skills, different tools)
• Speech balloons are placed last (planned in layouts from start)
• Fast drawing means less skilled (speed comes from practice and skill)

When helping with comics, prioritize clear visual explanation, professional standards, and practical application."""

    def _get_visual_storytelling(self) -> dict:
        """Visual storytelling principles."""
        return {
            'show_dont_tell': 'Use visuals to communicate; avoid text explaining what image shows',
            'panel_pacing': 'Panel size and timing control how quickly reader moves through story',
            'visual_metaphor': 'Use visual elements symbolically to enhance meaning',
            'emotional_composition': 'Layout, angle, and framing convey emotional tone',
            'body_language': 'Character poses and gestures tell story without dialogue',
            'facial_expression': 'Eyes and face convey emotion more powerfully than words',
            'environmental_storytelling': 'Background and setting provide context and mood',
            'visual_continuity': 'Consistent visual language helps readers follow story',
            'contrast_emphasis': 'Contrast draws attention to important story elements',
            'negative_space': 'Empty space guides reader eye and creates breathing room',
            'leading_lines': 'Lines in composition guide reader through sequence',
            'focal_point': 'Clear focal point controls what reader looks at first',
            'depth_layering': 'Foreground/midground/background create spatial depth',
            'symbolic_color': 'Color choices support emotional and thematic storytelling',
            'visual_rhythm': 'Repetition and variation create visual cohesion'
        }

    def _get_panel_layout(self) -> dict:
        """Panel layout and page composition."""
        return {
            'grid_layout': 'Standard grids (3x3, 4x4) provide structure and rhythm',
            'symmetrical_grid': 'Even grids feel stable and organized',
            'asymmetrical_layout': 'Varied panel sizes create dynamic, irregular feel',
            'splash_page': 'Single large image for dramatic impact or transitions',
            'action_flow': 'Panel arrangement guides reader eyes through action',
            'gutter_space': 'Space between panels - reader imagines action there',
            'wide_panels': 'Horizontal panels feel expansive, open, natural',
            'tall_panels': 'Vertical panels feel restrictive, focused, intimate',
            'square_panels': 'Neutral, stable feeling',
            'irregular_shapes': 'Non-rectangular panels create visual interest and emotion',
            'overlapping_panels': 'Panels breaking boundaries create dynamic tension',
            'inset_panels': 'Small panel within larger for detail or reaction',
            'page_flow': 'Logical progression guides reader left-right, top-bottom',
            'six_panel_grid': 'Industry standard allows good pacing and flexibility',
            'full_page_layout': 'Composition of all panels creates cohesive page image'
        }

    def _get_composition(self) -> dict:
        """Composition and visual balance."""
        return {
            'rule_of_thirds': 'Divide composition into thirds for balanced focal points',
            'center_composition': 'Central focal point feels stable, formal',
            'asymmetrical_balance': 'Off-center elements create dynamic tension',
            'leading_lines': 'Lines guide viewer through composition naturally',
            'framing': 'Use elements to frame focal point within composition',
            'perspective': 'Proper perspective creates convincing depth',
            'point_of_view': 'Camera angle conveys emotional perspective',
            'low_angle': 'Looking up makes subject powerful, imposing',
            'high_angle': 'Looking down makes subject weak, vulnerable',
            'dutch_angle': 'Tilted frame creates unease and tension',
            'close_up': 'Tight framing creates intimacy and emotional intensity',
            'wide_shot': 'Pulls back to show environmental context',
            'atmospheric_perspective': 'Size, detail, and color change with distance',
            'overlapping': 'Objects in front appear closer than objects behind',
            'consistent_space': 'Geography must make logical sense across pages'
        }

    def _get_character_design(self) -> dict:
        """Character design principles."""
        return {
            'silhouette_distinctiveness': 'Character recognizable by outline alone',
            'unique_features': 'Distinctive characteristics make character memorable',
            'shape_language': 'Body shapes suggest character personality and role',
            'costume_design': 'Clothing reflects character role, era, personality',
            'proportions': 'Consistent proportions maintain character throughout',
            'head_shapes': 'Head shape contributes to character personality',
            'facial_features': 'Exaggeration and simplification create style',
            'eye_expression': 'Eyes convey character emotion and personality most powerfully',
            'hair_design': 'Distinctive hairstyles aid recognition and character',
            'body_type': 'Body shape and size communicate character type and role',
            'stance': 'Resting pose reveals character personality',
            'gesture': 'Movement and gesture express character emotion and intent',
            'costume_consistency': 'Characters wear consistent clothing throughout',
            'emotional_flexibility': 'Design allows character to show range of emotions',
            'cultural_specificity': 'Design reflects character background and heritage'
        }

    def _get_inking_techniques(self) -> dict:
        """Inking and line work techniques."""
        return {
            'line_weight_variation': 'Thicker lines for emphasis, thinner for details',
            'contour_lines': 'Lines follow form to show volume and mass',
            'hatching': 'Parallel lines create shadow and texture',
            'cross_hatching': 'Intersecting lines create deeper shadow',
            'stippling': 'Dots create tone and texture',
            'texture_marks': 'Marks indicate surface quality: rough, smooth, etc',
            'feathering': 'Lines gradually tapering create soft edges',
            'tapered_lines': 'Line thickness variation adds elegance',
            'consistent_direction': 'Hatching direction creates sense of form',
            'shadow_shapes': 'Shadow areas defined as simple, readable shapes',
            'high_contrast': 'Strong black/white distinction creates visual punch',
            'expressive_mark': 'Ink marks carry personality and hand of artist',
            'edge_definition': 'Clear edges separate foreground from background',
            'white_space_preservation': 'Unink areas create breathing room',
            'technical_precision': 'Clean, professional linework quality'
        }

    def _get_coloring_methods(self) -> dict:
        """Coloring and color theory."""
        return {
            'color_theory_basics': 'Warm/cool, primary/secondary/tertiary colors',
            'complementary_colors': 'Opposite colors on wheel create vibrant contrast',
            'analogous_colors': 'Adjacent colors create harmony',
            'color_harmony': 'Limited palette creates cohesive feel',
            'color_mood': 'Color choices establish emotional tone of scene',
            'warm_colors_advance': 'Red, orange, yellow come forward visually',
            'cool_colors_recede': 'Blue, green, purple go back in space',
            'local_color': 'Actual object color modified by light and shadow',
            'atmospheric_color': 'Distant objects become cooler and less saturated',
            'saturation_control': 'More saturated colors feel closer, less saturated further',
            'value_contrast': 'Light/dark contrast more important than color contrast',
            'character_color_coding': 'Characters get distinct color palettes for recognition',
            'scene_color_palette': 'Limited palette creates unified look',
            'light_source_color': 'Light color tints surrounding areas',
            'printing_considerations': 'Colors must separate properly for print production'
        }

    def _get_lettering(self) -> dict:
        """Comic lettering principles."""
        return {
            'letterer_role': 'Lettering is craft requiring specific training and skill',
            'hand_lettering': 'Hand-drawn lettering has unique character and personality',
            'digital_fonts': 'Comic-specific fonts designed for readability',
            'balloon_containment': 'Text fits within balloon without cramming',
            'text_size': 'Dialogue size contrasts with captions and sound effects',
            'emphasis_technique': 'Bolder or larger text for emphasis or shouting',
            'font_consistency': 'Consistent font throughout maintains professionalism',
            'character_voice': 'Different fonts can distinguish character voices',
            'legibility': 'Text must be easily readable in printed reproduction',
            'hierarchy': 'Text size and placement guide reading order',
            'special_lettering': 'Distorted, shaky text conveys emotion',
            'thought_bubbles': 'Rounded-cloud shapes indicate thought',
            'whisper_effect': 'Thin lines or special style for quiet speech',
            'phonetic_writing': 'Informal spelling shows character dialect or voice',
            'caption_style': 'Narrative captions distinguished by box or style'
        }

    def _get_dialogue_balloons(self) -> dict:
        """Dialogue balloon design and placement."""
        return {
            'speech_bubble': 'Standard round balloon for normal dialogue',
            'thought_bubble': 'Cloud shape indicates character thought',
            'narrative_box': 'Rectangular box for narrator or scene setting',
            'jagged_bubble': 'Angry or intense emotion shown with rough edges',
            'cloud_whisper': 'Soft, diffuse shape for quiet speech',
            'electric_burst': 'Jagged spiky shape for electronic or alien voices',
            'caption_box': 'Traditional rectangular narrative caption',
            'pointed_tail': 'Tail indicates which character is speaking',
            'tail_direction': 'Tail points toward speaker, away from listener',
            'no_tail': 'Off-panel speaker when tail point off-page',
            'balloon_placement': 'Positioned to establish reading order and flow',
            'overlap_strategy': 'Balloons overlap to show dialogue timing',
            'balloon_size': 'Larger balloons for emphasis or shouting',
            'balloon_density': 'Avoid overcrowding with too many balloons',
            'emanation_symbol': 'Lines from mouth show speaking character'
        }

    def _get_pacing(self) -> dict:
        """Comic pacing and visual timing."""
        return {
            'panel_size_tempo': 'Large panels slow reading, tiny panels quicken pace',
            'action_sequence': 'Multiple small panels create sense of motion',
            'reaction_beat': 'Single larger panel allows reader to absorb emotion',
            'white_space_breath': 'Empty space creates pause for reader',
            'beat_timing': 'Panel sequence shows time between actions',
            'moment_emphasis': 'Large panel emphasizes key story moment',
            'quick_cut': 'Rapid panel transitions speed up action',
            'scene_transition': 'Larger panel between scenes slows momentum',
            'page_turn': 'Strategic page breaks create cliff-hangers or revelation',
            'reading_flow': 'Natural eye movement from panel to panel',
            'cliffhanger': 'Ending on dramatic moment compels page turn',
            'release_panel': 'Large panel after tension provides release',
            'silence_panels': 'Wordless panels can extend or compress time',
            'motion_lines': 'Speed lines suggest movement and velocity',
            'freeze_frame': 'Stopped moment stands out from action'
        }

    def _get_sequential_narrative(self) -> dict:
        """Sequential narrative techniques."""
        return {
            'cause_effect': 'Panel sequence shows clear cause and effect relationship',
            'temporal_sequence': 'Panels progress chronologically through time',
            'spatial_progression': 'Sequence moves through geographic space logically',
            'action_to_reaction': 'Action panel followed by reaction panel',
            'establishing_shot': 'Wide shot establishes location before action',
            'detail_shot': 'Close-up reveals important detail or emotion',
            'cut_back': 'Return to previous location or character',
            'parallel_action': 'Simultaneous events shown in alternating sequences',
            'flash_forward': 'Sequence jumps ahead to show future event',
            'flashback': 'Sequence returns to past event for context',
            'montage': 'Compressed time sequence of repeated action',
            'intercut': 'Rapid alternation between two action sequences',
            'build_climax': 'Escalating pacing and intensity toward climax',
            'resolution': 'Final sequence releases tension after climax',
            'denouement': 'Quiet sequence after action resolves character arcs'
        }

    def _get_comic_genres(self) -> dict:
        """Comic genre conventions and expectations."""
        return {
            'superhero': 'Action-driven, colorful, exaggerated anatomy and feats',
            'realistic': 'Detailed anatomy, realistic proportions, grounded style',
            'cartoonish': 'Simplified shapes, expressive distortion, stylized look',
            'horror': 'Dark value contrast, grotesque imagery, unsettling composition',
            'humor': 'Exaggerated expressions, sight gags, comedic timing',
            'adventure': 'Dynamic action, exotic locations, sense of discovery',
            'drama': 'Character focus, realistic emotion, subtle visual language',
            'noir': 'High contrast, shadows, moody atmosphere, vintage aesthetic',
            'sci_fi': 'Futuristic design, advanced technology, speculative elements',
            'fantasy': 'Magical elements, worldbuilding, non-realistic physics',
            'romance': 'Character focus, intimate framing, emotional expressions',
            'historical': 'Period-accurate details, setting research, authentic atmosphere',
            'experimental': 'Non-traditional layouts, innovative visual language',
            'comedy': 'Visual humor, exaggeration, playful distortion',
            'literary': 'Sophisticated narrative, subtle visual language, psychological depth'
        }

    def _get_manga_specific(self) -> dict:
        """Manga-specific conventions and techniques."""
        return {
            'right_to_left_reading': 'Traditional manga read right to left, top to bottom',
            'volume_format': 'Weekly serialization collected into tankobon volumes',
            'black_white_printing': 'Most manga printed in black and white, not color',
            'toned_backgrounds': 'Screentone adds texture and value variation efficiently',
            'speed_lines': 'Manga art style emphasizes speed line usage',
            'deformed_expressions': 'Chibi or super-deformed faces for comedy',
            'large_eyes': 'Big expressive eyes very common in manga',
            'emotional_symbols': 'Unique visual shorthand: sweat drop, anger vein, etc',
            'sound_effects': 'Sound effects integrated into artwork as lettering',
            'detail_hierarchy': 'Faces detailed, bodies less detailed than western comics',
            'screen_tone_patterns': 'Half-tone and pattern tones create tone and texture',
            'action_lines': 'Radiating lines behind character emphasize emotion',
            'visual_focus': 'Off-screen framing common, reader imagines action',
            'close_drama': 'Intimate character focus, psychological depth',
            'cultural_specificity': 'Visual language reflects Japanese aesthetic values'
        }

    def _get_art_fundamentals(self) -> dict:
        """Art fundamentals for comic creation."""
        return {
            'anatomy_knowledge': 'Understanding skeletal and muscular structure essential',
            'proportion_study': 'Head height as measurement unit for figure drawing',
            'perspective_rules': 'One, two, three-point perspective for environments',
            'light_shadow': 'Understanding light source informs value and shading',
            'gesture_drawing': 'Quick sketches capture movement and energy',
            'construction_method': 'Build complex forms from simple shapes',
            'foreshortening': 'Objects in depth appear compressed and distorted',
            'overlapping_planes': 'Planes facing different directions show form',
            'edge_quality': 'Soft edges recede, hard edges come forward',
            'atmospheric_effect': 'Distant objects lose detail and become cooler',
            'focal_distribution': 'Concentrate detail at focal point, simplify elsewhere',
            'stylization_balance': 'Style applied consistently while maintaining readability',
            'reference_usage': 'Using photo reference improves accuracy without tracing',
            'observation_skill': 'Direct observation develops drawing accuracy',
            'consistent_hand': 'Personal drawing style develops through practice and intent'
        }

    def _get_industry_knowledge(self) -> dict:
        """Comic industry standards and practices."""
        return {
            'page_dimensions': 'Standard comic size 6.625" x 10.1875" trimmed',
            'safe_area': 'Avoid critical elements near trim edges',
            'publication_formats': 'Single issues, graphic novels, manga, webcomics',
            'production_workflow': 'Pencil, ink, color, lettering, separation, printing',
            'freelance_model': 'Most comics created by freelancers for publishers',
            'submission_requirements': 'Portfolio, writing samples, professional presentation',
            'royalty_structure': 'Payment models vary: work-for-hire, royalties, profit sharing',
            'copyright_ownership': 'Understand who owns character and story rights',
            'convention_presence': 'Comic cons important for networking and sales',
            'self_publishing': 'Print-on-demand and digital distribution options available',
            'digital_comics': 'Webcomic and digital distribution changing industry',
            'international_market': 'Different standards for manga, european comics, etc',
            'editorial_process': 'Editors, publishers handle marketing and distribution',
            'professional_standards': 'Deadlines, specifications, and quality expectations',
            'artist_community': 'Collaborative and supportive creative community'
        }


def get_comic_art_knowledge():
    """Factory function to get comic art knowledge instance."""
    return ComicArtKnowledge()
