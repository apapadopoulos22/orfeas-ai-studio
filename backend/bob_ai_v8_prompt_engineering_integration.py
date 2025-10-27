"""
BOB AI v8.0 - Prompt Engineering Integration

Integration layer connecting prompt engineering knowledge with enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from typing import Tuple, Dict, List, Any


class PromptEngineeringIntegration(BobAIV8IntegrationBase):
    """Prompt engineering integration for prompt enhancement."""

    def __init__(self):
        """Initialize with prompt engineering context parameters."""
        super().__init__()
        self.confidence_multipliers = {
            'prompt': 1.4,
            'engineering': 1.4,
            'ai': 1.3,
            'model': 1.2,
            'instruction': 1.3,
            'optimization': 1.2,
            'technique': 1.2,
            'llm': 1.3,
            'chain of thought': 1.3,
            'format': 1.2
        }

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if prompt engineering knowledge should apply."""
        prompt_lower = prompt.lower()

        # Check for prompt engineering keywords
        pe_keywords = ['prompt', 'prompt engineering', 'ai', 'gpt', 'claude', 'chatgpt',
                       'llm', 'language model', 'instruction', 'system prompt', 'few shot',
                       'chain of thought', 'optimize', 'model', 'temperature', 'output format',
                       'constraint', 'instruction tuning', 'reasoning', 'step by step',
                       'role playing', 'context', 'token']

        keyword_count = sum(1 for kw in pe_keywords if kw in prompt_lower)

        if keyword_count == 0:
            return False, 0.0

        confidence = min(0.95, 0.35 + (keyword_count * 0.12))
        return True, confidence

    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Extract prompt engineering-specific context."""
        prompt_lower = prompt.lower()

        context = {
            'task_type': None,
            'model_target': None,
            'optimization_focus': None,
            'complexity_level': None,
            'quality_priority': None
        }

        # Detect task type
        if any(kw in prompt_lower for kw in ['generate', 'write', 'create']):
            context['task_type'] = 'generation'
        elif any(kw in prompt_lower for kw in ['summarize', 'summary']):
            context['task_type'] = 'summarization'
        elif any(kw in prompt_lower for kw in ['classify', 'classification']):
            context['task_type'] = 'classification'
        elif any(kw in prompt_lower for kw in ['extract', 'extraction']):
            context['task_type'] = 'extraction'
        elif any(kw in prompt_lower for kw in ['code', 'programming']):
            context['task_type'] = 'code_generation'
        elif any(kw in prompt_lower for kw in ['question', 'answer', 'qa']):
            context['task_type'] = 'qa'
        elif any(kw in prompt_lower for kw in ['translation', 'translate']):
            context['task_type'] = 'translation'

        # Detect model target
        if 'gpt' in prompt_lower or 'openai' in prompt_lower:
            context['model_target'] = 'gpt'
        elif 'claude' in prompt_lower or 'anthropic' in prompt_lower:
            context['model_target'] = 'claude'
        elif 'cohere' in prompt_lower:
            context['model_target'] = 'cohere'
        elif 'gemini' in prompt_lower or 'google' in prompt_lower:
            context['model_target'] = 'gemini'
        elif 'llama' in prompt_lower or 'meta' in prompt_lower:
            context['model_target'] = 'llama'

        # Detect optimization focus
        if any(kw in prompt_lower for kw in ['fast', 'speed', 'latency', 'quick']):
            context['optimization_focus'] = 'speed'
        elif any(kw in prompt_lower for kw in ['cost', 'token', 'efficient', 'budget']):
            context['optimization_focus'] = 'cost'
        elif any(kw in prompt_lower for kw in ['accuracy', 'quality', 'reliability']):
            context['optimization_focus'] = 'accuracy'
        elif any(kw in prompt_lower for kw in ['creative', 'imagination', 'novel']):
            context['optimization_focus'] = 'creativity'

        # Detect complexity level
        if any(kw in prompt_lower for kw in ['complex', 'complicated', 'difficult']):
            context['complexity_level'] = 'high'
        elif any(kw in prompt_lower for kw in ['simple', 'basic', 'straightforward']):
            context['complexity_level'] = 'low'
        else:
            context['complexity_level'] = 'medium'

        # Detect quality priority
        if any(kw in prompt_lower for kw in ['must', 'critical', 'important', 'production']):
            context['quality_priority'] = 'high'
        elif any(kw in prompt_lower for kw in ['prototype', 'draft', 'experiment']):
            context['quality_priority'] = 'low'

        return context

    def generate_enhancement_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate prompt engineering-specific enhancements."""
        enhancements = {}

        # Task type guidance
        task_type = context.get('task_type')
        if task_type == 'generation':
            enhancements['task_guidance'] = ('Specify exact output format and style. '
                                           'Include examples of desired output. '
                                           'Use role-playing to activate relevant expertise.')
        elif task_type == 'summarization':
            enhancements['task_guidance'] = ('Specify length requirements. '
                                           'Define what key points to include. '
                                           'Specify summary style and tone.')
        elif task_type == 'classification':
            enhancements['task_guidance'] = ('List all possible categories. '
                                           'Provide examples for each category. '
                                           'Specify output format (JSON, list, etc).')
        elif task_type == 'code_generation':
            enhancements['task_guidance'] = ('Specify programming language. '
                                           'Include example code if possible. '
                                           'Define requirements and edge cases.')
        elif task_type == 'qa':
            enhancements['task_guidance'] = ('Provide context for question. '
                                           'Specify confidence level needed. '
                                           'Request step-by-step reasoning.')

        # Model-specific guidance
        model = context.get('model_target')
        if model == 'gpt':
            enhancements['model_guidance'] = ('Use structured format for clarity. '
                                            'Lower temperature (0.3-0.7) for factual tasks. '
                                            'Supports JSON mode for structured output.')
        elif model == 'claude':
            enhancements['model_guidance'] = ('Claude good at reasoning and nuance. '
                                            'Use for complex analysis and writing. '
                                            'Larger context window available.')
        elif model == 'cohere':
            enhancements['model_guidance'] = ('Cohere strong for classification. '
                                            'Good at following detailed instructions. '
                                            'Test examples for your use case.')

        # Optimization guidance
        focus = context.get('optimization_focus')
        if focus == 'speed':
            enhancements['optimization'] = ('Use shorter prompts. '
                                          'Fewer examples reduce tokens. '
                                          'Parallel requests when possible.')
        elif focus == 'cost':
            enhancements['optimization'] = ('Remove unnecessary context. '
                                          'Use fewer examples. '
                                          'Batch requests together.')
        elif focus == 'accuracy':
            enhancements['optimization'] = ('Add more examples. '
                                          'Use chain-of-thought reasoning. '
                                          'Request verification and self-critique.')
        elif focus == 'creativity':
            enhancements['optimization'] = ('Use higher temperature (0.7-1.0). '
                                          'Avoid overly specific constraints. '
                                          'Encourage exploration.')

        # Complexity guidance
        complexity = context.get('complexity_level')
        if complexity == 'high':
            enhancements['complexity_guidance'] = ('Break into smaller steps. '
                                                 'Use decomposition and chain-of-thought. '
                                                 'More examples help.')
        elif complexity == 'low':
            enhancements['complexity_guidance'] = ('Keep prompt simple and concise. '
                                                 'Direct instruction sufficient. '
                                                 'Few examples needed.')

        return enhancements

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with prompt engineering guidance."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply or confidence < 0.3:
            return prompt

        context = self.get_discipline_specific_context(prompt)
        enhancements = self.generate_enhancement_context(prompt, context)
        recommendations = self._generate_recommendations(context)

        enhancement = f"""
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚙️ PROMPT ENGINEERING ENHANCEMENT (Confidence: {confidence:.0%})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

        if enhancements.get('task_guidance'):
            enhancement += f"\n📋 TASK GUIDANCE ({context.get('task_type', 'general')})\n{enhancements['task_guidance']}\n"

        if enhancements.get('model_guidance'):
            enhancement += f"\n🤖 MODEL GUIDANCE ({context.get('model_target', 'general')})\n{enhancements['model_guidance']}\n"

        if enhancements.get('optimization'):
            enhancement += f"\n⚡ OPTIMIZATION ({context.get('optimization_focus', 'general')})\n{enhancements['optimization']}\n"

        if enhancements.get('complexity_guidance'):
            enhancement += f"\n📊 COMPLEXITY ({context.get('complexity_level')})\n{enhancements['complexity_guidance']}\n"

        if recommendations:
            enhancement += f"\n💡 KEY TECHNIQUES\n{recommendations}\n"

        enhancement += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 PROMPT ENGINEERING PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. CLARITY: Specific beats vague. Remove ambiguity.
2. STRUCTURE: Clear structure with sections aids understanding.
3. EXAMPLES: Few-shot examples teach desired patterns.
4. CONSTRAINTS: Explicit boundaries narrow output space.
5. ROLE: Who should model be? Activate relevant expertise.
6. FORMAT: Specify exact output format (JSON, markdown, etc).
7. REASONING: Request step-by-step thinking for complex tasks.
8. TESTING: Test, measure, refine. Iteration improves results.

Apply these principles to create effective AI prompts.
"""
        return enhancement.strip()

    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate context-specific recommendations."""
        recommendations = []

        task_type = context.get('task_type')
        if task_type in ['generation', 'code_generation']:
            recommendations.append('Provide clear examples of desired output format')
            recommendations.append('Specify tone, style, and any constraints upfront')

        if task_type in ['classification', 'qa']:
            recommendations.append('List all possible output categories or answers')
            recommendations.append('Use few-shot examples for each category')

        complexity = context.get('complexity_level')
        if complexity == 'high':
            recommendations.append('Use chain-of-thought: request step-by-step reasoning')
            recommendations.append('Break complex task into smaller subtasks')
            recommendations.append('Request reasoning and verification')

        focus = context.get('optimization_focus')
        if focus == 'accuracy':
            recommendations.append('Add detailed examples for each scenario')
            recommendations.append('Request model to verify and self-critique')
        elif focus == 'cost':
            recommendations.append('Remove unnecessary context and examples')
            recommendations.append('Consolidate related instructions')
        elif focus == 'speed':
            recommendations.append('Minimize token count without losing clarity')
            recommendations.append('Use simpler language and shorter examples')

        priority = context.get('quality_priority')
        if priority == 'high':
            recommendations.append('Test with multiple edge cases before production')
            recommendations.append('Monitor output quality continuously')
            recommendations.append('Implement error detection and fallback logic')

        return '\n'.join(f'• {rec}' for rec in recommendations) if recommendations else ''

    def _get_enhancement_areas(self) -> List[str]:
        """Get list of enhancement areas."""
        return [
            'Prompt Structure',
            'Example Design',
            'Constraint Specification',
            'Role Establishment',
            'Output Format',
            'Task Clarity',
            'Context Management',
            'Reasoning Techniques',
            'Model Parameters',
            'Error Handling',
            'Performance Testing',
            'Cost Optimization'
        ]


def get_prompt_engineering_module():
    """Get prompt engineering knowledge module instance."""
    from bob_ai_v8_prompt_engineering import PromptEngineeringKnowledge
    return PromptEngineeringKnowledge()
