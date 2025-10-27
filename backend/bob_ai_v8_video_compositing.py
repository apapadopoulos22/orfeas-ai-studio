"""
BOB AI v8.0 - Video Compositing Knowledge Module

Comprehensive knowledge base for VFX and video compositing expertise including keying,
tracking, rotoscoping, color grading, effects, and post-production workflows.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge


class VideoCompositingKnowledge(BobAIV8BaseKnowledge):
    """Video compositing domain knowledge and expertise."""
    
    METADATA = {
        'discipline': 'Video Compositing',
        'version': '1.0',
        'author': 'BOB AI v8.0',
        'category': 'Visual Effects & Post-Production',
        'knowledge_items': 185,
        'keywords_count': 55,
        'expertise_level': 'Professional (8+ years VFX compositing)',
        'primary_use': 'Video compositing, VFX creation, post-production enhancement',
        'secondary_uses': ['motion graphics', 'color grading', 'visual effects', 'rotoscoping', 'tracking'],
        'domain_keywords': ['compositing', 'vfx', 'keying', 'tracking', 'rotoscope']
    }
    
    def get_keywords(self) -> list:
        """Return video compositing domain keywords."""
        return [
            'compositing', 'vfx', 'visual effects', 'keying', 'key',
            'green screen', 'chroma key', 'tracking', 'motion track',
            'rotoscope', 'rotoscoping', 'mask', 'matte', 'mattes',
            'color grading', 'color correction', 'lut', 'curves',
            'effects', 'particle', 'particles', 'blur', 'glow',
            'nuke', 'after effects', 'fusion', 'davinci', 'resolve',
            'post production', 'post-production', 'render', 'rendering',
            'composite', 'layer', 'blending', 'blend mode', 'node',
            'alpha', 'transparency', 'channel', 'expression', 'plugin',
            'animation', 'motion', 'camera tracking', '3d', 'scene'
        ]
    
    def get_knowledge_dictionaries(self) -> dict:
        """Return all video compositing knowledge dictionaries."""
        return {
            'compositing_fundamentals': self._get_compositing_fundamentals(),
            'keying_techniques': self._get_keying_techniques(),
            'rotoscoping': self._get_rotoscoping(),
            'tracking': self._get_tracking(),
            'color_grading': self._get_color_grading(),
            'effects_compositing': self._get_effects_compositing(),
            'audio_mixing': self._get_audio_mixing(),
            'timeline_editing': self._get_timeline_editing(),
            'motion_graphics': self._get_motion_graphics(),
            'vfx_principles': self._get_vfx_principles(),
            'software_mastery': self._get_software_mastery(),
            'optimization': self._get_optimization(),
            'troubleshooting': self._get_troubleshooting(),
            'industry_practices': self._get_industry_practices()
        }
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with video compositing context if applicable."""
        compositing_keywords = self.get_keywords()
        prompt_lower = prompt.lower()
        
        if any(kw in prompt_lower for kw in compositing_keywords):
            knowledge_items = []
            
            if any(kw in prompt_lower for kw in ['key', 'green screen', 'chroma']):
                knowledge_items.extend(list(self._get_keying_techniques().values())[:3])
            
            if any(kw in prompt_lower for kw in ['track', 'motion', 'camera']):
                knowledge_items.extend(list(self._get_tracking().values())[:3])
            
            if any(kw in prompt_lower for kw in ['roto', 'mask', 'matte']):
                knowledge_items.extend(list(self._get_rotoscoping().values())[:3])
            
            if any(kw in prompt_lower for kw in ['color', 'grade', 'lut']):
                knowledge_items.extend(list(self._get_color_grading().values())[:3])
            
            if any(kw in prompt_lower for kw in ['effect', 'particle', 'blur']):
                knowledge_items.extend(list(self._get_effects_compositing().values())[:3])
            
            if knowledge_items:
                context = '\n'.join(f'• {item}' for item in knowledge_items[:6])
                return f"{prompt}\n\n[VIDEO COMPOSITING CONTEXT]\n{context}"
        
        return prompt
    
    def generate_system_prompt(self) -> str:
        """Generate expert video compositor system prompt."""
        return """You are a professional VFX compositor and post-production specialist with 8+ years 
of experience creating stunning visual effects, composites, and finishing for broadcast, film, and digital media.

KEY RESPONSIBILITIES:
1. Guide video compositing from concept through final output
2. Explain keying, tracking, and rotoscoping techniques
3. Provide color grading and color correction expertise
4. Teach effects compositing and particle systems
5. Help with workflow optimization and technical efficiency
6. Address software-specific questions and techniques
7. Share industry best practices and standards
8. Support artists across different compositing applications

EXPERTISE AREAS:
• Keying: Green/blue screen keying, alpha channel management, edge refinement
• Tracking: Motion tracking, camera tracking, 3D tracking for integration
• Rotoscoping: Frame-by-frame masking, clean plate removal, isolation
• Color grading: Color correction, creative color grading, LUTs, curves
• Effects: Particle effects, motion blur, glow, distortion, warping
• Animation: Keyframe animation, expression-based animation, motion graphics
• Audio mixing: Audio level management, mix for broadcast standards
• Software: Nuke, After Effects, Fusion, DaVinci Resolve, professional tools
• 3D integration: Integrating 3D renders with 2D footage
• Optimization: Efficient workflow, render optimization, file management
• Troubleshooting: Common compositing problems and solutions
• Industry standards: Color space, delivery specs, quality standards

TEACHING APPROACH:
• Practical: Include specific techniques and workflows
• Software-agnostic: Principles work across all compositing software
• Step-by-step: Clear progression from fundamentals to advanced
• Problem-focused: Address specific compositing challenges
• Technical: Explain color space, bit depth, compression, and quality
• Creative: Support artistic vision while maintaining technical quality
• Efficient: Optimize workflow and render times

COMMON MISCONCEPTIONS TO ADDRESS:
• Compositing is just "gluing images together" (highly technical craft)
• Higher resolution always means better quality (depends on proper workflow)
• Compositing is automatic (requires expert manual refinement)
• You can fix anything in post (some issues impossible to fix)
• All color grading tools are the same (subtle differences matter)
• Rendering is just a button (requires careful settings and planning)

When helping with video compositing, prioritize clear technical explanation, 
professional workflow practices, and quality-focused problem solving."""
    
    def _get_compositing_fundamentals(self) -> dict:
        """Compositing fundamentals."""
        return {
            'color_space': 'sRGB, rec709, DCI P3 - choose correct space for output',
            'bit_depth': '8-bit (broadcast), 16-bit (intermediate), 32-bit (color grading)',
            'alpha_channel': 'Transparency information separate from RGB data',
            'premultiplied': 'Alpha already factored into color values',
            'straight_alpha': 'RGB and alpha are separate, not multiplied',
            'node_based': 'Network of connected operations - non-destructive workflow',
            'timeline_based': 'Sequential editing on timeline - different workflow model',
            'layer_blending': 'Blend modes control how layers combine',
            'masking': 'Masks isolate effects to specific areas',
            'keyframing': 'Animate parameters over time for dynamic effects',
            'nested_comps': 'Compositions within compositions for organization',
            'expression_scripting': 'Code-based animation and linking',
            'metadata': 'Frame rate, resolution, aspect ratio crucial information',
            'pipeline': 'Organized workflow from source through delivery',
            'version_control': 'Track changes and maintain project history'
        }
    
    def _get_keying_techniques(self) -> dict:
        """Green/blue screen keying techniques."""
        return {
            'green_screen_standard': 'Bright green background for maximum separation',
            'blue_screen_alternative': 'Blue screen for red-dominant subjects',
            'screen_quality': 'Evenly lit, wrinkle-free background essential',
            'keylight_algorithm': 'Industry standard keying algorithm',
            'difference_keying': 'Separates based on color difference from screen',
            'luminance_keying': 'Uses brightness difference - limited use',
            'premult_method': 'Process premult vs straight alpha differently',
            'edge_refinement': 'Refine edges after initial key for clean separation',
            'spill_suppression': 'Remove color fringing from screen reflection',
            'screen_color_selection': 'Choose screen color that contrasts with subject',
            'shadow_area': 'Properly expose shadow areas under subject',
            'light_falloff': 'Ensure even lighting without falloff edges',
            'cleanup_work': 'Manual masking for poorly keyed areas',
            'multi_pass_keying': 'Multiple keys combined for better result',
            'quality_standards': 'Professional keying requires meticulous attention'
        }
    
    def _get_rotoscoping(self) -> dict:
        """Rotoscoping and masking techniques."""
        return {
            'frame_by_frame': 'Creating masks one frame at a time',
            'motion_path': 'Tracking mask movement across frames',
            'bezier_curves': 'Smooth curves for precise mask shapes',
            'control_points': 'Anchor points define mask shape',
            'automation': 'Motion path reduces manual labor',
            'tracking_roto': 'Link roto to tracking data for consistency',
            'overlapping_roto': 'Multiple overlapping masks for complex subjects',
            'feathering': 'Soft edges blend mask smoothly with background',
            'quality_standards': 'Professional roto is extremely tedious',
            'efficiency_techniques': 'Work smarter not harder',
            'clean_plates': 'Creating original reference plates from footage',
            'removal_work': 'Rotoscoping to remove unwanted elements',
            'isolation_technique': 'Roto isolates effects to specific subjects',
            'time_investment': 'Roto is labor-intensive - plan accordingly',
            'geometric_shapes': 'Use simple shapes when possible'
        }
    
    def _get_tracking(self) -> dict:
        """Motion and camera tracking."""
        return {
            '2d_tracking': 'Tracking point movement in 2D space',
            '3d_tracking': 'Solving camera motion in 3D space',
            'feature_tracking': 'Track distinctive features in image',
            'point_selection': 'Choose trackable features with good contrast',
            'tracking_markers': 'Place markers on set for precise tracking',
            'optical_flow': 'Analyze pixel motion across frames',
            'solve_quality': 'Good solve requires good footage and markers',
            'camera_intrinsics': 'Lens distortion parameters affect tracking',
            'lens_distortion': 'Fix barrel/pincushion distortion',
            'match_move': 'Aligning 3D camera to filmed camera motion',
            'stabilization': 'Remove unwanted camera movement',
            'motion_blur_matching': 'Match blur to original footage',
            'steadicam_work': 'Smooth operator movement requires different approach',
            'handheld_footage': 'Erratic motion more challenging to track',
            'tracked_effects': 'Apply effects following tracked motion'
        }
    
    def _get_color_grading(self) -> dict:
        """Color grading and color correction."""
        return {
            'color_correction': 'Fixing white balance and exposure issues',
            'color_grading': 'Creative color work for mood and atmosphere',
            'lut_usage': '3D lookup tables for consistent color transform',
            'curves_tool': 'Powerful tool for precise tone control',
            'wheels_interface': 'Shadows/midtones/highlights control',
            'hue_saturation': 'Adjust specific color ranges',
            'scopes': 'Waveform, vectorscope monitor color objectively',
            'histogram': 'Visualize tonal distribution',
            'legal_levels': 'Video broadcast-safe color range',
            'color_space_conversion': 'Transform between rec709, dci-p3, rec2020',
            'white_balance': 'Correct color temperature cast',
            'skin_tone_correction': 'Maintain natural skin tones',
            'grade_matching': 'Match color across different shots',
            'day_for_night': 'Creative color to simulate night from day footage',
            'reference_monitoring': 'Calibrated display for accurate color'
        }
    
    def _get_effects_compositing(self) -> dict:
        """Effects and motion graphics compositing."""
        return {
            'particle_systems': 'Dust, smoke, fire, magic effects',
            'particle_parameters': 'Life, velocity, scale, rotation control',
            'particle_physics': 'Gravity, wind, collision simulation',
            'blur_effects': 'Motion blur, depth blur, directional blur',
            'glow_bloom': 'Light blooming from bright areas',
            'distortion': 'Wave, ripple, turbulence deformation',
            'lighting': '3D lights in 2D composite space',
            'shadows': 'Drop shadows, realistic light casting',
            'volumetric': 'Light rays, god rays, atmosphere effects',
            'motion_graphics': 'Text animation, shape animation, transitions',
            'audio_sync': 'Animation synchronized to audio beats',
            'transition_effects': 'Dissolves, wipes, morphs between scenes',
            'animated_graphics': 'Titles, lower thirds, overlays',
            'performance': 'Monitor GPU/CPU usage during playback',
            'render_layers': 'Separate render passes for flexibility'
        }
    
    def _get_audio_mixing(self) -> dict:
        """Audio mixing and sound post-production."""
        return {
            'level_control': 'Adjusting volume for consistent levels',
            'loudness_standards': 'LKFS, dBFS standards for broadcast',
            'mixing_interface': 'Fader control and automation',
            'audio_sync': 'Synchronizing audio to video',
            'eq_adjustment': 'Equalization for tonal balance',
            'compression': 'Dynamic range control',
            'reverb': 'Adding space and ambience',
            'delay_effect': 'Echo and timing-based effects',
            'multitrack_mixing': 'Balancing multiple audio sources',
            'ducking': 'Volume automation for speech/music separation',
            'normalization': 'Optimize overall level',
            'headroom': 'Leave space to prevent clipping',
            'monitoring': 'Accurate speaker system for mixing',
            'export_settings': 'Correct format and codec for delivery',
            'surround_sound': '5.1 or 7.1 surround format delivery'
        }
    
    def _get_timeline_editing(self) -> dict:
        """Timeline editing techniques."""
        return {
            'linear_editing': 'Sequential timeline-based editing',
            'non_linear_editing': 'Flexible frame-accurate editing',
            'source_monitoring': 'Preview clips before editing',
            'playback_resolution': 'Adjust quality during playback',
            'proxy_workflow': 'Low-res proxies for performance',
            'multicam_editing': 'Multi-camera sequence editing',
            'audio_sync_detection': 'Automatic syncing of multiple sources',
            'audio_timecode': 'Precise audio sync via timecode',
            'transitions': 'Dissolves, cuts, effects between clips',
            'effects_stack': 'Multiple effects on single clip',
            'keyframing': 'Parameter animation over time',
            'expressions': 'Dynamic keyframe linking',
            'nested_sequences': 'Sequences within sequences',
            'adjustment_layers': 'Apply effects to multiple clips',
            'color_coding': 'Organize clips by type/priority'
        }
    
    def _get_motion_graphics(self) -> dict:
        """Motion graphics and animation."""
        return {
            'text_animation': 'Dynamic title and text effects',
            'character_animation': 'Animating text characters',
            'shape_animation': 'Morphing and shape animation',
            'keyframe_animation': 'Parameter changes over time',
            'bezier_easing': 'Smooth acceleration and deceleration',
            'motion_paths': 'Animating objects along paths',
            'layer_parenting': 'Hierarchy of animated elements',
            'expression_animation': 'Code-driven animation',
            'wiggle_expression': 'Random jitter and motion',
            'time_remapping': 'Variable playback speed',
            'motion_blur': 'Realistic blur matching speed',
            '3d_animation': 'Animating in 3D space',
            'camera_animation': 'Moving virtual camera',
            'light_animation': 'Animating light sources',
            'export_formats': 'ProRes, DNxHD for intermediate formats'
        }
    
    def _get_vfx_principles(self) -> dict:
        """VFX and motion graphics principles."""
        return {
            'compositing_order': 'Element layering affects final result',
            'color_management': 'Consistent color space throughout pipeline',
            'motion_matching': 'Effects must match footage motion',
            'light_matching': 'Lighting integration with original scene',
            'perspective_matching': 'Scale and perspective consistency',
            'depth_perception': 'Elements at correct apparent depth',
            'shadow_casting': 'Realistic shadows from 3D elements',
            'reflection_adding': 'Reflective surfaces show integrated elements',
            'edge_integration': 'Smooth edges blend with surroundings',
            'atmospheric_effects': 'Dust, haze, fog integration',
            'motion_blur_consistency': 'Blur settings match original',
            'chromatic_aberration': 'Match lens aberration if present',
            'grain_matching': 'Match film grain for consistency',
            'quality_focus': 'Details matter - study reference',
            'iteration_refinement': 'Multiple passes improve quality'
        }
    
    def _get_software_mastery(self) -> dict:
        """Software-specific knowledge."""
        return {
            'nuke_nodes': 'Node-based compositing industry standard',
            'nuke_expressions': 'TCL scripting for automation',
            'after_effects_layers': 'Layer-based compositing workflow',
            'ae_expressions': 'JavaScript for dynamic animation',
            'davinci_fusion': 'Node-based color and compositing',
            'davinci_resolve': 'Integrated editing and color grading',
            'resolve_fusion_page': 'Advanced compositing in Resolve',
            'plugin_extensions': 'Third-party plugins expand capabilities',
            'gpu_acceleration': 'CUDA/OpenCL for performance',
            'batch_processing': 'Processing multiple sequences',
            'project_organization': 'File structure and naming conventions',
            'script_automation': 'Python/TCL for workflow automation',
            'custom_tools': 'Creating custom tools and presets',
            'keyboard_shortcuts': 'Speed up workflow significantly',
            'troubleshooting': 'Common software issues and solutions'
        }
    
    def _get_optimization(self) -> dict:
        """Workflow optimization and performance."""
        return {
            'render_time_reduction': 'Optimize for faster renders',
            'cache_management': 'Smart caching strategies',
            'proxy_quality': 'Balance quality and performance',
            'resource_monitoring': 'Track GPU/CPU/RAM usage',
            'disk_space_planning': 'Manage project file sizes',
            'playback_smoothness': 'Achieve real-time playback',
            'batch_rendering': 'Process multiple outputs efficiently',
            'render_farm': 'Distributed rendering for speed',
            'file_organization': 'Quick access to project elements',
            'versioning_system': 'Track changes and iterations',
            'backup_strategy': 'Protect against data loss',
            'archival_planning': 'Long-term project storage',
            'deadline_management': 'Meet delivery schedules',
            'quality_gates': 'Checkpoints prevent rework',
            'documentation': 'Notes for future revisions'
        }
    
    def _get_troubleshooting(self) -> dict:
        """Common issues and solutions."""
        return {
            'color_shift_problem': 'Verify color space settings throughout pipeline',
            'alpha_matte_issues': 'Check premult vs straight alpha settings',
            'tracking_failure': 'Poor track solve from bad markers or footage',
            'keying_artifacts': 'Improve with better screen or technique adjustment',
            'render_slow': 'Disable unused effects, use proxies, upgrade hardware',
            'memory_error': 'Reduce resolution, disable preview, use proxies',
            'frame_drops': 'Insufficient disk speed - upgrade or use proxies',
            'sync_drifting': 'Audio/video desync from playback rate mismatch',
            'corruption_detected': 'Rebuild cache, restart software, restore backup',
            'codec_incompatibility': 'Use industry-standard codecs',
            'color_banding': 'Use higher bit depth processing',
            'quality_degradation': 'Avoid multiple compression steps',
            'file_linking_broken': 'Use relative paths, organize file structure',
            'plugin_crashes': 'Update software and plugins',
            'preview_mismatch': 'Playback quality differs from render'
        }
    
    def _get_industry_practices(self) -> dict:
        """Industry standards and best practices."""
        return {
            'color_space_standard': 'rec709 for broadcast, DCI-P3 for cinema',
            'resolution_standards': '1920x1080 (HD), 4096x2160 (4K cinema)',
            'frame_rate_options': '24p (film), 25p (PAL), 29.97p (NTSC), 60p (high-speed)',
            'delivery_specs': 'Client provides technical specifications',
            'quality_review': 'Multiple rounds of feedback and iteration',
            'version_naming': 'Descriptive names track changes',
            'file_delivery': 'Master files plus multiple delivery formats',
            'archive_retention': 'Keep source files for future changes',
            'documentation_standards': 'Document creative decisions',
            'client_communication': 'Regular updates and feedback loops',
            'deadline_buffers': 'Build in time for revisions',
            'quality_gates': 'Checkpoints prevent rework',
            'legal_compliance': 'Copyright and licensing compliance',
            'industry_trends': 'Stay current with new tools and techniques',
            'professional_community': 'Networking and continuous learning'
        }


def get_video_compositing_knowledge():
    """Factory function to get video compositing knowledge instance."""
    return VideoCompositingKnowledge()
