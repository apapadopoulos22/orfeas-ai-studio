"""
BOB AI v8.0 - Video Compositing Integration

Integration layer connecting video compositing knowledge with enhancement.
"""

from bob_ai_v8_base import BobAIV8IntegrationBase
from typing import Tuple, Dict, List, Any


class VideoCompositingIntegration(BobAIV8IntegrationBase):
    """Video compositing integration for post-production enhancement."""
    
    def __init__(self):
        """Initialize with video compositing context parameters."""
        super().__init__()
        self.confidence_multipliers = {
            'compositing': 1.4,
            'vfx': 1.4,
            'video': 1.2,
            'keying': 1.3,
            'tracking': 1.3,
            'color': 1.2,
            'grading': 1.2,
            'effects': 1.2,
            'rendering': 1.2,
            'post-production': 1.3
        }
    
    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if video compositing knowledge should apply."""
        prompt_lower = prompt.lower()
        
        # Check for video compositing keywords
        compositing_keywords = ['compositing', 'vfx', 'visual effects', 'keying', 'key',
                               'green screen', 'chroma key', 'tracking', 'rotoscope',
                               'roto', 'color grading', 'color correction', 'effects',
                               'post production', 'post-production', 'nuke', 'after effects',
                               'davinci', 'resolve', 'fusion', 'composite', 'render',
                               'particle', 'motion track', 'alpha', 'matte']
        
        keyword_count = sum(1 for kw in compositing_keywords if kw in prompt_lower)
        
        if keyword_count == 0:
            return False, 0.0
        
        confidence = min(0.95, 0.35 + (keyword_count * 0.12))
        return True, confidence
    
    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Extract video compositing-specific context."""
        prompt_lower = prompt.lower()
        
        context = {
            'task_type': None,
            'software_tool': None,
            'skill_level': None,
            'project_scale': None,
            'quality_target': None
        }
        
        # Detect task type
        if any(kw in prompt_lower for kw in ['key', 'keying', 'green screen', 'blue screen']):
            context['task_type'] = 'keying'
        elif any(kw in prompt_lower for kw in ['track', 'tracking', 'motion track', 'camera track']):
            context['task_type'] = 'tracking'
        elif any(kw in prompt_lower for kw in ['roto', 'rotoscope', 'mask']):
            context['task_type'] = 'rotoscoping'
        elif any(kw in prompt_lower for kw in ['color grade', 'color correct', 'grading']):
            context['task_type'] = 'color'
        elif any(kw in prompt_lower for kw in ['effect', 'particle', 'blur', 'glow']):
            context['task_type'] = 'effects'
        elif any(kw in prompt_lower for kw in ['render', 'rendering', 'output']):
            context['task_type'] = 'rendering'
        
        # Detect software tool
        if 'nuke' in prompt_lower:
            context['software_tool'] = 'nuke'
        elif 'after effects' in prompt_lower or 'ae' in prompt_lower:
            context['software_tool'] = 'after_effects'
        elif 'davinci' in prompt_lower or 'resolve' in prompt_lower:
            context['software_tool'] = 'davinci_resolve'
        elif 'fusion' in prompt_lower:
            context['software_tool'] = 'fusion'
        elif 'premiere' in prompt_lower:
            context['software_tool'] = 'premiere'
        
        # Detect skill level
        if any(kw in prompt_lower for kw in ['beginner', 'new', 'learning', 'tutorial']):
            context['skill_level'] = 'beginner'
        elif any(kw in prompt_lower for kw in ['intermediate', 'experienced']):
            context['skill_level'] = 'intermediate'
        elif any(kw in prompt_lower for kw in ['professional', 'advanced', 'expert']):
            context['skill_level'] = 'professional'
        
        # Detect project scale
        if any(kw in prompt_lower for kw in ['simple', 'basic', 'single', 'short']):
            context['project_scale'] = 'small'
        elif any(kw in prompt_lower for kw in ['medium', 'moderate']):
            context['project_scale'] = 'medium'
        elif any(kw in prompt_lower for kw in ['complex', 'large', 'feature', '4k']):
            context['project_scale'] = 'large'
        
        # Detect quality target
        if any(kw in prompt_lower for kw in ['broadcast', 'professional', 'cinema']):
            context['quality_target'] = 'professional'
        elif any(kw in prompt_lower for kw in ['web', 'social media', 'youtube']):
            context['quality_target'] = 'web'
        elif any(kw in prompt_lower for kw in ['quick', 'fast', 'draft']):
            context['quality_target'] = 'draft'
        
        return context
    
    def generate_enhancement_context(self, prompt: str, context: Dict[str, Any]) -> Dict[str, str]:
        """Generate video compositing-specific enhancements."""
        enhancements = {}
        
        # Task type guidance
        task_type = context.get('task_type')
        if task_type == 'keying':
            enhancements['task_guidance'] = ('Ensure good screen color separation. '
                                           'Light evenly and avoid shadows on screen. '
                                           'Plan for edge refinement after initial key.')
        elif task_type == 'tracking':
            enhancements['task_guidance'] = ('Use high-contrast tracking markers. '
                                           'Ensure markers visible throughout shot. '
                                           'Verify tracking accuracy before integration.')
        elif task_type == 'rotoscoping':
            enhancements['task_guidance'] = ('Work frame-by-frame carefully. '
                                           'Use bezier curves for smooth masks. '
                                           'Plan for significant time investment.')
        elif task_type == 'color':
            enhancements['task_guidance'] = ('Use scopes for objective measurement. '
                                           'Maintain legal broadcast levels. '
                                           'Reference calibrated display for accuracy.')
        elif task_type == 'effects':
            enhancements['task_guidance'] = ('Ensure effects match footage motion. '
                                           'Integrate lighting realistically. '
                                           'Render in separate passes for flexibility.')
        
        # Software-specific guidance
        software = context.get('software_tool')
        if software == 'nuke':
            enhancements['software_guidance'] = ('Node-based workflow is powerful. '
                                               'Use expressions for efficiency. '
                                               'Plan node tree architecture carefully.')
        elif software == 'after_effects':
            enhancements['software_guidance'] = ('Layer-based workflow is intuitive. '
                                               'Use expressions for dynamic animation. '
                                               'Consider GPU acceleration.')
        elif software == 'davinci_resolve':
            enhancements['software_guidance'] = ('Integrated editing and color grading. '
                                               'Fusion page for advanced compositing. '
                                               'Strong color science for professional work.')
        
        # Skill level guidance
        skill = context.get('skill_level')
        if skill == 'beginner':
            enhancements['skill_guidance'] = ('Start with simple keying examples. '
                                            'Learn fundamentals before advanced techniques. '
                                            'Practice color space concepts thoroughly.')
        elif skill == 'professional':
            enhancements['skill_guidance'] = ('Optimize workflow for efficiency. '
                                            'Focus on quality and problem-solving. '
                                            'Stay current with industry standards.')
        
        # Project scale guidance
        scale = context.get('project_scale')
        if scale == 'large':
            enhancements['scale_guidance'] = ('Plan workflow for efficiency. '
                                            'Use proxies for performance. '
                                            'Organize file structure carefully.')
        elif scale == 'small':
            enhancements['scale_guidance'] = ('Quality first over speed. '
                                            'Perfect technique more important than shortcuts. '
                                            'Build portfolio with strong examples.')
        
        return enhancements
    
    def enhance(self, prompt: str) -> str:
        """Enhance prompt with video compositing guidance."""
        should_apply, confidence = self.should_apply_to_prompt(prompt)
        
        if not should_apply or confidence < 0.3:
            return prompt
        
        context = self.get_discipline_specific_context(prompt)
        enhancements = self.generate_enhancement_context(prompt, context)
        recommendations = self._generate_recommendations(context)
        
        enhancement = f"""
{prompt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 VIDEO COMPOSITING ENHANCEMENT (Confidence: {confidence:.0%})
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""
        
        if enhancements.get('task_guidance'):
            enhancement += f"\n📋 TASK ({context.get('task_type', 'general')})\n{enhancements['task_guidance']}\n"
        
        if enhancements.get('software_guidance'):
            enhancement += f"\n💻 SOFTWARE ({context.get('software_tool', 'general')})\n{enhancements['software_guidance']}\n"
        
        if enhancements.get('skill_guidance'):
            enhancement += f"\n📚 LEVEL ({context.get('skill_level', 'intermediate')})\n{enhancements['skill_guidance']}\n"
        
        if enhancements.get('scale_guidance'):
            enhancement += f"\n📏 PROJECT ({context.get('project_scale', 'medium')})\n{enhancements['scale_guidance']}\n"
        
        if recommendations:
            enhancement += f"\n💡 KEY TECHNIQUES\n{recommendations}\n"
        
        enhancement += """
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎬 VIDEO COMPOSITING PRINCIPLES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. COLOR MANAGEMENT: Consistent color space throughout pipeline
2. QUALITY FIRST: Details matter - seamless integration is key
3. MOTION MATCHING: All effects must align with footage motion
4. LIGHT INTEGRATION: Realistic lighting makes composites believable
5. EDGE REFINEMENT: Smooth integration at element boundaries
6. WORKFLOW EFFICIENCY: Plan for optimization and render time
7. MULTIPLE PASSES: Render in separate passes for flexibility
8. REFERENCE MONITORS: Calibrated display for accurate color work
9. ITERATIVE REFINEMENT: Multiple rounds improve final result
10. INDUSTRY STANDARDS: Follow broadcast/cinema specifications

