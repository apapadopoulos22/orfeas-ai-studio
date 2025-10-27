"""
BOB AI v8.0 - Video Editing Integration Module

LLM integration for video editing knowledge.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_video_editing import VideoEditingKnowledge
from typing import Dict, Any, Tuple, Optional, List


class VideoEditingIntegration(BobAIV8IntegrationBase):
    """Integration of video editing knowledge with LLM enhancement."""

    def __init__(self, knowledge: Optional[VideoEditingKnowledge] = None):
        """Initialize video editing integration."""
        if knowledge is None:
            knowledge = VideoEditingKnowledge()
        super().__init__(knowledge)

        self.confidence_multipliers = {
            'editing': 1.4,
            'transition': 1.3,
            'pacing': 1.3,
            'cut': 1.2,
            'sound': 1.2,
            'color': 1.2,
            'grade': 1.2,
            'video': 1.1,
            'export': 1.1
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if video editing should enhance prompt."""
        should_apply, base_confidence = super().should_apply_to_prompt(prompt)

        if not should_apply:
            return False, 0.0

        prompt_lower = prompt.lower()
        multiplier = 1.0

        for key, mult in self.confidence_multipliers.items():
            if key in prompt_lower:
                multiplier = max(multiplier, mult)

        final_confidence = min(1.0, base_confidence * multiplier)
        return True, final_confidence

    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Get video editing specific context from prompt."""
        prompt_lower = prompt.lower()

        context = {
            'pace_style': None,
            'transition_preference': None,
            'tone_approach': None,
            'audio_emphasis': None,
            'color_style': None,
            'narrative_structure': None
        }

        # Detect pace style
        if any(word in prompt_lower for word in ['fast', 'quick', 'energy', 'dynamic']):
            context['pace_style'] = 'fast'
        elif any(word in prompt_lower for word in ['slow', 'contemplat', 'deliberate']):
            context['pace_style'] = 'slow'
        elif any(word in prompt_lower for word in ['varied', 'rhythm', 'accelerate']):
            context['pace_style'] = 'varied'

        # Detect transition preference
        if any(word in prompt_lower for word in ['seamless', 'smooth', 'flow']):
            context['transition_preference'] = 'dissolve'
        elif any(word in prompt_lower for word in ['sharp', 'cut', 'abrupt']):
            context['transition_preference'] = 'cut'
        elif any(word in prompt_lower for word in ['wipe', 'effect', 'transition']):
            context['transition_preference'] = 'effects'

        # Detect tone approach
        if any(word in prompt_lower for word in ['professional', 'corporate', 'formal']):
            context['tone_approach'] = 'professional'
        elif any(word in prompt_lower for word in ['creative', 'artistic', 'experimental']):
            context['tone_approach'] = 'creative'
        elif any(word in prompt_lower for word in ['music', 'beat', 'rhythm']):
            context['tone_approach'] = 'music_driven'

        # Detect audio emphasis
        if any(word in prompt_lower for word in ['dialogue', 'speech', 'voiceover']):
            context['audio_emphasis'] = 'dialogue'
        elif any(word in prompt_lower for word in ['music', 'soundtrack', 'score']):
            context['audio_emphasis'] = 'music'
        elif any(word in prompt_lower for word in ['sound', 'foley', 'effects']):
            context['audio_emphasis'] = 'effects'

        # Detect color style
        if any(word in prompt_lower for word in ['cinematic', 'color grade', 'lut']):
            context['color_style'] = 'cinematic'
        elif any(word in prompt_lower for word in ['desaturated', 'bw', 'monochrome']):
            context['color_style'] = 'desaturated'
        elif any(word in prompt_lower for word in ['vibrant', 'saturated', 'colorful']):
            context['color_style'] = 'vibrant'

        # Detect narrative structure
        if any(word in prompt_lower for word in ['montage', 'sequence', 'series']):
            context['narrative_structure'] = 'montage'
        elif any(word in prompt_lower for word in ['parallel', 'intercutting', 'simultaneous']):
            context['narrative_structure'] = 'parallel'
        elif any(word in prompt_lower for word in ['linear', 'chronological', 'sequence']):
            context['narrative_structure'] = 'linear'

        return context

    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete video editing enhancement context."""
        base_context = super().generate_enhancement_context(prompt)

        discipline_context = self.get_discipline_specific_context(prompt)
        recommendations = self._generate_recommendations(discipline_context, prompt)

        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)

        return base_context

    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate video editing recommendations."""
        recommendations = {
            'pacing': [],
            'transitions': [],
            'audio': [],
            'color': [],
            'narrative': []
        }

        # Pacing recommendations
        if context['pace_style'] == 'fast':
            recommendations['pacing'].extend([
                'Use rapid cuts for energy',
                'Match edits to beat for synchronization',
                'Keep shot durations short (2-4 seconds)'
            ])
        elif context['pace_style'] == 'slow':
            recommendations['pacing'].extend([
                'Use longer shot durations (5-8 seconds)',
                'Employ subtle transitions (dissolves)',
                'Allow space for contemplation'
            ])
        elif context['pace_style'] == 'varied':
            recommendations['pacing'].append('Vary cutting pace intentionally')

        # Transition recommendations
        if context['transition_preference'] == 'cut':
            recommendations['transitions'].append('Use clean cuts for immediacy and energy')
        elif context['transition_preference'] == 'dissolve':
            recommendations['transitions'].append('Use dissolves for smooth, flowing transitions')
        elif context['transition_preference'] == 'effects':
            recommendations['transitions'].append('Use stylistic transitions sparingly, only for emphasis')

        # Audio recommendations
        if context['audio_emphasis']:
            recommendations['audio'].append(
                f"Prioritize {context['audio_emphasis']} in audio mix"
            )
        recommendations['audio'].append('Layer sound elements for depth')

        # Color recommendations
        if context['color_style']:
            recommendations['color'].append(
                f"Apply {context['color_style']} color grading aesthetic"
            )
        recommendations['color'].append('Ensure consistent color across shots')

        # Narrative recommendations
        if context['narrative_structure']:
            recommendations['narrative'].append(
                f"Use {context['narrative_structure']} narrative structure"
            )
        recommendations['narrative'].append('Maintain spatial and temporal continuity')

        return recommendations

    def _get_enhancement_areas(self, prompt: str) -> List[str]:
        """Identify video editing enhancement areas."""
        enhancement_areas = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['pace', 'timing', 'cut']):
            enhancement_areas.append('pacing')
        if any(word in prompt_lower for word in ['transition', 'wipe', 'dissolve']):
            enhancement_areas.append('transitions')
        if any(word in prompt_lower for word in ['sound', 'audio', 'music', 'dialogue']):
            enhancement_areas.append('audio')
        if any(word in prompt_lower for word in ['color', 'grade', 'tone']):
            enhancement_areas.append('color')
        if any(word in prompt_lower for word in ['sequence', 'montage', 'narrative', 'story']):
            enhancement_areas.append('narrative')
        if any(word in prompt_lower for word in ['effect', 'vfx', 'motion']):
            enhancement_areas.append('effects')
        if any(word in prompt_lower for word in ['export', 'delivery', 'format']):
            enhancement_areas.append('export')

        return enhancement_areas if enhancement_areas else ['general_editing']

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with video editing expertise."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.1:
            return prompt

        return self.knowledge.enhance_prompt(prompt)


def get_video_editing_module() -> Tuple[VideoEditingKnowledge, VideoEditingIntegration]:
    """Get instantiated video editing knowledge and integration modules."""
    knowledge = VideoEditingKnowledge()
    integration = VideoEditingIntegration(knowledge)
    return knowledge, integration


if __name__ == "__main__":
    knowledge, integration = get_video_editing_module()

    test_prompts = [
        "Create a fast-paced music video with beat-synced cuts",
        "Edit a documentary with contemplative pacing",
        "Assemble a montage sequence with varied transitions",
        "Produce a corporate video with professional color grading"
    ]

    print("Video Editing Integration Test")
    print("=" * 50)

    for prompt in test_prompts:
        should_apply, confidence = integration.should_apply_to_prompt(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Should apply: {should_apply}, Confidence: {confidence:.2f}")

        if should_apply:
            enhanced = integration.enhance(prompt)
            print(f"Enhanced:\n{enhanced[:100]}...")
