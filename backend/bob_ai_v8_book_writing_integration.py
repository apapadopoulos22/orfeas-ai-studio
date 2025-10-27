"""
BOB AI v8.0 - Book Writing Integration

Integration layer connecting book writing knowledge with prompt enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from typing import Tuple, Dict, List, Any


class BookWritingIntegration(BobAIV8IntegrationBase):
    """Book writing integration for prompt enhancement."""

    def __init__(self):
        """Initialize with book writing context parameters."""
        super().__init__()
        self.confidence_multipliers = {
            'writing': 1.4,
            'story': 1.4,
            'book': 1.4,
            'character': 1.3,
            'plot': 1.3,
            'dialogue': 1.2,
            'novel': 1.3,
            'fiction': 1.3,
            'narrative': 1.2,
            'publish': 1.2
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if book writing knowledge should apply and confidence level."""
        prompt_lower = prompt.lower()

        # Check for writing keywords
        writing_keywords = ['write', 'writing', 'story', 'book', 'novel', 'character', 'plot',
                           'dialogue', 'narrative', 'fiction', 'chapter', 'scene', 'protagonist',
                           'antagonist', 'publish', 'manuscript', 'memoir', 'essay', 'author',
                           'protagonist', 'climax', 'pacing', 'tension', 'world building']

        keyword_count = sum(1 for kw in writing_keywords if kw in prompt_lower)

        if keyword_count == 0:
            return False, 0.0

        confidence = min(0.95, 0.35 + (keyword_count * 0.12))
        return True, confidence

    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Extract book writing-specific context from prompt."""
        prompt_lower = prompt.lower()

        context = {
            'project_type': None,
            'genre': None,
            'stage': None,
            'challenge': None,
            'target_audience': None
        }

        # Detect project type
        if any(kw in prompt_lower for kw in ['novel', 'book', 'manuscript', 'story']):
            context['project_type'] = 'novel'
        elif any(kw in prompt_lower for kw in ['memoir', 'autobiography']):
            context['project_type'] = 'memoir'
        elif any(kw in prompt_lower for kw in ['essay', 'article', 'piece']):
            context['project_type'] = 'essay'
        elif any(kw in prompt_lower for kw in ['short story', 'flash fiction']):
            context['project_type'] = 'short_story'

        # Detect genre
        genres = ['fantasy', 'science fiction', 'mystery', 'thriller', 'romance', 'horror',
                 'literary', 'young adult', 'middle grade', 'historical', 'contemporary',
                 'paranormal', 'magical realism', 'dystopian']
        for genre in genres:
            if genre in prompt_lower:
                context['genre'] = genre
                break

        # Detect writing stage
        if any(kw in prompt_lower for kw in ['outline', 'planning', 'plot', 'structure']):
            context['stage'] = 'planning'
        elif any(kw in prompt_lower for kw in ['draft', 'first draft', 'writing', 'write']):
            context['stage'] = 'drafting'
        elif any(kw in prompt_lower for kw in ['revise', 'edit', 'revision', 'rewrite']):
            context['stage'] = 'revision'
        elif any(kw in prompt_lower for kw in ['polish', 'proofread', 'final']):
            context['stage'] = 'polishing'
        elif any(kw in prompt_lower for kw in ['publish', 'query', 'agent', 'submission']):
            context['stage'] = 'publishing'

        # Detect main challenge
        if any(kw in prompt_lower for kw in ['character', 'protagonist', 'development']):
            context['challenge'] = 'character'
        elif any(kw in prompt_lower for kw in ['plot', 'story', 'structure', 'pacing']):
            context['challenge'] = 'plot'
        elif any(kw in prompt_lower for kw in ['dialogue', 'conversation']):
            context['challenge'] = 'dialogue'
        elif any(kw in prompt_lower for kw in ['ending', 'climax', 'resolution']):
            context['challenge'] = 'ending'
        elif any(kw in prompt_lower for kw in ['world', 'setting', 'build']):
            context['challenge'] = 'world'

        # Detect audience
        if any(kw in prompt_lower for kw in ['young adult', 'teen', 'ya', 'young']):
            context['target_audience'] = 'young_adult'
        elif any(kw in prompt_lower for kw in ['middle grade', 'children', 'kids']):
            context['target_audience'] = 'middle_grade'
        elif any(kw in prompt_lower for kw in ['adult']):
            context['target_audience'] = 'adult'

        return context

    def generate_enhancement_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate book writing-specific enhancement context."""
        enhancements = {}

        # Stage-specific guidance
        stage = context.get('stage')
        if stage == 'planning':
            enhancements['stage_guidance'] = ('Focus on character motivation first. What does protagonist want and why? '
                                            'Build plot around character choices, not external events.')
        elif stage == 'drafting':
            enhancements['stage_guidance'] = ('Write freely. Ignore perfectionism. Forward momentum matters. '
                                             'You can edit later. Permission to have a bad first draft.')
        elif stage == 'revision':
            enhancements['stage_guidance'] = ('Big picture first: does plot work? Then character arcs. Then pacing. '
                                             'Finally prose quality. Multiple passes. Take distance between revisions.')
        elif stage == 'polishing':
            enhancements['stage_guidance'] = ('Read aloud. Cut unnecessary scenes. Tighten prose. Replace weak verbs. '
                                             'Every word must earn its place. Get beta readers. Professional edit if possible.')
        elif stage == 'publishing':
            enhancements['stage_guidance'] = ('Query letter must hook immediately. Research agents carefully. '
                                             'Multiple rejections normal. Consider self-publishing option. Build author platform.')

        # Genre-specific guidance
        genre = context.get('genre')
        if genre == 'fantasy':
            enhancements['genre_guidance'] = ('World-building crucial. Establish magic rules and limitations clearly. '
                                             'Epic scope but intimate character arcs. Readers want escapism with emotional truth.')
        elif genre == 'mystery':
            enhancements['genre_guidance'] = ('Plant clues fairly. Fair play with reader. Don\'t withhold information unfairly. '
                                             'Puzzle first, characters second. Twist must be surprising but inevitable.')
        elif genre == 'romance':
            enhancements['genre_guidance'] = ('Chemistry between characters essential. Obstacles to relationship drive plot. '
                                             'Emotionally satisfying HEA (Happy Ever After) required. Sensual but not gratuitous.')
        elif genre == 'young adult':
            enhancements['genre_guidance'] = ('Teen protagonist must have agency. Emotional journey primary. Not just romance. '
                                             'Authentic teen voice. Address real issues. Give teens power in story.')
        elif genre == 'literary':
            enhancements['genre_guidance'] = ('Character psychology primary. Literary merit over plot. Ambiguous endings acceptable. '
                                             'Precise prose. Themes explored deeply. Experimental structure allowed.')

        # Challenge-specific guidance
        challenge = context.get('challenge')
        if challenge == 'character':
            enhancements['challenge_guidance'] = ('Give protagonist clear want and need. Contradiction creates tension. '
                                                 'Flaws make relatable. Arc: flawed → learns lesson → changed. Backstory informs choices.')
        elif challenge == 'plot':
            enhancements['challenge_guidance'] = ('Inciting incident forces protagonist to act ~15% in. Escalate stakes. '
                                                 'Climax highest stakes. Resolution shows changed character. Three-act structure foundational.')
        elif challenge == 'dialogue':
            enhancements['challenge_guidance'] = ('Each character unique voice. Subtext between words. Show conflict through dialogue. '
                                                 'Avoid info-dumping. Use action beats. Read aloud to hear rhythm.')
        elif challenge == 'ending':
            enhancements['challenge_guidance'] = ('Must be earned. Character changed. Answers main question. Satisfying but not neat. '
                                                 'Emotional truth. Not too long. Final image lingers.')
        elif challenge == 'world':
            enhancements['challenge_guidance'] = ('Weave details in gradually. Don\'t info-dump. Show culture through character choices. '
                                                 'Consistent rules. World feels lived-in. Details serve story, not showcase.')

        # Audience-specific guidance
        audience = context.get('target_audience')
        if audience == 'young_adult':
            enhancements['audience_guidance'] = ('Teen voice authentic. Issues real (identity, belonging, power). Agency for teens. '
                                                'Not preachy. Fast pacing. Emotional stakes high.')
        elif audience == 'middle_grade':
            enhancements['audience_guidance'] = ('Ages 8-12. Adventure and humor. Clear conflicts. Wonder and discovery. '
                                                'Shorter chapters. Positive messages. Characters face challenges, overcome them.')
        elif audience == 'adult':
            enhancements['audience_guidance'] = ('Complex themes. Sophisticated prose. Assume reader intelligence. '
                                                'Can explore mature content thoughtfully. Literary merit expected.')

        return enhancements

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with book writing guidance."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.3:
            return prompt

        context = self.get_discipline_specific_context(prompt)
        enhancements = self.generate_enhancement_context(prompt, context)
        recommendations = self._generate_recommendations(context)

        enhancement = f"""
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📖 BOOK WRITING ENHANCEMENT (Confidence: {confidence:.0%})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if enhancements.get('stage_guidance'):
            enhancement += f"\n📝 STAGE GUIDANCE ({context.get('stage', 'unknown')})\n{enhancements['stage_guidance']}\n"

        if enhancements.get('genre_guidance'):
            enhancement += f"\n🎭 GENRE GUIDANCE ({context.get('genre', 'general')})\n{enhancements['genre_guidance']}\n"

        if enhancements.get('challenge_guidance'):
            enhancement += f"\n⚠️ CHALLENGE GUIDANCE ({context.get('challenge', 'general')})\n{enhancements['challenge_guidance']}\n"

        if enhancements.get('audience_guidance'):
            enhancement += f"\n👥 AUDIENCE GUIDANCE ({context.get('target_audience', 'general')})\n{enhancements['audience_guidance']}\n"

        if recommendations:
            enhancement += f"\n💡 KEY RECOMMENDATIONS\n{recommendations}\n"

        enhancement += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✨ CORE WRITING PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. STORY IS CHARACTER: Compelling characters drive compelling stories.
2. SHOW, DON'T TELL: Demonstrate through action, dialogue, scene.
3. CONFLICT CREATES TENSION: Without it, no engagement. Essential.
4. PACING MATTERS: Vary to match intensity. Control reader experience.
5. SPECIFICITY SELLS: Concrete details over abstract generalizations.
6. AUTHENTIC VOICE: Unique perspective and language. Original.
7. REVISION ESSENTIAL: First draft rough. Editing is where real writing happens.
8. READ ALOUD: Your ear catches what your eyes miss.

Apply these principles to create compelling, publishable writing.
"""
        return enhancement.strip()

    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate context-specific recommendations."""
        recommendations = []

        # Stage recommendations
        stage = context.get('stage')
        if stage == 'planning':
            recommendations.append('Create detailed character profiles: wants, needs, fears, motivations')
            recommendations.append('Outline key plot points: inciting incident, midpoint, climax')
        elif stage == 'drafting':
            recommendations.append('Write daily. Keep momentum. Word count targets help.')
            recommendations.append('Don\'t edit while drafting. Momentum more important than perfection.')
        elif stage == 'revision':
            recommendations.append('Take distance between revisions (weeks or months)')
            recommendations.append('Multiple passes: big picture, then characters, then pacing, then prose')
        elif stage == 'polishing':
            recommendations.append('Get beta readers for feedback')
            recommendations.append('Professional edit recommended (developmental or line edit)')
        elif stage == 'publishing':
            recommendations.append('Research agents before querying')
            recommendations.append('Consider self-publishing as valid option')

        # Challenge recommendations
        challenge = context.get('challenge')
        if challenge == 'character':
            recommendations.append('Character contradictions create depth: want vs. need creates arc')
            recommendations.append('Flaws make characters relatable and interesting')
        elif challenge == 'plot':
            recommendations.append('Inciting incident ~15% in: event forces protagonist to act')
            recommendations.append('Escalate stakes incrementally throughout')
        elif challenge == 'dialogue':
            recommendations.append('Each character has distinct voice: vocabulary, speech patterns, concerns')
            recommendations.append('Subtext: what\'s unsaid creates tension')
        elif challenge == 'ending':
            recommendations.append('Ending must be earned through character arc')
            recommendations.append('Final image should linger: emotionally resonant')
        elif challenge == 'world':
            recommendations.append('Weave world details gradually into action')
            recommendations.append('Establish clear rules for magic/technology/society')

        # Project type recommendations
        project_type = context.get('project_type')
        if project_type == 'novel':
            recommendations.append('Target word count varies by genre: fantasy 90-120K, mystery 70-90K')
        elif project_type == 'memoir':
            recommendations.append('Emotional truth more important than fact accuracy')
            recommendations.append('Selective memory is fine; frame is personal perspective')

        return '\n'.join(f'• {rec}' for rec in recommendations) if recommendations else ''

    def _get_enhancement_areas(self) -> List[str]:
        """Get list of enhancement areas."""
        return [
            'Character Development',
            'Plot Structure',
            'Pacing & Tension',
            'Dialogue Quality',
            'World Building',
            'Point of View',
            'Writing Craft',
            'Show vs Tell',
            'Sensory Details',
            'Conflict & Stakes',
            'Editing Strategy',
            'Publishing Options'
        ]


def get_book_writing_module():
    """Get book writing knowledge module instance."""
    from bob_ai_v8_book_writing import BookWritingKnowledge
    return BookWritingKnowledge()