Master these principles to create professional-quality composites.
"""
        return enhancement.strip()
    
    def _generate_recommendations(self, context: Dict[str, Any]) -> str:
        """Generate context-specific recommendations."""
        recommendations = []
        
        task_type = context.get('task_type')
        if task_type == 'keying':
            recommendations.append('Position talent clearly away from screen background')
            recommendations.append('Use high-quality lighting for even screen exposure')
            recommendations.append('Plan for spill suppression and edge refinement')
        elif task_type == 'tracking':
            recommendations.append('Place high-contrast markers visible throughout shot')
            recommendations.append('Test tracking on sample frames before full solve')
            recommendations.append('Verify accuracy before integrating 3D elements')
        elif task_type == 'rotoscoping':
            recommendations.append('Use automated tools first to reduce manual work')
            recommendations.append('Work frame-by-frame carefully for precision')
            recommendations.append('Feather edges for smooth integration')
        elif task_type == 'color':
            recommendations.append('Use waveform and vectorscope for objective measurement')
            recommendations.append('Keep broadcast levels legal to specification')
            recommendations.append('Match color across different shot types')
        
        software = context.get('software_tool')
        if software == 'nuke':
            recommendations.append('Plan node tree architecture before building')
            recommendations.append('Use expressions for automation and efficiency')
            recommendations.append('Create reusable node groups for common tasks')
        elif software == 'after_effects':
            recommendations.append('Organize layers logically with naming conventions')
            recommendations.append('Use adjustment layers for global effects')
            recommendations.append('Plan precomposition strategy carefully')
        
        quality = context.get('quality_target')
        if quality == 'professional':
            recommendations.append('Follow strict color space and resolution standards')
            recommendations.append('Deliver multiple formats per specifications')
            recommendations.append('Document creative decisions for future reference')
        
        return '\n'.join(f'• {rec}' for rec in recommendations) if recommendations else ''
    
    def _get_enhancement_areas(self) -> List[str]:
        """Get list of enhancement areas."""
        return [
            'Keying Technique',
            'Motion Tracking',
            'Rotoscoping',
            'Color Grading',
            'Effects Compositing',
            'Integration',
            'Quality Control',
            'Workflow Optimization',
            'Technical Specifications',
            'Software Mastery',
            'Problem Solving',
            'Project Management'
        ]


def get_video_compositing_module():
    """Get video compositing knowledge module instance."""
    from bob_ai_v8_video_compositing import VideoCompositingKnowledge
    return VideoCompositingKnowledge()
