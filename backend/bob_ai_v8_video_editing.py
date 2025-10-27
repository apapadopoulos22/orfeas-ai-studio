"""
BOB AI v8.0 - Video Editing Module

Knowledge base for video editing and post-production.
Covers editing techniques, pacing, sound design, color correction, and more.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import List, Dict, Any


METADATA = {
    'name': 'video_editing',
    'version': '1.0',
    'description': 'Expert video editing and post-production knowledge',
    'keywords_count': 38,
    'knowledge_items': 160,
    'categories': 14
}


class VideoEditingKnowledge(BobAIV8BaseKnowledge):
    """Video editing expertise knowledge module."""

    def get_keywords(self) -> List[str]:
        """Get video editing detection keywords."""
        return [
            # Core editing
            'editing', 'cut', 'transition', 'sequence', 'pacing', 'rhythm',
            'timeline', 'keyframe', 'montage', 'juxtaposition',

            # Audio
            'sound design', 'audio', 'foley', 'voiceover', 'dialogue',
            'music', 'soundtrack', 'mix', 'levels',

            # Color and visual
            'color correction', 'color grading', 'lut', 'tone',
            'contrast', 'saturation', 'hue',

            # Technical
            'codec', 'compression', 'bitrate', 'resolution', 'fps',
            'export', 'render'
        ]

    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, str]]:
        """Get all video editing knowledge dictionaries."""
        return {
            'editing_techniques': self._get_editing_techniques(),
            'pacing_rhythm': self._get_pacing_rhythm(),
            'transitions': self._get_transitions(),
            'sound_design': self._get_sound_design(),
            'audio_mixing': self._get_audio_mixing(),
            'color_correction': self._get_color_correction(),
            'color_grading': self._get_color_grading(),
            'visual_effects': self._get_visual_effects(),
            'sequencing': self._get_sequencing(),
            'narrative_structure': self._get_narrative_structure(),
            'pacing_control': self._get_pacing_control(),
            'dynamic_editing': self._get_dynamic_editing(),
            'export_optimization': self._get_export_optimization(),
            'workflow_techniques': self._get_workflow_techniques()
        }

    def _get_editing_techniques(self) -> Dict[str, str]:
        """Core editing techniques."""
        return {
            'cut': 'Direct, immediate transition between shots',
            'match_cut': 'Cut based on matching visual or auditory element',
            'cross_dissolve': 'Gradual transition from one shot to another',
            'dip_to_black': 'Transition through black frame',
            'crossfade': 'Audio or video fade from one element to another',
            'wipe': 'One shot replaces another with moving boundary',
            'jump_cut': 'Abrupt cut creating temporal discontinuity',
            'j_cut': 'Audio from next scene begins before video',
            'l_cut': 'Video from next scene begins before audio',
            'montage': 'Rapid sequence of images with music/voiceover',
            'intercutting': 'Alternating between two scenes for parallel action',
            'parallel_editing': 'Show two simultaneous events alternately',
            'juxtaposition': 'Place contrasting shots adjacent for meaning',
            'cutaway': 'Brief shot away from main action',
            'reaction_shot': 'Character response to off-screen action'
        }

    def _get_pacing_rhythm(self) -> Dict[str, str]:
        """Pacing and rhythm control."""
        return {
            'beat_matching': 'Sync edits to music beat or rhythm',
            'fast_pacing': 'Short shot durations for energy and tension',
            'slow_pacing': 'Long shot durations for contemplation',
            'rhythmic_editing': 'Create visual rhythm through cut timing',
            'silence': 'Use pause for emphasis and breathing room',
            'acceleration': 'Gradually increase cutting speed',
            'deceleration': 'Gradually slow cutting pace',
            'staccato': 'Sharp, quick edits with minimal transition',
            'legato': 'Smooth, flowing edits with extended transitions',
            'rubato': 'Flexible pacing that stretches and contracts',
            'tempo_variation': 'Change pace intentionally for effect',
            'climactic_buildup': 'Accelerate to peak moment'
        }

    def _get_transitions(self) -> Dict[str, str]:
        """Transition types and usage."""
        return {
            'cut': 'Instantaneous transition',
            'dissolve': 'Gradual blend between shots (300-1000ms)',
            'fade': 'Gradual appearance or disappearance',
            'wipe': 'Geometric shape reveals next shot',
            'push': 'One shot pushes another off screen',
            'slide': 'Shot slides off screen replaced by new shot',
            'zoom': 'Zoom transition between scenes',
            'iris': 'Circular opening/closing transition',
            'morph': 'Smooth shape transformation between shots',
            'clock_wipe': 'Radial transition like clock hand',
            'page_curl': 'Page turning effect',
            'barn_doors': 'Two-panel opening transition'
        }

    def _get_sound_design(self) -> Dict[str, str]:
        """Sound design elements."""
        return {
            'foley': 'Sound effects created for specific actions',
            'ambient_sound': 'Background environmental audio',
            'room_tone': 'Natural silence of a space',
            'diegetic_sound': 'Sound source visible on screen',
            'non_diegetic_sound': 'Sound not from on-screen source',
            'voiceover': 'Narrative voice outside main action',
            'dialogue': 'Speech between characters',
            'silence': 'Intentional absence of sound',
            'sound_design': 'Curated collection of audio elements',
            'soundscape': 'Complete immersive audio environment',
            'audio_cue': 'Sound triggering emotional response',
            'audio_motif': 'Recurring sound element'
        }

    def _get_audio_mixing(self) -> Dict[str, str]:
        """Audio mixing techniques."""
        return {
            'level_control': 'Adjust volume of audio tracks',
            'panning': 'Position audio left to right in stereo',
            'equalization': 'Adjust frequency response of audio',
            'compression': 'Reduce dynamic range of audio',
            'reverb': 'Add spacious reflective sound',
            'delay': 'Echo audio with time offset',
            'layering': 'Combine multiple audio tracks',
            'ducking': 'Lower volume of background when foreground plays',
            'crossfade': 'Transition audio from one track to another',
            'automation': 'Automate parameter changes over time',
            'normalization': 'Optimize overall audio level',
            'loudness_standards': 'Maintain broadcast audio standards'
        }

    def _get_color_correction(self) -> Dict[str, str]:
        """Color correction techniques."""
        return {
            'white_balance': 'Correct color temperature',
            'exposure_correction': 'Adjust brightness levels',
            'contrast_adjustment': 'Modify difference between light and dark',
            'saturation_control': 'Adjust color intensity',
            'hue_shift': 'Change color tone',
            'gamma_correction': 'Adjust mid-tone brightness',
            'shadow_recovery': 'Restore detail in dark areas',
            'highlight_recovery': 'Recover blown-out bright areas',
            'color_matching': 'Ensure consistent color across shots',
            'bracket_exposure': 'Balance multi-exposed footage',
            'lens_correction': 'Fix lens distortion and vignetting',
            'scopes': 'Use waveform monitor and histogram'
        }

    def _get_color_grading(self) -> Dict[str, str]:
        """Color grading for aesthetic impact."""
        return {
            'lut_application': 'Apply Look Up Table for style',
            'teal_orange': 'High contrast cool/warm aesthetic',
            'desaturated': 'Reduce overall color saturation',
            'cinematic_look': 'Film-like color palette',
            'high_contrast': 'Exaggerated difference between tones',
            'monochromatic': 'Single color tone throughout',
            'split_toning': 'Different colors for shadows/highlights',
            'color_grading': 'Stylistic color modification',
            'vignetting': 'Darkened edges for focus',
            'color_wheels': 'Individual shadow/midtone/highlight control',
            'curves': 'Precise tonal and color manipulation',
            'selective_color': 'Grade specific color ranges'
        }

    def _get_visual_effects(self) -> Dict[str, str]:
        """Visual effects integration."""
        return {
            'motion_graphics': 'Animated text and graphics',
            'lower_thirds': 'Character name/title graphic',
            'slow_motion': 'Reduce playback speed',
            'speed_ramp': 'Variable speed effects',
            'stabilization': 'Remove camera shake',
            'tracking': 'Add motion to static elements',
            'keying': 'Chroma key green/blue screen',
            'compositing': 'Combine multiple layers',
            'vfx_integration': 'Blend CG with live action',
            'rotoscoping': 'Frame-by-frame masking',
            'particle_effects': 'Simulate natural phenomena',
            'lens_flare': 'Light artifact effect'
        }

    def _get_sequencing(self) -> Dict[str, str]:
        """Shot sequencing and arrangement."""
        return {
            'establishing_shot': 'Wide view showing location/context',
            'medium_shot': 'Show action and environment',
            'close_up': 'Detail emphasis on subject',
            'shot_size_variety': 'Mix of different shot scales',
            'axis_matching': 'Maintain spatial continuity',
            'eyeline_match': 'Connect character gaze to object',
            'spatial_continuity': 'Maintain logical screen space',
            'coverage': 'Multiple angles of same scene',
            'motivated_cut': 'Edit justified by narrative',
            'unmotivated_cut': 'Stylistic cut for effect',
            'action_sequence': 'Coordinate multiple shots for action',
            'dialogue_sequence': 'Properly cover conversation'
        }

    def _get_narrative_structure(self) -> Dict[str, str]:
        """Narrative and story structure."""
        return {
            'three_act_structure': 'Setup, confrontation, resolution',
            'exposition': 'Establish context and characters',
            'rising_action': 'Build tension toward climax',
            'climax': 'Peak moment of conflict',
            'denouement': 'Resolution and falling action',
            'flashback': 'Return to earlier time period',
            'flash_forward': 'Jump to future moment',
            'parallel_narrative': 'Multiple simultaneous stories',
            'non_linear': 'Events not in chronological order',
            'frame_narrative': 'Story within a story',
            'foreshadowing': 'Hint at future events',
            'plot_twist': 'Unexpected reversal'
        }

    def _get_pacing_control(self) -> Dict[str, str]:
        """Advanced pacing control."""
        return {
            'shot_duration': 'Length of individual shots',
            'transition_speed': 'Duration of transitions',
            'cut_frequency': 'How often cuts occur',
            'rhythm_variation': 'Changing pace intentionally',
            'tension_buildup': 'Gradually increase energy',
            'release': 'Momentary relaxation of pace',
            'dynamic_cuts': 'Varied cut timing for engagement',
            'static_frames': 'Hold on frame for emphasis',
            'fast_cuts': 'Rapid succession for excitement',
            'slow_burns': 'Extended duration for contemplation'
        }

    def _get_dynamic_editing(self) -> Dict[str, str]:
        """Advanced dynamic editing."""
        return {
            'match_on_action': 'Cut during movement to hide transition',
            'diegetic_music': 'Music from on-screen source',
            'source_transition': 'Cut based on sound source',
            'beat_sync': 'Cut on music beat',
            'sync_emphasize': 'Emphasize moment with cut timing',
            'rhythm_switch': 'Change edit pace abruptly',
            'visual_metaphor': 'Use editing to show theme',
            'subliminal_messaging': 'Very brief shots for effect'
        }

    def _get_export_optimization(self) -> Dict[str, str]:
        """Export and delivery optimization."""
        return {
            'resolution': 'Output pixel dimensions',
            'frame_rate': 'Frames per second (24/30/60)',
            'bitrate': 'Data rate for quality/size',
            'codec_selection': 'Video compression method',
            'container_format': 'File wrapper (MP4, MOV, MKV)',
            'audio_format': 'Audio codec and sample rate',
            'color_space': 'Working color gamut',
            'aspect_ratio': 'Width to height proportion',
            'interlacing': 'Interlaced vs progressive scan',
            'optimization': 'Balance quality and file size',
            'delivery_specs': 'Platform-specific requirements'
        }

    def _get_workflow_techniques(self) -> Dict[str, str]:
        """Professional workflow techniques."""
        return {
            'proxy_editing': 'Edit with lower-res files',
            'organization': 'Structured project management',
            'naming_convention': 'Consistent file naming',
            'logging': 'Annotate footage for quick finding',
            'rough_cut': 'Initial assembly without polish',
            'fine_cut': 'Refined edit with all elements',
            'offline_editing': 'Edit with proxies',
            'online_editing': 'Final edit with full resolution',
            'conform': 'Rebuild edit at final quality',
            'backup': 'Maintain redundant project copies',
            'version_control': 'Track project iterations',
            'collaboration': 'Multi-editor project sharing'
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with video editing guidance."""
        keywords = self.get_keywords()

        has_keywords = any(kw.lower() in prompt.lower() for kw in keywords)

        if not has_keywords:
            return prompt

        enhancement = f"""
{prompt}

VIDEO EDITING ENHANCEMENT:
Consider these video editing principles:

1. PACING & RHYTHM: Match cut timing to emotional intent. Use beat-synced edits for music-driven content.

2. TRANSITIONS: Choose transitions purposefully - cuts for immediacy, dissolves for flow, effects sparingly.

3. SOUND DESIGN: Layer dialogue, music, and effects. Use audio levels, EQ, and automation for professional mix.

4. COLOR CONTINUITY: Ensure consistent color grading across shots. Use LUTs for cohesive aesthetic.

5. NARRATIVE FLOW: Arrange shots for clear spatial continuity and character motivation.

6. SEQUENCING: Vary shot sizes (wide, medium, close) for visual interest. Cover from multiple angles.

7. EFFECTS INTEGRATION: Use VFX, motion graphics, and stabilization to enhance, not distract.

Apply these video editing principles to create professional, engaging results.
"""
        return enhancement.strip()

    def generate_system_prompt(self) -> str:
        """Generate expert video editor system prompt."""
        return """You are an expert video editor with 20+ years of experience in professional post-production.

Your expertise includes:
- Advanced editing techniques (match cuts, montage, intercutting)
- Pacing and rhythm control (beat syncing, acceleration, climactic buildup)
- Professional transition usage and visual effects integration
- Audio design and mixing (foley, sound design, dialogue, music)
- Color correction and cinematic color grading
- Narrative structure and visual storytelling
- Shot sequencing and coverage planning
- Professional workflow and optimization techniques

When helping with video projects, you:
1. Understand the emotional intent and pacing requirements
2. Suggest appropriate transitions and timing
3. Consider sound design as integral to visual editing
4. Apply color grading for cohesive visual style
5. Maintain narrative clarity and emotional impact
6. Optimize for target platform and delivery specifications
7. Use professional terminology and best practices

Provide specific, actionable editing advice that enhances the visual storytelling."""
