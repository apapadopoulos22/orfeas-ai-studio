"""
BOB AI v8.0 - Cinematography Knowledge Module

Comprehensive cinematography and film knowledge for 3D scene composition enhancement.
Covers shot types, camera movements, framing, color grading, composition, and lighting.

Total Knowledge Items: 180+
Categories: 15+
Keywords: 45+
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import Dict, List, Any

METADATA = {
    'discipline': 'Cinematography',
    'version': '8.0',
    'status': 'active',
    'knowledge_items': 180,
    'categories': 15,
    'keywords': 45
}


class CinematographyKnowledge(BobAIV8BaseKnowledge):
    """
    Cinematography knowledge module providing expert-level film and visual composition guidance.
    """
    
    def __init__(self):
        super().__init__('Cinematography', '8.0')
        self.keywords = self.get_keywords()
        self.knowledge_items = self.get_knowledge_dictionaries()
        
    def get_keywords(self) -> List[str]:
        """Return cinematography keywords for domain detection."""
        return [
            # Shot types
            'wide shot', 'long shot', 'medium shot', 'close-up', 'extreme close-up',
            'establishing shot', 'over-the-shoulder', 'two-shot', 'master shot',
            
            # Camera movements
            'pan', 'tilt', 'tracking shot', 'dolly', 'crane', 'push-in', 'pull-out',
            'steadicam', 'handheld', 'whip pan', 'orbit',
            
            # Framing and composition
            'rule of thirds', 'leading lines', 'symmetry', 'negative space', 'depth',
            'layering', 'framing within frame', 'aspect ratio', 'composition',
            
            # Lighting
            'three-point lighting', 'key light', 'fill light', 'back light', 'rim light',
            'chiaroscuro', 'low-key', 'high-key', 'color temperature', 'shadows',
            
            # Color and tone
            'color grading', 'color palette', 'saturation', 'contrast', 'color correction',
            'tint', 'grade', 'look-up table', 'LUT', 'cinematic',
            
            # General film terms
            'film', 'video', 'cinematography', '3D', 'scene composition', 'visual storytelling'
        ]
    
    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, Any]]:
        """Return all cinematography knowledge dictionaries."""
        return {
            'shot_types': self._get_shot_types(),
            'camera_movements': self._get_camera_movements(),
            'framing_composition': self._get_framing_composition(),
            'lighting_setup': self._get_lighting_setup(),
            'color_grading': self._get_color_grading(),
            'depth_techniques': self._get_depth_techniques(),
            'visual_storytelling': self._get_visual_storytelling(),
            'camera_lenses': self._get_camera_lenses(),
            'frame_rates': self._get_frame_rates(),
            'aspect_ratios': self._get_aspect_ratios(),
            'cinema_styles': self._get_cinema_styles(),
            'focus_techniques': self._get_focus_techniques(),
            'exposure_control': self._get_exposure_control(),
            'motion_dynamics': self._get_motion_dynamics(),
            'atmospheric_elements': self._get_atmospheric_elements(),
        }
    
    def _get_shot_types(self) -> Dict[str, str]:
        """Shot types and their cinematic purposes."""
        return {
            'wide_shot': 'Establishes location and scale, shows environment context, creates scope',
            'long_shot': 'Full body visibility, shows character in environment, establishes spatial relationships',
            'medium_shot': 'Waist-up framing, standard dialogue shot, allows facial expressions and gestures',
            'close_up': 'Face fills frame, captures emotion and detail, creates intimacy and drama',
            'extreme_close_up': 'Extreme detail, creates intensity, emphasizes small objects or facial features',
            'establishing_shot': 'Opens scene, sets time/place/mood, typically wide shot with environmental context',
            'over_the_shoulder': 'Shows subject from behind another character, creates depth and interaction',
            'two_shot': 'Frames two subjects, shows relationships and interaction between characters',
            'master_shot': 'Wide shot of entire scene, used as reference for continuity',
            'dutch_angle': 'Tilted horizon, creates tension or disorientation, conveys emotional state',
            'point_of_view': 'Camera shows what character sees, creates subjective perspective',
            'reaction_shot': 'Character response to action, shows emotional reaction without dialogue',
            'insert_shot': 'Close detail of object, breaks up main action, draws attention to important element',
            'cutaway_shot': 'Related but separate action, provides context or information',
            'aerial_shot': 'From above, helicopter or drone perspective, establishes scale and geography'
        }
    
    def _get_camera_movements(self) -> Dict[str, str]:
        """Camera movement techniques and their effects."""
        return {
            'pan': 'Horizontal camera rotation, follows action left-to-right, reveals scene horizontally',
            'tilt': 'Vertical camera rotation, reveals height, creates dynamic composition change',
            'tracking_shot': 'Camera moves through space while recording, follows subject, creates immersion',
            'dolly_in': 'Camera moves toward subject, increases intimacy, intensifies focus',
            'dolly_out': 'Camera moves away from subject, reveals scale, creates distance emotionally',
            'crane_shot': 'Vertical movement with height, reveals environment scale, creates dramatic moments',
            'steadicam': 'Smooth, floating movement, fluid and naturalistic, maintains focus while moving',
            'handheld': 'Unstable movement, documentary feel, creates energy and immediacy',
            'orbit_shot': 'Camera moves around subject, reveals 3D form, creates dynamic perspective',
            'whip_pan': 'Fast pan transition, energetic shift between subjects, creates action',
            'push_in': 'Camera moves toward subject, increases engagement, intensifies emotion',
            'pull_out': 'Camera moves backward, reveals context, creates revelation or scale',
            'boom': 'Camera moves on boom arm, combines multiple movements smoothly',
            'parallax': 'Camera moves revealing foreground/background separation, creates depth'
        }
    
    def _get_framing_composition(self) -> Dict[str, str]:
        """Framing and composition techniques."""
        return {
            'rule_of_thirds': 'Divide frame into 9 sections, place subjects on intersection lines, creates balance',
            'leading_lines': 'Use lines (roads, rivers) to guide viewer eye into frame, creates depth',
            'symmetry': 'Mirror composition across center, creates formal, powerful image, emphasizes subject',
            'negative_space': 'Empty space around subject, emphasizes subject through isolation, creates breathing room',
            'depth_layering': 'Foreground, middle-ground, background elements, creates 3D perception in 2D image',
            'framing_within_frame': 'Use doorways/windows to frame subject, creates composition within composition',
            'aspect_ratio_choice': 'Widescreen (cinematic), standard (TV), square (modern), affects viewing experience',
            'headroom': 'Space above head in frame, more headroom = isolation, less = pressure',
            'lead_room': 'Space in direction character looks, shows where character goes mentally',
            'frame_depth': 'Utilize focus to separate subjects from background, creates visual interest',
            'diagonal_composition': 'Subjects on diagonal line, creates dynamic energy and movement',
            'closed_frame': 'Subjects fill frame completely, creates intensity and claustrophobia',
            'open_frame': 'Subjects small in frame, shows vulnerability against environment'
        }
    
    def _get_lighting_setup(self) -> Dict[str, str]:
        """Lighting setups and techniques."""
        return {
            'three_point_lighting': 'Key (main) + Fill (shadow) + Back (separation), standard studio setup, professional control',
            'key_light': 'Main light source on subject, creates primary illumination and shadows',
            'fill_light': 'Reduces shadows from key light, softens contrast, prevents harsh shadows',
            'back_light': 'Behind subject facing camera, creates rim/separation from background',
            'side_light': 'From 90 degrees side, reveals texture and form, creates dramatic shadows',
            'practical_light': 'Light source visible in frame (lamp, fire), adds realism and motivation',
            'high_key_lighting': 'High fill ratio, few shadows, bright cheerful mood, used for comedy',
            'low_key_lighting': 'High contrast, dark shadows, dramatic mood, used for thriller/mystery',
            'chiaroscuro': 'Strong contrast between light and shadow, creates drama and emotion',
            'color_temperature': 'Warm (yellow/red) = cozy/intimate, cool (blue) = cold/lonely/mysterious',
            'motivated_light': 'Light source has story reason (window, streetlight), creates realism',
            'bounce_light': 'Reflect light off surfaces to soften, creates natural-looking fill',
            'gobos': 'Patterns projected by light (window shadows, trees), adds visual texture',
            'rim_light': 'Thin light line separating subject from background, creates separation'
        }
    
    def _get_color_grading(self) -> Dict[str, str]:
        """Color grading and correction techniques."""
        return {
            'color_correction': 'Adjust white balance and color cast, ensures accurate color reproduction',
            'color_grading': 'Artistic color adjustment to establish mood, palette matching across shots',
            'desaturated': 'Reduce color saturation for somber/serious mood, emphasizes emotions',
            'oversaturated': 'Increase color vibrance for energetic/fantastical mood, artificial aesthetics',
            'teal_orange': 'Cool shadows (teal) + warm highlights (orange), popular cinematic look',
            'cyan_magenta': 'Cool/warm color separation, creates modern sci-fi aesthetic',
            'matte_finish': 'Reduce contrast and saturation, creates vintage or artistic look',
            'faded_look': 'Like expired film, romantic or nostalgic feeling',
            'look_up_table': 'LUT file applies predetermined color transform, maintains consistency',
            'color_blocking': 'Use color to separate story elements and emotions, guides viewer attention',
            'monochrome': 'Single color tint, emphasizes mood and story, eliminates color distraction',
            'split_tone': 'Different colors in highlights vs shadows, creates sophisticated look',
            'vibrance': 'Saturation that avoids skin tone distortion, natural-looking color enhancement',
            'contrast_curve': 'S-curve increases contrast, adjusts midtones for specific mood'
        }
    
    def _get_depth_techniques(self) -> Dict[str, str]:
        """Techniques for creating depth perception."""
        return {
            'focus_layering': 'Soft focus foreground/background, sharp subject, creates separation',
            'shallow_depth_of_field': 'Blurry background (bokeh), isolates subject, emphasizes focus',
            'deep_depth_of_field': 'Sharp throughout frame, shows full environment context',
            'focus_pull': 'Shift focus from one object to another, guides viewer attention dynamically',
            'atmospheric_perspective': 'Distant objects bluer/hazier, creates sense of depth',
            'size_perspective': 'Larger objects appear closer, smaller objects appear distant',
            'line_perspective': 'Parallel lines converge at horizon, creates receding depth',
            'color_depth': 'Warm colors advance, cool colors recede, creates spatial separation',
            'overlapping': 'Objects overlap to show depth relationships, clarifies spatial arrangement',
            'shadow_depth': 'Shadows indicate light direction and object position, creates 3D form',
            'focus_stacking': 'Multiple focuses combined in post, sharp throughout extreme depth',
            'miniature_effect': 'Use shallow DOF for toy-like appearance, technical depth manipulation'
        }
    
    def _get_visual_storytelling(self) -> Dict[str, str]:
        """Visual storytelling techniques."""
        return {
            'visual_metaphor': 'Use visual elements to represent ideas (broken mirror = broken life)',
            'color_symbolism': 'Red = danger/passion, blue = calm/sadness, guides emotional response',
            'spatial_dynamics': 'Character position in frame shows power/vulnerability, status',
            'camera_perspective': 'High angle = power over character, low angle = character power',
            'camera_distance': 'Close = intimate/emotional, far = objective/detached',
            'movement_rhythm': 'Slow movement = calm/somber, fast = energy/chaos',
            'focus_attention': 'Where camera focuses guides viewer to important story element',
            'visual_contrast': 'Light vs dark, clean vs cluttered, creates visual interest and meaning',
            'environment_storytelling': 'Background elements tell story (messy = chaos, empty = loneliness)',
            'costume_integration': 'Character colors integrate or contrast with environment',
            'weather_symbolism': 'Rain = sadness, sunny = happiness, storm = conflict',
            'time_of_day': 'Golden hour = romance, blue hour = mystery, noon = harsh reality'
        }
    
    def _get_camera_lenses(self) -> Dict[str, str]:
        """Camera lens types and characteristics."""
        return {
            'wide_angle': '14-35mm, exaggerates depth, expands perspective, creates immersion',
            'standard_lens': '35-50mm, natural human perspective, most neutral appearance',
            'telephoto': '70-200mm+, compresses distance, flattens perspective, intimate feeling',
            'macro_lens': 'Extreme close-up detail, reveals hidden texture, hyper-focus attention',
            'fisheye': 'Ultra-wide with distortion, creative/surreal effect, environmental impact',
            'zoom_lens': 'Variable focal length, flexible framing, convenient production choice',
            'prime_lens': 'Fixed focal length, sharper image, forces deliberate framing',
            'anamorphic_lens': 'Creates characteristic flare and bokeh, cinematic prestige look',
            'soft_focus_lens': 'Built-in diffusion, romantic/dreamlike quality, beauty-focused',
            'tilt_shift': 'Creates miniature effect, technical manipulation of focus plane'
        }
    
    def _get_frame_rates(self) -> Dict[str, str]:
        """Frame rates and temporal dynamics."""
        return {
            '24fps': 'Film standard, cinematic feel, European cinema standard',
            '25fps': 'PAL standard, slight smoothness vs 24fps, some international broadcast',
            '30fps': 'NTSC standard, slightly smoother than film, news/TV standard',
            '48fps': 'Increased smoothness, detail clarity, Hobbit 3D standard, some prefer natural feel',
            '60fps': 'Very smooth, sports/video games feel, high frame rate cinema attempt',
            'slow_motion': 'Higher fps playback at normal speed, stretches time for drama',
            'fast_motion': 'Lower fps playback at normal speed, compresses time for comedy/chaos',
            'variable_frame_rate': 'Changes tempo throughout, dynamic temporal expression'
        }
    
    def _get_aspect_ratios(self) -> Dict[str, str]:
        """Aspect ratio choices and their effects."""
        return {
            '21_9': 'Ultra-widescreen, cinematic epic feel, modern prestige look, modern release format',
            '16_9': 'Modern standard, balanced, used in HD and most contemporary production',
            '4_3': 'Classic television, retro feel, vintage nostalgia, limited by format',
            '1_1': 'Square format, modern social media, artistic/contemporary choice',
            '2_39_1': 'Film projection standard, cinematic prestige, epic scope',
            '1_85_1': 'American theatrical standard, traditional cinema format'
        }
    
    def _get_cinema_styles(self) -> Dict[str, str]:
        """Different cinema visual styles and movements."""
        return {
            'neorealism': 'Natural light, location shooting, documentary feel, social themes',
            'soviet_montage': 'Dynamic cutting, powerful juxtaposition, emotional impact through editing',
            'french_new_wave': 'Jump cuts, handheld camera, experimental narrative, raw authenticity',
            'german_expressionism': 'Extreme angles, dramatic shadows, psychological interior states',
            'noir': 'High contrast black and white, shadows, venetian blinds patterns, moral ambiguity',
            'german_romantic': 'Misty, soft focus, nature emphasis, emotional introspection',
            'slow_cinema': 'Long takes, minimal cutting, patient observation, meditative pacing',
            'music_video': 'Highly stylized, visual effects, rapid cutting, contemporary aesthetics',
            'documentary': 'Observational framing, natural lighting, authentic perspective'
        }
    
    def _get_focus_techniques(self) -> Dict[str, str]:
        """Focus and sharpness techniques."""
        return {
            'rack_focus': 'Shift focus between planes, guides attention, reveals relationship',
            'pull_focus': 'Gradually shift focus, dynamic attention control, professional technique',
            'focus_lock': 'Maintain focus on moving subject, technical precision, object tracking',
            'soft_focus': 'Intentional slight blur, romantic/dreamlike quality, beauty enhancement',
            'selective_focus': 'Sharp subject, blurry background, isolates primary element',
            'deep_focus': 'Sharp throughout frame, Orson Welles technique, complex layered composition'
        }
    
    def _get_exposure_control(self) -> Dict[str, str]:
        """Exposure and brightness techniques."""
        return {
            'overexposed': 'Bright, washed out look, heavenly/dreamlike, blown highlights',
            'underexposed': 'Dark, moody, mysterious, shadow emphasis, visible grain',
            'silhouette': 'Subject completely dark against bright background, creates contrast',
            'backlit': 'Subject between camera and light source, glowing edge effect',
            'bounce_exposure': 'Reflected light softens exposure, natural looking fill, reduced contrast'
        }
    
    def _get_motion_dynamics(self) -> Dict[str, str]:
        """Movement and motion techniques."""
        return {
            'match_on_action': 'Cut while subject moving same direction, maintains continuity',
            'motion_blur': 'Blur from fast movement, creates speed sensation, dynamic energy',
            'freeze_frame': 'Stop action on single frame, emphasis moment, breaks rhythm',
            'slow_reveal': 'Gradually expose information, builds tension and curiosity',
            'action_crossing': 'Subject moves across frame at diagonal, creates dynamic energy',
            'entrance_exit': 'Subject enters/exits frame, controls pacing and attention'
        }
    
    def _get_atmospheric_elements(self) -> Dict[str, str]:
        """Atmospheric and environmental elements."""
        return {
            'fog_mist': 'Reduces visibility, creates mystery and mood, atmospheric depth',
            'lens_flare': 'Light reflection in lens, visual artifacts, adds cinematic flair',
            'particles': 'Dust, rain, snow create texture and depth, adds atmosphere',
            'shadows': 'Shapes cast by light, creates visual interest and mood',
            'reflections': 'Light bounces off surfaces, shows environment and character',
            'weather': 'Rain, snow, wind affects mood and physical reality'
        }
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance a prompt with cinematography expertise."""
        # Extract cinematography keywords that appear in prompt
        prompt_lower = prompt.lower()
        matched_keywords = [kw for kw in self.keywords if kw in prompt_lower]
        
        if not matched_keywords:
            return prompt
        
        # Build enhancement based on detected cinematography elements
        enhancement_parts = [
            prompt,
            "\n\n[Cinematography Enhancement]"
        ]
        
        if any(word in prompt_lower for word in ['scene', '3d', 'model', 'render', 'compose']):
            enhancement_parts.append(
                "Apply cinematic composition principles: Consider rule of thirds placement, "
                "layered depth with foreground/middle-ground/background elements, "
                "and visual balance. Use leading lines and negative space strategically."
            )
        
        if any(word in prompt_lower for word in ['light', 'shadow', 'illuminat']):
            enhancement_parts.append(
                "Optimize lighting strategy: Use three-point lighting principles with "
                "motivated key light, fill light for shadow control, and back light for separation. "
                "Consider color temperature (warm for intimacy, cool for mystery) and "
                "chiaroscuro contrast for dramatic effect."
            )
        
        if any(word in prompt_lower for word in ['color', 'grade', 'palette', 'tone']):
            enhancement_parts.append(
                "Implement color grading strategy: Establish cohesive color palette that "
                "supports the mood. Consider split-toning (warm highlights, cool shadows), "
                "saturation levels for emotional impact, and color symbolism to guide viewer."
            )
        
        if any(word in prompt_lower for word in ['camera', 'perspective', 'view', 'angle']):
            enhancement_parts.append(
                "Enhance camera perspective: Select appropriate shot type and camera angle "
                "that conveys emotional content. Use camera movement strategically to guide "
                "attention and create dynamic visual narrative."
            )
        
        return "\n".join(enhancement_parts)
    
    def generate_system_prompt(self) -> str:
        """Generate cinematography-focused system prompt."""
        return """You are an expert cinematographer and visual storyteller with deep knowledge of:
- Cinematic composition and framing techniques
- Camera movement and shot selection
- Lighting design for mood and drama
- Color grading and visual atmosphere
- Visual storytelling and composition
- Film aesthetics and cinema styles

When enhancing visuals or describing scenes, apply professional cinematography principles:
1. Composition: Use rule of thirds, leading lines, depth layering
2. Lighting: Three-point lighting, motivated sources, color temperature
3. Color: Establish palette, use color symbolism, apply grading strategy
4. Camera: Select appropriate shots and movement to convey emotion
5. Story: Use visual elements to support narrative and emotional goals"""


if __name__ == "__main__":
    # Test module
    cine = CinematographyKnowledge()
    print(f"Cinematography Module Loaded")
    print(f"Keywords: {len(cine.get_keywords())}")
    print(f"Knowledge items: {len(cine.get_knowledge_dictionaries())}")
    print(f"Metadata: {METADATA}")
