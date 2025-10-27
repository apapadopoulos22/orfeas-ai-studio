"""
BOB AI v8.0 - Web Development Integration Module

LLM integration for HTML/CSS/JavaScript web development knowledge.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_web_development import WebDevelopmentKnowledge
from typing import Dict, Any, Tuple, Optional, List


class WebDevelopmentIntegration(BobAIV8IntegrationBase):
    """Integration of web development knowledge with LLM enhancement."""

    def __init__(self, knowledge: Optional[WebDevelopmentKnowledge] = None):
        """Initialize web development integration."""
        if knowledge is None:
            knowledge = WebDevelopmentKnowledge()
        super().__init__(knowledge)

        self.confidence_multipliers = {
            'html': 1.4,
            'css': 1.4,
            'javascript': 1.3,
            'web': 1.2,
            'responsive': 1.2,
            'accessibility': 1.3,
            'dom': 1.2,
            'async': 1.2,
            'performance': 1.1,
            'browser': 1.1
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if web development should enhance prompt."""
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
        """Get web development specific context from prompt."""
        prompt_lower = prompt.lower()

        context = {
            'html_focus': None,
            'css_focus': None,
            'js_focus': None,
            'accessibility_required': None,
            'responsive_required': None,
            'performance_critical': None
        }

        # Detect HTML focus
        if any(word in prompt_lower for word in ['semantic', 'markup', 'structure', 'form']):
            context['html_focus'] = 'semantic'

        # Detect CSS focus
        if any(word in prompt_lower for word in ['layout', 'responsive', 'grid', 'flexbox']):
            context['css_focus'] = 'layout'
        elif any(word in prompt_lower for word in ['style', 'theme', 'animation']):
            context['css_focus'] = 'styling'

        # Detect JavaScript focus
        if any(word in prompt_lower for word in ['interaction', 'dom', 'event']):
            context['js_focus'] = 'interaction'
        elif any(word in prompt_lower for word in ['async', 'fetch', 'api']):
            context['js_focus'] = 'async'

        # Detect accessibility requirement
        if any(word in prompt_lower for word in ['accessibility', 'wcag', 'screen reader', 'a11y']):
            context['accessibility_required'] = True

        # Detect responsive requirement
        if any(word in prompt_lower for word in ['responsive', 'mobile', 'device', 'breakpoint']):
            context['responsive_required'] = True

        # Detect performance criticality
        if any(word in prompt_lower for word in ['fast', 'optimize', 'performance', 'speed']):
            context['performance_critical'] = True

        return context

    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete web development enhancement context."""
        base_context = super().generate_enhancement_context(prompt)

        discipline_context = self.get_discipline_specific_context(prompt)
        recommendations = self._generate_recommendations(discipline_context, prompt)

        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)

        return base_context

    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate web development recommendations."""
        recommendations = {
            'html': [],
            'css': [],
            'javascript': [],
            'accessibility': [],
            'performance': []
        }

        # HTML recommendations
        if context['html_focus'] == 'semantic':
            recommendations['html'].extend([
                'Use semantic elements for document structure',
                'Implement proper heading hierarchy',
                'Use labels with form inputs'
            ])

        # CSS recommendations
        if context['css_focus'] == 'layout':
            recommendations['css'].extend([
                'Use flexbox or CSS grid for layouts',
                'Implement mobile-first responsive design'
            ])
        elif context['css_focus'] == 'styling':
            recommendations['css'].append('Use CSS variables for maintainable themes')

        # JavaScript recommendations
        if context['js_focus'] == 'interaction':
            recommendations['javascript'].append('Use event delegation for efficient listeners')
        elif context['js_focus'] == 'async':
            recommendations['javascript'].append('Use async/await for cleaner async code')

        # Accessibility recommendations
        if context['accessibility_required']:
            recommendations['accessibility'].extend([
                'Ensure WCAG contrast ratios',
                'Test keyboard navigation',
                'Provide alternative text for images'
            ])

        # Performance recommendations
        if context['performance_critical']:
            recommendations['performance'].extend([
                'Optimize images and use WebP',
                'Lazy load non-critical content',
                'Minify and compress assets'
            ])

        return recommendations

    def _get_enhancement_areas(self, prompt: str) -> List[str]:
        """Identify web development enhancement areas."""
        enhancement_areas = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['html', 'markup', 'structure']):
            enhancement_areas.append('html_semantics')
        if any(word in prompt_lower for word in ['css', 'style', 'layout', 'responsive']):
            enhancement_areas.append('css_design')
        if any(word in prompt_lower for word in ['javascript', 'interaction', 'dom']):
            enhancement_areas.append('javascript_interaction')
        if any(word in prompt_lower for word in ['accessibility', 'wcag', 'a11y']):
            enhancement_areas.append('accessibility')
        if any(word in prompt_lower for word in ['performance', 'speed', 'optimize']):
            enhancement_areas.append('performance')

        return enhancement_areas if enhancement_areas else ['general_web']

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with web development expertise."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.1:
            return prompt

        return self.knowledge.enhance_prompt(prompt)


def get_web_development_module() -> Tuple[WebDevelopmentKnowledge, WebDevelopmentIntegration]:
    """Get instantiated web development knowledge and integration modules."""
    knowledge = WebDevelopmentKnowledge()
    integration = WebDevelopmentIntegration(knowledge)
    return knowledge, integration
