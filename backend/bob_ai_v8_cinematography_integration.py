"""
BOB AI v8.0 - Cinematography Integration Module

LLM integration for cinematography knowledge.
Provides discipline-specific context retrieval and enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_cinematography import CinematographyKnowledge
from typing import Dict, Any, Tuple


class CinematographyIntegration(BobAIV8IntegrationBase):
    """
    Integration of cinematography knowledge with LLM enhancement pipeline.
    """
    
    def __init__(self, knowledge: CinematographyKnowledge = None):
        """Initialize cinematography integration.
        
        Args:
            knowledge: CinematographyKnowledge instance (creates new if None)
        """
        if knowledge is None:
            knowledge = CinematographyKnowledge()
        super().__init__(knowledge)
        
        # Cinematography-specific confidence multipliers
        self.confidence_multipliers = {
            'camera': 1.3,
            'lighting': 1.4,
            'color': 1.2,
            'composition': 1.3,
            'film': 1.2,
            'scene': 1.1,
            '3d': 1.1
        }
    
    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if cinematography should enhance prompt.
        
        Args:
            prompt: Input prompt to analyze
            
        Returns:
            Tuple of (should_apply, confidence_score)
        """
        # Base detection using keywords
        should_apply, base_confidence = super().should_apply_to_prompt(prompt)
        
        if not should_apply:
            return False, 0.0
        
        # Enhance confidence for high-value cinematography prompts
        prompt_lower = prompt.lower()
        multiplier = 1.0
        
        for key, mult in self.confidence_multipliers.items():
            if key in prompt_lower:
                multiplier = max(multiplier, mult)
        
        final_confidence = min(1.0, base_confidence * multiplier)
        return True, final_confidence
    
    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Get cinematography-specific context from prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Cinematography context dictionary
        """
        prompt_lower = prompt.lower()
        
        context = {
            'shot_type': None,
            'lighting_style': None,
            'color_approach': None,
            'camera_movement': None,
            'composition_style': None,
            'atmosphere': None
        }
        
        # Detect shot type
        if any(word in prompt_lower for word in ['wide', 'long', 'establish']):
            context['shot_type'] = 'wide_shot'
        elif 'close' in prompt_lower:
            context['shot_type'] = 'close_up'
        elif any(word in prompt_lower for word in ['medium', 'mid']):
            context['shot_type'] = 'medium_shot'
        elif 'two' in prompt_lower and 'shot' in prompt_lower:
            context['shot_type'] = 'two_shot'
        
        # Detect lighting style
        if any(word in prompt_lower for word in ['dark', 'shadow', 'noir', 'moody']):
            context['lighting_style'] = 'low_key'
        elif any(word in prompt_lower for word in ['bright', 'lit', 'cheerful']):
            context['lighting_style'] = 'high_key'
        elif any(word in prompt_lower for word in ['dramatic', 'contrast']):
            context['lighting_style'] = 'chiaroscuro'
        
        # Detect color approach
        if 'saturated' in prompt_lower or 'vibrant' in prompt_lower:
            context['color_approach'] = 'saturated'
        elif 'desaturated' in prompt_lower or 'muted' in prompt_lower:
            context['color_approach'] = 'desaturated'
        elif 'warm' in prompt_lower:
            context['color_approach'] = 'warm_tones'
        elif 'cool' in prompt_lower or 'blue' in prompt_lower:
            context['color_approach'] = 'cool_tones'
        
        # Detect camera movement
        if any(word in prompt_lower for word in ['pan', 'track', 'dolly', 'moving']):
            context['camera_movement'] = 'dynamic'
        elif any(word in prompt_lower for word in ['static', 'still', 'fixed']):
            context['camera_movement'] = 'static'
        elif 'orbit' in prompt_lower:
            context['camera_movement'] = 'orbit'
        
        # Detect composition style
        if 'rule of thirds' in prompt_lower:
            context['composition_style'] = 'rule_of_thirds'
        elif any(word in prompt_lower for word in ['symmetry', 'symmetric']):
            context['composition_style'] = 'symmetric'
        elif any(word in prompt_lower for word in ['depth', 'layered']):
            context['composition_style'] = 'layered_depth'
        
        # Detect atmosphere
        if any(word in prompt_lower for word in ['fog', 'mist', 'haze']):
            context['atmosphere'] = 'misty'
        elif any(word in prompt_lower for word in ['rain', 'storm', 'weather']):
            context['atmosphere'] = 'weather_driven'
        elif 'particles' in prompt_lower or 'dust' in prompt_lower:
            context['atmosphere'] = 'particle_heavy'
        
        return context
    
    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete cinematography enhancement context.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Complete context dictionary with guidance
        """
        base_context = super().generate_enhancement_context(prompt)
        
        # Add cinematography-specific recommendations
        discipline_context = self.get_discipline_specific_context(prompt)
        
        recommendations = self._generate_recommendations(discipline_context, prompt)
        
        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)
        
        return base_context
    
    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate specific cinematography recommendations.
        
        Args:
            context: Cinematography context from analysis
            prompt: Original prompt
            
        Returns:
            Recommendations dictionary
        """
        recommendations = {
            'composition': [],
            'lighting': [],
            'color': [],
            'camera': []
        }
        
        # Composition recommendations
        if context['shot_type']:
            recommendations['composition'].append(
                f"Use {context['shot_type'].replace('_', ' ')} framing"
            )
        if context['composition_style']:
            recommendations['composition'].append(
                f"Apply {context['composition_style'].replace('_', ' ')} principles"
            )
        
        # Lighting recommendations
        if context['lighting_style']:
            recommendations['lighting'].append(
                f"Implement {context['lighting_style'].replace('_', ' ')} lighting setup"
            )
        if 'light' in prompt.lower() or 'shadow' in prompt.lower():
            recommendations['lighting'].append(
                "Use motivated light sources with clear direction"
            )
        
        # Color recommendations
        if context['color_approach']:
            recommendations['color'].append(
                f"Apply {context['color_approach'].replace('_', ' ')} color strategy"
            )
        recommendations['color'].append(
            "Establish cohesive color palette supporting mood"
        )
        
        # Camera recommendations
        if context['camera_movement']:
            recommendations['camera'].append(
                f"Use {context['camera_movement']} camera placement/movement"
            )
        recommendations['camera'].append(
            "Consider character perspective and emotional viewpoint"
        )
        
        return recommendations
    
    def _get_enhancement_areas(self, prompt: str) -> list:
        """Identify areas where cinematography can enhance the prompt.
        
        Args:
            prompt: Input prompt
            
        Returns:
            List of enhancement areas
        """
        enhancement_areas = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['scene', '3d', 'render', 'model']):
            enhancement_areas.append('scene_composition')
        if any(word in prompt_lower for word in ['light', 'shadow', 'illuminate']):
            enhancement_areas.append('lighting_design')
        if any(word in prompt_lower for word in ['color', 'tone', 'mood', 'feel']):
            enhancement_areas.append('color_grading')
        if any(word in prompt_lower for word in ['view', 'angle', 'perspective', 'camera']):
            enhancement_areas.append('camera_perspective')
        if any(word in prompt_lower for word in ['action', 'movement', 'motion', 'dynamic']):
            enhancement_areas.append('motion_dynamics')
        if any(word in prompt_lower for word in ['atmosphere', 'mood', 'emotion']):
            enhancement_areas.append('visual_storytelling')
        
        return enhancement_areas if enhancement_areas else ['general_cinematography']
    
    def enhance(self, prompt: str) -> str:
        """Enhance prompt with cinematography expertise.
        
        Args:
            prompt: Input prompt
            
        Returns:
            Enhanced prompt with cinematography guidance
        """
        should_apply, confidence = self.should_apply_to_prompt(prompt)
        
        if not should_apply or confidence < 0.1:
            return prompt
        
        # Get context and recommendations
        context = self.generate_enhancement_context(prompt)
        
        # Apply cinematography enhancement
        return self.knowledge.enhance_prompt(prompt)


def get_cinematography_module() -> Tuple[CinematographyKnowledge, CinematographyIntegration]:
    """Get instantiated cinematography knowledge and integration modules.
    
    Returns:
        Tuple of (CinematographyKnowledge, CinematographyIntegration)
    """
    knowledge = CinematographyKnowledge()
    integration = CinematographyIntegration(knowledge)
    return knowledge, integration


if __name__ == "__main__":
    # Test integration
    knowledge, integration = get_cinematography_module()
    
    test_prompts = [
        "Create a dramatic 3D scene with cinematic lighting",
        "Design a scene using low-key lighting and shadows",
        "Render an aerial shot with warm color grading",
        "Compose a portrait with rule of thirds framing"
    ]
    
    print("Cinematography Integration Test")
    print("=" * 50)
    
    for prompt in test_prompts:
        should_apply, confidence = integration.should_apply_to_prompt(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Should apply: {should_apply}, Confidence: {confidence:.2f}")
        
        if should_apply:
            enhanced = integration.enhance(prompt)
            print(f"Enhanced:\n{enhanced[:100]}...")
