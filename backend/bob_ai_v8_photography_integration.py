"""
BOB AI v8.0 - Photography Integration Module

LLM integration for photography knowledge.
Provides discipline-specific context retrieval and enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_photography import PhotographyKnowledge
from typing import Dict, Any, Tuple, Optional


class PhotographyIntegration(BobAIV8IntegrationBase):
    """
    Integration of photography knowledge with LLM enhancement pipeline.
    """

    def __init__(self, knowledge: Optional[PhotographyKnowledge] = None):
        """Initialize photography integration.

        Args:
            knowledge: PhotographyKnowledge instance (creates new if None)
        """
        if knowledge is None:
            knowledge = PhotographyKnowledge()
        super().__init__(knowledge)

        # Photography-specific confidence multipliers
        self.confidence_multipliers = {
            'composition': 1.4,
            'exposure': 1.3,
            'aperture': 1.3,
            'shutter': 1.2,
            'iso': 1.2,
            'lighting': 1.4,
            'focus': 1.3,
            'photograph': 1.2,
            'image': 1.1
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if photography should enhance prompt.

        Args:
            prompt: Input prompt to analyze

        Returns:
            Tuple of (should_apply, confidence_score)
        """
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
        """Get photography-specific context from prompt.

        Args:
            prompt: Input prompt

        Returns:
            Photography context dictionary
        """
        prompt_lower = prompt.lower()

        context = {
            'composition_style': None,
            'lighting_style': None,
            'focus_strategy': None,
            'exposure_strategy': None,
            'color_temperature': None,
            'depth_of_field': None
        }

        # Detect composition style
        if any(word in prompt_lower for word in ['rule of thirds', 'thirds']):
            context['composition_style'] = 'rule_of_thirds'
        elif any(word in prompt_lower for word in ['symmetry', 'symmetric']):
            context['composition_style'] = 'symmetric'
        elif any(word in prompt_lower for word in ['leading', 'diagonal']):
            context['composition_style'] = 'leading_lines'
        elif 'negative space' in prompt_lower:
            context['composition_style'] = 'negative_space'

        # Detect lighting style
        if any(word in prompt_lower for word in ['golden hour', 'golden']):
            context['lighting_style'] = 'golden_hour'
        elif 'blue hour' in prompt_lower:
            context['lighting_style'] = 'blue_hour'
        elif any(word in prompt_lower for word in ['backlit', 'backlighting']):
            context['lighting_style'] = 'backlit'
        elif any(word in prompt_lower for word in ['soft', 'diffuse']):
            context['lighting_style'] = 'soft_light'
        elif any(word in prompt_lower for word in ['harsh', 'contrast']):
            context['lighting_style'] = 'harsh_light'

        # Detect focus strategy
        if any(word in prompt_lower for word in ['shallow', 'bokeh', 'blur']):
            context['focus_strategy'] = 'shallow_dof'
        elif any(word in prompt_lower for word in ['deep', 'sharp', 'focus']):
            context['focus_strategy'] = 'deep_dof'
        elif 'macro' in prompt_lower:
            context['focus_strategy'] = 'macro'

        # Detect exposure strategy
        if any(word in prompt_lower for word in ['bright', 'overexpos']):
            context['exposure_strategy'] = 'bright'
        elif any(word in prompt_lower for word in ['dark', 'underexpos', 'low key']):
            context['exposure_strategy'] = 'dark'
        elif 'silhouette' in prompt_lower:
            context['exposure_strategy'] = 'silhouette'

        # Detect color temperature
        if any(word in prompt_lower for word in ['warm', 'golden', 'orange']):
            context['color_temperature'] = 'warm'
        elif any(word in prompt_lower for word in ['cool', 'blue', 'cold']):
            context['color_temperature'] = 'cool'

        # Detect depth of field
        if 'shallow' in prompt_lower or 'bokeh' in prompt_lower:
            context['depth_of_field'] = 'shallow'
        elif 'deep' in prompt_lower or 'sharp' in prompt_lower:
            context['depth_of_field'] = 'deep'

        return context

    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete photography enhancement context.

        Args:
            prompt: Input prompt

        Returns:
            Complete context dictionary with guidance
        """
        base_context = super().generate_enhancement_context(prompt)

        discipline_context = self.get_discipline_specific_context(prompt)
        recommendations = self._generate_recommendations(discipline_context, prompt)

        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)

        return base_context

    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate specific photography recommendations.

        Args:
            context: Photography context from analysis
            prompt: Original prompt

        Returns:
            Recommendations dictionary
        """
        recommendations = {
            'composition': [],
            'lighting': [],
            'exposure': [],
            'focus': []
        }

        # Composition recommendations
        if context['composition_style']:
            recommendations['composition'].append(
                f"Apply {context['composition_style'].replace('_', ' ')} composition"
            )
        recommendations['composition'].append(
            "Ensure balanced frame with strong visual hierarchy"
        )

        # Lighting recommendations
        if context['lighting_style']:
            recommendations['lighting'].append(
                f"Use {context['lighting_style'].replace('_', ' ')} lighting"
            )
        recommendations['lighting'].append(
            "Control highlights and shadows for dimensional form"
        )

        # Exposure recommendations
        if context['exposure_strategy']:
            recommendations['exposure'].append(
                f"Apply {context['exposure_strategy']} exposure strategy"
            )
        recommendations['exposure'].append(
            "Preserve highlight detail and shadow information"
        )

        # Focus recommendations
        if context['focus_strategy']:
            recommendations['focus'].append(
                f"Use {context['focus_strategy'].replace('_', ' ')} focus strategy"
            )
        recommendations['focus'].append(
            "Place focus point on most important element"
        )

        return recommendations

    def _get_enhancement_areas(self, prompt: str) -> list:
        """Identify areas where photography can enhance the prompt.

        Args:
            prompt: Input prompt

        Returns:
            List of enhancement areas
        """
        enhancement_areas = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['compose', 'frame', 'layout']):
            enhancement_areas.append('composition')
        if any(word in prompt_lower for word in ['light', 'shadow', 'illuminate']):
            enhancement_areas.append('lighting')
        if any(word in prompt_lower for word in ['exposur', 'bright', 'dark']):
            enhancement_areas.append('exposure')
        if any(word in prompt_lower for word in ['focus', 'sharp', 'bokeh']):
            enhancement_areas.append('focus')
        if any(word in prompt_lower for word in ['color', 'white balance', 'temperature']):
            enhancement_areas.append('color')
        if any(word in prompt_lower for word in ['image', 'photograph', 'photo']):
            enhancement_areas.append('general_photography')

        return enhancement_areas if enhancement_areas else ['general_photography']

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with photography expertise.

        Args:
            prompt: Input prompt

        Returns:
            Enhanced prompt with photography guidance
        """
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.1:
            return prompt

        return self.knowledge.enhance_prompt(prompt)


def get_photography_module() -> Tuple[PhotographyKnowledge, PhotographyIntegration]:
    """Get instantiated photography knowledge and integration modules.

    Returns:
        Tuple of (PhotographyKnowledge, PhotographyIntegration)
    """
    knowledge = PhotographyKnowledge()
    integration = PhotographyIntegration(knowledge)
    return knowledge, integration


if __name__ == "__main__":
    # Test integration
    knowledge, integration = get_photography_module()

    test_prompts = [
        "Create a portrait with shallow depth of field",
        "Compose a landscape with rule of thirds framing",
        "Capture a scene with golden hour lighting",
        "Generate an image with perfect exposure control"
    ]

    print("Photography Integration Test")
    print("=" * 50)

    for prompt in test_prompts:
        should_apply, confidence = integration.should_apply_to_prompt(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Should apply: {should_apply}, Confidence: {confidence:.2f}")

        if should_apply:
            enhanced = integration.enhance(prompt)
            print(f"Enhanced:\n{enhanced[:100]}...")
