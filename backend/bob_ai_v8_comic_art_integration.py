"""
BOB AI v8.0 - Comic Art Integration

Integration layer connecting comic art knowledge with enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from typing import Tuple, Dict, List, Any


class ComicArtIntegration(BobAIV8IntegrationBase):
    """Comic art integration for visual narrative enhancement."""

    def __init__(self):
        """Initialize with comic art context parameters."""
        super().__init__()
        self.confidence_multipliers = {
            'comic': 1.4,
            'art': 1.3,
            'panel': 1.4,
            'character': 1.2,
            'illustration': 1.3,
            'sequential': 1.3,
            'visual': 1.2,
            'layout': 1.2,
            'manga': 1.3,
            'narrative': 1.2
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if comic art knowledge should apply."""
        prompt_lower = prompt.lower()

        # Check for comic art keywords
        comic_keywords = ['comic', 'comic art', 'panel', 'sequential', 'art', 'manga',
                         'graphic novel', 'illustration', 'character design', 'layout',
                         'storyboard', 'visual narrative', 'inking', 'coloring', 'lettering',
                         'dialogue balloon', 'panel layout', 'page layout', 'composition',
                         'character', 'draw', 'drawing', 'illustrated']

        keyword_count = sum(1 for kw in comic_keywords if kw in prompt_lower)

        if keyword_count == 0:
            return False, 0.0

        confidence = min(0.95, 0.35 + (keyword_count * 0.12))
        return True, confidence

    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Extract comic art-specific context."""
        prompt_lower = prompt.lower()

        context = {
            'art_format': None,
            'art_style': None,
            'focus_area': None,
            'experience_level': None,
            'project_type': None
        }

        # Detect art format
        if 'manga' in prompt_lower or 'anime' in prompt_lower:
            context['art_format'] = 'manga'
        elif 'graphic novel' in prompt_lower:
            context['art_format'] = 'graphic_novel'
        elif 'comic strip' in prompt_lower or 'webcomic' in prompt_lower:
            context['art_format'] = 'comic_strip'
        elif 'storyboard' in prompt_lower:
            context['art_format'] = 'storyboard'

        # Detect art style
        if any(kw in prompt_lower for kw in ['realistic', 'realism', 'realistic style']):
            context['art_style'] = 'realistic'
        elif any(kw in prompt_lower for kw in ['cartoon', 'cartoonish', 'simplified']):
            context['art_style'] = 'cartoon'
        elif any(kw in prompt_lower for kw in ['anime', 'manga style']):
            context['art_style'] = 'anime'
        elif any(kw in prompt_lower for kw in ['superhero', 'cape']):
            context['art_style'] = 'superhero'
        elif any(kw in prompt_lower for kw in ['horror', 'dark', 'gothic']):
            context['art_style'] = 'horror'

        # Detect focus area
        if any(kw in prompt_lower for kw in ['character', 'character design', 'figure']):
            context['focus_area'] = 'character'
        elif any(kw in prompt_lower for kw in ['panel', 'layout', 'page', 'composition']):
            context['focus_area'] = 'layout'
        elif any(kw in prompt_lower for kw in ['color', 'coloring', 'color palette']):
            context['focus_area'] = 'coloring'
        elif any(kw in prompt_lower for kw in ['ink', 'inking', 'line work']):
            context['focus_area'] = 'inking'
        elif any(kw in prompt_lower for kw in ['story', 'narrative', 'pacing']):
            context['focus_area'] = 'narrative'

        # Detect experience level
        if any(kw in prompt_lower for kw in ['beginner', 'new', 'learning']):
            context['experience_level'] = 'beginner'
        elif any(kw in prompt_lower for kw in ['intermediate', 'experienced']):
            context['experience_level'] = 'intermediate'
        elif any(kw in prompt_lower for kw in ['professional', 'advanced', 'expert']):
            context['experience_level'] = 'professional'

        # Detect project type
        if any(kw in prompt_lower for kw in ['short story', 'one shot']):
            context['project_type'] = 'short'
        elif any(kw in prompt_lower for kw in ['series', 'ongoing', 'continuing']):
            context['project_type'] = 'series'
        elif any(kw in prompt_lower for kw in ['single', 'standalone', 'story']):
            context['project_type'] = 'single'

        return context

    def generate_enhancement_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate comic art-specific enhancements."""
        enhancements = {}

        # Format-specific guidance
        art_format = context.get('art_format')
        if art_format == 'manga':
            enhancements['format_guidance'] = ('Use right-to-left panel reading. '
                                             'Consider black and white with screentone. '
                                             'Use typical manga visual conventions.')
        elif art_format == 'graphic_novel':
            enhancements['format_guidance'] = ('Plan as collected work, not serialized. '
                                             'Consider color or black/white medium. '
                                             'Focus on narrative cohesion.')
        elif art_format == 'comic_strip':
            enhancements['format_guidance'] = ('Work within strip constraints (3-4 panels). '
                                             'Make punchline clear in final panel. '
                                             'Establish setup quickly.')

        # Style-specific guidance
        style = context.get('art_style')
        if style == 'realistic':
            enhancements['style_guidance'] = ('Accurate proportions essential. '
                                            'Study anatomy and perspective carefully. '
                                            'Value and light are critical.')
        elif style == 'cartoon':
            enhancements['style_guidance'] = ('Exaggeration is core to cartoon style. '
                                            'Simplify shapes for clarity. '
                                            'Expressive distortion tells the story.')
        elif style == 'anime':
            enhancements['style_guidance'] = ('Large expressive eyes are signature feature. '
                                            'Use typical anime visual shorthand. '
                                            'Speed lines and effects enhance action.')
        elif style == 'superhero':
            enhancements['style_guidance'] = ('Exaggerated anatomy shows power. '
                                            'Dynamic posing creates action feel. '
                                            'Bright colors typical for genre.')

        # Focus area guidance
        focus = context.get('focus_area')
        if focus == 'character':
            enhancements['focus_guidance'] = ('Ensure silhouette is distinctive. '
                                            'Design should be instantly recognizable. '
                                            'Costume reflects character personality.')
        elif focus == 'layout':
            enhancements['focus_guidance'] = ('Plan page composition as whole. '
                                            'Vary panel sizes for pacing control. '
                                            'Flow should guide reader naturally.')
        elif focus == 'coloring':
            enhancements['focus_guidance'] = ('Establish limited color palette. '
                                            'Use color to guide attention. '
                                            'Consistency aids character recognition.')
        elif focus == 'inking':
            enhancements['focus_guidance'] = ('Line weight creates emphasis and depth. '
                                            'Hatching adds texture and value. '
                                            'Consistency is professional standard.')
        elif focus == 'narrative':
            enhancements['focus_guidance'] = ('Panel sequence controls pacing. '
                                            'Establish setting before action. '
                                            'Show cause-effect relationships clearly.')

        # Experience level guidance
        exp = context.get('experience_level')
        if exp == 'beginner':
            enhancements['experience_guidance'] = ('Start with simple shapes and basic anatomy. '
                                                 'Study fundamentals before advanced techniques. '
                                                 'Practice simple three-panel stories first.')
        elif exp == 'professional':
            enhancements['experience_guidance'] = ('Polish technical execution. '
                                                 'Push stylistic boundaries intentionally. '
                                                 'Focus on narrative sophistication.')

        return enhancements

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with comic art guidance."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.3:
            return prompt

        context = self.get_discipline_specific_context(prompt)
        enhancements = self.generate_enhancement_context(prompt, context)
        recommendations = self._generate_recommendations(context)

        enhancement = f"""
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 COMIC ART ENHANCEMENT (Confidence: {confidence:.0%})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if enhancements.get('format_guidance'):
            enhancement += f"\n📖 FORMAT ({context.get('art_format', 'general')})\n{enhancements['format_guidance']}\n"

        if enhancements.get('style_guidance'):
            enhancement += f"\n🎭 STYLE ({context.get('art_style', 'general')})\n{enhancements['style_guidance']}\n"

        if enhancements.get('focus_guidance'):
            enhancement += f"\n🎯 FOCUS ({context.get('focus_area', 'general')})\n{enhancements['focus_guidance']}\n"

        if enhancements.get('experience_guidance'):
            enhancement += f"\n📚 LEVEL ({context.get('experience_level', 'intermediate')})\n{enhancements['experience_guidance']}\n"

        if recommendations:
            enhancement += f"\n💡 KEY TECHNIQUES\n{recommendations}\n"

        enhancement += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎨 COMIC ART FUNDAMENTALS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. VISUAL STORYTELLING: Show don't tell - let images carry narrative
2. PANEL LAYOUT: Size and arrangement control pacing and flow
3. COMPOSITION: Balance, focal points guide reader attention
4. CHARACTER DESIGN: Distinctive silhouette aids recognition
5. LINE WORK: Ink quality and line weight convey depth and style
6. COLOR: Palette choice and consistency support storytelling
7. TYPOGRAPHY: Lettering placement and style convey voice
8. SEQUENTIAL LOGIC: Panel order must make cause-effect sense
9. PACING: Large/small panels slow or quicken reader flow
10. DETAIL: Concentrate at focal point, simplify elsewhere

Master these principles to create compelling sequential art.
"""
        return enhancement.strip()

    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate context-specific recommendations."""
        recommendations = []

        focus = context.get('focus_area')
        if focus == 'character':
            recommendations.append('Create distinctive silhouette - recognizable at thumbnail size')
            recommendations.append('Design costume that reflects character personality and role')
            recommendations.append('Develop consistent facial features and body proportions')
        elif focus == 'layout':
            recommendations.append('Vary panel sizes to control reading pace')
            recommendations.append('Ensure logical flow guides reader eyes naturally')
            recommendations.append('Plan full page composition before drawing')
        elif focus == 'coloring':
            recommendations.append('Establish limited color palette before coloring')
            recommendations.append('Use color to separate characters from environment')
            recommendations.append('Apply color theory: warm advances, cool recedes')
        elif focus == 'inking':
            recommendations.append('Use line weight variation to show depth and emphasis')
            recommendations.append('Keep inking consistent throughout comic')
            recommendations.append('Practice hatching for texture and value variation')

        style = context.get('art_style')
        if style == 'realistic':
            recommendations.append('Study anatomy and human proportions intensively')
            recommendations.append('Use reference photos without tracing')
            recommendations.append('Master perspective for environments')
        elif style == 'cartoon':
            recommendations.append('Simplify shapes without losing readability')
            recommendations.append('Use exaggeration for personality and emotion')
            recommendations.append('Keep character design instantly recognizable')

        exp = context.get('experience_level')
        if exp == 'beginner':
            recommendations.append('Start with simple three-panel stories')
            recommendations.append('Use grid layouts until comfortable with composition')
            recommendations.append('Study comics in your target genre carefully')

        return '\n'.join(f'• {rec}' for rec in recommendations) if recommendations else ''

    def _get_enhancement_areas(self) -> List[str]:
        """Get list of enhancement areas."""
        return [
            'Character Design',
            'Panel Layout',
            'Visual Composition',
            'Inking Technique',
            'Coloring Method',
            'Sequential Narrative',
            'Pacing Control',
            'Visual Storytelling',
            'Typography & Lettering',
            'Background Design',
            'Environmental Design',
            'Genre Conventions'
        ]


def get_comic_art_module():
    """Get comic art knowledge module instance."""
    from bob_ai_v8_comic_art import ComicArtKnowledge
    return ComicArtKnowledge()
