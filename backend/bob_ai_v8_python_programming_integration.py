"""
BOB AI v8.0 - Python Programming Integration Module

LLM integration for Python programming knowledge.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_python_programming import PythonProgrammingKnowledge
from typing import Dict, Any, Tuple, Optional, List


class PythonProgrammingIntegration(BobAIV8IntegrationBase):
    """Integration of Python programming knowledge with LLM enhancement."""

    def __init__(self, knowledge: Optional[PythonProgrammingKnowledge] = None):
        """Initialize Python programming integration."""
        if knowledge is None:
            knowledge = PythonProgrammingKnowledge()
        super().__init__(knowledge)

        self.confidence_multipliers = {
            'python': 1.4,
            'function': 1.2,
            'class': 1.2,
            'test': 1.2,
            'async': 1.2,
            'decorator': 1.3,
            'exception': 1.2,
            'type': 1.2,
            'pattern': 1.1,
            'performance': 1.1
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if Python programming should enhance prompt."""
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
        """Get Python-specific context from prompt."""
        prompt_lower = prompt.lower()

        context = {
            'code_style': None,
            'testing_approach': None,
            'async_needed': None,
            'error_handling': None,
            'type_hints': None,
            'performance_concern': None
        }

        # Detect code style expectations
        if any(word in prompt_lower for word in ['pep8', 'clean', 'readable', 'pythonic']):
            context['code_style'] = 'pep8_clean'
        elif any(word in prompt_lower for word in ['fast', 'optimized', 'performance']):
            context['code_style'] = 'performance_optimized'

        # Detect testing approach
        if any(word in prompt_lower for word in ['test', 'pytest', 'unittest']):
            context['testing_approach'] = 'test_driven'
        elif any(word in prompt_lower for word in ['coverage', 'mock']):
            context['testing_approach'] = 'coverage_focused'

        # Detect async needs
        if any(word in prompt_lower for word in ['async', 'concurrent', 'parallel', 'io']):
            context['async_needed'] = True

        # Detect error handling emphasis
        if any(word in prompt_lower for word in ['error', 'exception', 'handling', 'robust']):
            context['error_handling'] = 'robust'

        # Detect type hints expectation
        if any(word in prompt_lower for word in ['type', 'annotation', 'mypy', 'typing']):
            context['type_hints'] = 'required'

        # Detect performance concern
        if any(word in prompt_lower for word in ['fast', 'speed', 'optimize', 'profile']):
            context['performance_concern'] = 'important'

        return context

    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete Python enhancement context."""
        base_context = super().generate_enhancement_context(prompt)

        discipline_context = self.get_discipline_specific_context(prompt)
        recommendations = self._generate_recommendations(discipline_context, prompt)

        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)

        return base_context

    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate Python-specific recommendations."""
        recommendations = {
            'style': [],
            'testing': [],
            'typing': [],
            'error_handling': [],
            'performance': []
        }

        # Style recommendations
        if context['code_style'] == 'pep8_clean':
            recommendations['style'].extend([
                'Follow PEP 8 style guidelines',
                'Use black formatter for consistency',
                'Aim for descriptive variable and function names'
            ])
        elif context['code_style'] == 'performance_optimized':
            recommendations['style'].append('Use efficient Python patterns and built-ins')

        # Testing recommendations
        if context['testing_approach'] == 'test_driven':
            recommendations['testing'].extend([
                'Write tests before implementation',
                'Use pytest with fixtures',
                'Aim for 80%+ test coverage'
            ])
        elif context['testing_approach'] == 'coverage_focused':
            recommendations['testing'].append('Use coverage.py to measure test coverage')

        # Type hints recommendations
        if context['type_hints'] == 'required':
            recommendations['typing'].extend([
                'Add comprehensive type hints',
                'Use mypy for static type checking',
                'Document return types and parameter types'
            ])

        # Error handling recommendations
        if context['error_handling'] == 'robust':
            recommendations['error_handling'].extend([
                'Catch specific exceptions, not bare except',
                'Use custom exceptions for clarity',
                'Provide informative error messages'
            ])

        # Performance recommendations
        if context['performance_concern'] == 'important':
            recommendations['performance'].extend([
                'Profile code to identify bottlenecks',
                'Use appropriate algorithms (Big O analysis)',
                'Consider async for I/O-bound operations'
            ])

        return recommendations

    def _get_enhancement_areas(self, prompt: str) -> List[str]:
        """Identify Python enhancement areas."""
        enhancement_areas = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ['style', 'format', 'pep8', 'clean']):
            enhancement_areas.append('code_style')
        if any(word in prompt_lower for word in ['test', 'mock', 'fixture']):
            enhancement_areas.append('testing')
        if any(word in prompt_lower for word in ['type', 'annotation', 'mypy']):
            enhancement_areas.append('type_hints')
        if any(word in prompt_lower for word in ['error', 'exception', 'handling']):
            enhancement_areas.append('error_handling')
        if any(word in prompt_lower for word in ['fast', 'optimize', 'performance', 'profile']):
            enhancement_areas.append('performance')
        if any(word in prompt_lower for word in ['async', 'concurrent', 'await']):
            enhancement_areas.append('concurrency')
        if any(word in prompt_lower for word in ['design', 'pattern', 'architecture']):
            enhancement_areas.append('design_patterns')

        return enhancement_areas if enhancement_areas else ['general_python']

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with Python expertise."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.1:
            return prompt

        return self.knowledge.enhance_prompt(prompt)


def get_python_programming_module() -> Tuple[PythonProgrammingKnowledge, PythonProgrammingIntegration]:
    """Get instantiated Python programming knowledge and integration modules."""
    knowledge = PythonProgrammingKnowledge()
    integration = PythonProgrammingIntegration(knowledge)
    return knowledge, integration


if __name__ == "__main__":
    knowledge, integration = get_python_programming_module()

    test_prompts = [
        "Create a Python function with proper type hints and docstring",
        "Write a test suite for this algorithm",
        "Optimize this loop for performance",
        "Design a Python class following SOLID principles"
    ]

    print("Python Programming Integration Test")
    print("=" * 50)

    for prompt in test_prompts:
        should_apply, confidence = integration.should_apply_to_prompt(prompt)
        print(f"\nPrompt: {prompt}")
        print(f"Should apply: {should_apply}, Confidence: {confidence:.2f}")

        if should_apply:
            enhanced = integration.enhance(prompt)
            print(f"Enhanced:\n{enhanced[:100]}...")
