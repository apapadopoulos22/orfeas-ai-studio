"""
BOB AI v8.0 - PHP Backend Integration Module

LLM integration for PHP backend knowledge.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from bob_ai_v8_php_backend import PHPBackendKnowledge
from typing import Dict, Any, Tuple, Optional, List


class PHPBackendIntegration(BobAIV8IntegrationBase):
    """Integration of PHP backend knowledge with LLM enhancement."""
    
    def __init__(self, knowledge: Optional[PHPBackendKnowledge] = None):
        """Initialize PHP backend integration."""
        if knowledge is None:
            knowledge = PHPBackendKnowledge()
        super().__init__(knowledge)
        
        self.confidence_multipliers = {
            'php': 1.4,
            'database': 1.3,
            'security': 1.3,
            'function': 1.2,
            'class': 1.2,
            'query': 1.2,
            'session': 1.2,
            'backend': 1.1,
            'optimization': 1.1
        }
    
    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if PHP backend should enhance prompt."""
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
        """Get PHP-specific context from prompt."""
        prompt_lower = prompt.lower()
        
        context = {
            'code_style': None,
            'database_focus': None,
            'security_concern': None,
            'performance_critical': None,
            'testing_needed': None,
            'framework_used': None
        }
        
        # Detect framework usage
        if 'laravel' in prompt_lower:
            context['framework_used'] = 'laravel'
        elif 'symfony' in prompt_lower:
            context['framework_used'] = 'symfony'
        elif 'wordpress' in prompt_lower:
            context['framework_used'] = 'wordpress'
        
        # Detect database focus
        if any(word in prompt_lower for word in ['database', 'query', 'sql', 'mysql']):
            context['database_focus'] = 'database'
        
        # Detect security concern
        if any(word in prompt_lower for word in ['security', 'xss', 'sql injection', 'password']):
            context['security_concern'] = 'important'
        
        # Detect performance criticality
        if any(word in prompt_lower for word in ['fast', 'optimize', 'performance', 'scale']):
            context['performance_critical'] = True
        
        # Detect testing needs
        if any(word in prompt_lower for word in ['test', 'unittest', 'phpunit']):
            context['testing_needed'] = True
        
        # Detect code style expectations
        if any(word in prompt_lower for word in ['clean', 'oop', 'pattern', 'solid']):
            context['code_style'] = 'oop_clean'
        
        return context
    
    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete PHP enhancement context."""
        base_context = super().generate_enhancement_context(prompt)
        
        discipline_context = self.get_discipline_specific_context(prompt)
        recommendations = self._generate_recommendations(discipline_context, prompt)
        
        base_context['discipline_context'] = discipline_context
        base_context['recommendations'] = recommendations
        base_context['enhancement_areas'] = self._get_enhancement_areas(prompt)
        
        return base_context
    
    def _generate_recommendations(self, context: Dict[str, Any], prompt: str) -> Dict[str, Any]:
        """Generate PHP-specific recommendations."""
        recommendations = {
            'security': [],
            'database': [],
            'code_quality': [],
            'performance': [],
            'testing': []
        }
        
        # Security recommendations
        if context['security_concern'] == 'important':
            recommendations['security'].extend([
                'Validate and sanitize all input',
                'Use prepared statements for SQL',
                'Hash passwords with password_hash()',
                'Set secure cookie flags'
            ])
        else:
            recommendations['security'].append('Always prioritize security in PHP')
        
        # Database recommendations
        if context['database_focus'] == 'database':
            recommendations['database'].extend([
                'Use ORM (Eloquent) when possible',
                'Index frequently queried columns',
                'Optimize SQL queries and use LIMIT'
            ])
        
        # Code quality recommendations
        if context['code_style'] == 'oop_clean':
            recommendations['code_quality'].extend([
                'Use type hints and strict types',
                'Follow PSR standards',
                'Use interfaces and traits for abstraction'
            ])
        
        # Performance recommendations
        if context['performance_critical']:
            recommendations['performance'].extend([
                'Enable opcache',
                'Implement caching strategy',
                'Profile with xdebug or Blackfire'
            ])
        
        # Testing recommendations
        if context['testing_needed']:
            recommendations['testing'].extend([
                'Use PHPUnit for unit tests',
                'Mock dependencies',
                'Test for security vulnerabilities'
            ])
        
        return recommendations
    
    def _get_enhancement_areas(self, prompt: str) -> List[str]:
        """Identify PHP enhancement areas."""
        enhancement_areas = []
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ['security', 'password', 'injection']):
            enhancement_areas.append('security')
        if any(word in prompt_lower for word in ['database', 'query', 'sql']):
            enhancement_areas.append('database')
        if any(word in prompt_lower for word in ['class', 'function', 'oop']):
            enhancement_areas.append('code_design')
        if any(word in prompt_lower for word in ['test', 'phpunit', 'mock']):
            enhancement_areas.append('testing')
        if any(word in prompt_lower for word in ['performance', 'optimize', 'cache']):
            enhancement_areas.append('performance')
        if any(word in prompt_lower for word in ['session', 'auth', 'login']):
            enhancement_areas.append('authentication')
        
        return enhancement_areas if enhancement_areas else ['general_php']
    
    def enhance(self, prompt: str) -> str:
        """Enhance prompt with PHP expertise."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)
        
        if not should_apply or confidence < 0.1:
            return prompt
        
        return self.knowledge.enhance_prompt(prompt)


def get_php_backend_module() -> Tuple[PHPBackendKnowledge, PHPBackendIntegration]:
    """Get instantiated PHP backend knowledge and integration modules."""
    knowledge = PHPBackendKnowledge()
    integration = PHPBackendIntegration(knowledge)
    return knowledge, integration
