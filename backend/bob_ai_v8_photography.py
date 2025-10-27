"""
BOB AI v8.0 - Photography Knowledge Module

Comprehensive photography knowledge for image composition and visual quality enhancement.
Covers composition, exposure, aperture, shutter speed, ISO, and lighting.

Total Knowledge Items: 170+
Categories: 14+
Keywords: 42+
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge
from typing import Dict, List, Any

METADATA = {
    'discipline': 'Photography',
    'version': '8.0',
    'status': 'active',
    'knowledge_items': 170,
    'categories': 14,
    'keywords': 42
}


class PhotographyKnowledge(BobAIV8BaseKnowledge):
    """
    Photography knowledge module providing expert-level image composition and technical guidance.
    """
    
    def __init__(self):
        super().__init__('Photography', '8.0')
        self.keywords = self.get_keywords()
        self.knowledge_items = self.get_knowledge_dictionaries()
    
    def get_keywords(self) -> List[str]:
        """Return photography keywords for domain detection."""
        return [
            # Composition
            'composition', 'framing', 'rule of thirds', 'leading lines', 'depth', 'perspective',
            'symmetry', 'negative space', 'golden ratio', 'rule of odds',
            
            # Exposure
            'exposure', 'overexposed', 'underexposed', 'metering', 'histogram', 'dynamic range',
            'blown highlights', 'crushed blacks', 'exposure compensation',
            
            # Aperture and depth
            'aperture', 'f-stop', 'depth of field', 'bokeh', 'shallow focus', 'deep focus',
            'focus stacking', 'macro', 'wide angle',
            
            # Shutter speed
            'shutter speed', 'motion blur', 'freeze', 'long exposure', 'fast shutter', 'slow shutter',
            'panning', 'action photography',
            
            # ISO
            'iso', 'noise', 'grain', 'sensitivity', 'low iso', 'high iso',
            
            # Lighting
            'lighting', 'natural light', 'golden hour', 'blue hour', 'backlit', 'sidelighting',
            'fill light', 'reflector', 'diffuser', 'harsh light', 'soft light',
            
            # Focus techniques
            'focus', 'autofocus', 'manual focus', 'focus point', 'focus lock', 'af-on',
            
            # Color
            'white balance', 'color temperature', 'color cast', 'saturation', 'vibrance',
            'color grading', 'color correction',
            
            # Photography styles
            'portrait', 'landscape', 'macro', 'street', 'wildlife', 'product', 'sports',
            'photography', 'photo', 'image', 'picture'
        ]
    
    def get_knowledge_dictionaries(self) -> Dict[str, Dict[str, Any]]:
        """Return all photography knowledge dictionaries."""
        return {
            'composition_principles': self._get_composition_principles(),
            'exposure_control': self._get_exposure_control(),
            'aperture_depth': self._get_aperture_depth(),
            'shutter_speed': self._get_shutter_speed(),
            'iso_sensitivity': self._get_iso_sensitivity(),
            'lighting_techniques': self._get_lighting_techniques(),
            'focus_techniques': self._get_focus_techniques(),
            'color_temperature': self._get_color_temperature(),
            'photography_styles': self._get_photography_styles(),
            'camera_settings': self._get_camera_settings(),
            'post_processing': self._get_post_processing(),
            'lenses': self._get_lenses(),
            'light_modifiers': self._get_light_modifiers(),
            'perspective_techniques': self._get_perspective_techniques(),
        }
    
    def _get_composition_principles(self) -> Dict[str, str]:
        """Composition principles for compelling images."""
        return {
            'rule_of_thirds': 'Divide frame into 9 sections, place subjects on lines/intersections',
            'leading_lines': 'Use lines (roads, rivers, fences) to guide viewer eye into image',
            'golden_ratio': 'Mathematical proportion (1.618:1) found in nature, more organic than thirds',
            'framing_within_frame': 'Use foreground elements to frame main subject',
            'negative_space': 'Empty space around subject emphasizes subject through isolation',
            'symmetry': 'Mirror composition across vertical/horizontal axis, creates formal balance',
            'asymmetry': 'Unbalanced composition creates tension and visual interest',
            'rule_of_odds': 'Odd number of subjects more visually interesting than even',
            'depth_layering': 'Foreground, middle-ground, background create sense of dimension',
            'perspective': 'Position relative to subject changes perceived relationships',
            'diagonal_lines': 'Diagonal composition creates dynamic energy and movement',
            'patterns_repetition': 'Repeated elements create visual rhythm and interest',
            'center_composition': 'Subject centered creates formal, direct statement',
            'color_contrast': 'Complementary colors create visual pop and attraction',
            'foreground_interest': 'Include foreground element for depth and visual entry point'
        }
    
    def _get_exposure_control(self) -> Dict[str, str]:
        """Exposure control and metering techniques."""
        return {
            'metering_evaluative': 'Averages exposure across entire frame, good general-purpose',
            'metering_center_weighted': 'Emphasizes center of frame, useful for portraits',
            'metering_spot': 'Meters only small spot, allows precise exposure control',
            'metering_partial': 'Similar to spot but larger area, balanced approach',
            'exposure_compensation': 'Override metering by adding/subtracting exposure',
            'exposure_bracketing': 'Take multiple exposures to choose best in post-production',
            'histogram_reading': 'Graph shows tonal distribution, prevents blown highlights/blacks',
            'dynamic_range': 'Range between brightest and darkest tones, extended range preserves detail',
            'blown_highlights': 'Overexposed white areas with no detail, use exposure comp to prevent',
            'crushed_blacks': 'Underexposed black areas with no detail, watch shadows in histogram',
            'exposure_latitude': 'Amount of over/underexposure before loss of quality',
            'wet_exposure': 'Slightly overexposing RAW file to maximize shadow detail',
            'metering_lock': 'Lock exposure while recomposing frame, allows creative positioning'
        }
    
    def _get_aperture_depth(self) -> Dict[str, str]:
        """Aperture and depth of field techniques."""
        return {
            'aperture_f_stop': 'Measures lens opening size, lower number = larger opening',
            'wide_aperture': 'f/1.4 to f/2.8, shallow depth of field, collects more light',
            'standard_aperture': 'f/4 to f/5.6, balanced depth of field, most natural looking',
            'narrow_aperture': 'f/8 to f/16, deep depth of field, everything in focus',
            'shallow_depth_of_field': 'Blurry background (bokeh), isolates sharp subject',
            'deep_depth_of_field': 'Sharp throughout frame, shows full environment context',
            'bokeh_quality': 'Character of out-of-focus areas, affects aesthetic appeal',
            'bokeh_shape': 'Lens blades determine shape of bokeh (circular, hexagonal)',
            'coma_aberration': 'Bokeh distortion toward edges, more apparent in wide apertures',
            'focus_plane': 'Plane where camera focuses, adjustable in manual focus',
            'hyperfocal_distance': 'Specific focus distance maximizes depth of field for given aperture',
            'macro_photography': 'Extreme close-up with shallow depth of field requiring precision',
            'focus_stacking': 'Multiple images with different focus points combined for complete sharpness'
        }
    
    def _get_shutter_speed(self) -> Dict[str, str]:
        """Shutter speed and motion techniques."""
        return {
            'fast_shutter': '1/1000 or faster, freezes motion, requires light or high ISO',
            'standard_shutter': '1/125 to 1/500, balances motion and handheld stability',
            'slow_shutter': '1/15 to 1 second, captures motion blur, requires tripod',
            'long_exposure': '1-30 seconds or bulb mode, extreme motion blur, light trails, smooth water',
            'motion_blur': 'Intentional blur of moving subjects creates sense of speed',
            'panning': 'Follow moving subject keeping focus, blurs background while subject sharp',
            'handheld_limit': 'Slowest practical shutter without blur is roughly 1/(focal length)',
            'sync_speed': 'Maximum shutter speed where flash can expose entire frame',
            'image_stabilization': 'Lens or camera technology compensates for shake, allows slower shutter',
            'bulb_mode': 'Shutter stays open as long as button pressed, for very long exposures',
            'action_freezing': 'Fast shutter stops motion, critical for sports and wildlife',
            'star_trails': 'Long exposure captures star movement across sky over time'
        }
    
    def _get_iso_sensitivity(self) -> Dict[str, str]:
        """ISO and sensor sensitivity."""
        return {
            'low_iso': 'ISO 50-400, best quality, minimal noise, requires good light',
            'standard_iso': 'ISO 400-1600, general purpose, acceptable noise for most uses',
            'high_iso': 'ISO 1600-3200, necessary in low light, visible noise acceptable',
            'extreme_iso': 'ISO 3200+, extreme low light only, significant noise',
            'iso_noise': 'Random grain pattern visible at high ISO, reduces fine detail',
            'noise_patterns': 'Different sensor types produce different noise signatures',
            'noise_reduction': 'In-camera or post-processing smoothing reduces detail with noise',
            'base_iso': 'Native ISO where sensor performs best, typically 100 or 400',
            'iso_push': 'Overexposing in-camera then underexposing in post, preserves shadows',
            'iso_expanded': 'Extending beyond native ISO range sacrifices quality for convenience',
            'high_iso_performance': 'Modern sensors handle high ISO better than older models',
            'iso_reciprocity': 'Raising ISO one stop requires 1 stop faster shutter or smaller aperture'
        }
    
    def _get_lighting_techniques(self) -> Dict[str, str]:
        """Lighting techniques and control."""
        return {
            'natural_light': 'Sunlight, available light, free and abundant but uncontrollable',
            'golden_hour': 'Hour after sunrise or before sunset, warm and directional light',
            'blue_hour': 'Twilight time just before sunrise/after sunset, cool blue tones',
            'harsh_light': 'Midday sun creates harsh shadows and high contrast',
            'soft_light': 'Diffused light from clouds or diffusers, flatters subjects',
            'backlit': 'Light behind subject creates rim light and separation from background',
            'sidelighting': 'Light from side reveals texture and dimensionality',
            'front_lighting': 'Light from front flattens subject, reduces dimension',
            'three_point_lighting': 'Key + fill + back light, professional portrait setup',
            'key_light': 'Primary light source, defines shadows and form',
            'fill_light': 'Secondary light fills shadows, reduces contrast',
            'back_light': 'Separates subject from background, creates depth',
            'practical_light': 'Light source within frame (window, lamp, fire)',
            'window_light': 'Directional soft light from window, popular for portraits',
            'reflectors': 'Bounce light onto shadow areas, inexpensive fill solution',
            'diffusers': 'Soften light by scattering rays, reduce contrast',
            'light_modifiers': 'Umbrellas, softboxes, beauty dishes shape light quality',
            'reciprocity': 'Lower fill light ratio creates more drama, higher ratio flattens'
        }
    
    def _get_focus_techniques(self) -> Dict[str, str]:
        """Focus methods and techniques."""
        return {
            'autofocus': 'Camera autofocus system chooses focus point, fast and convenient',
            'manual_focus': 'Photographer manually focuses, precision control, slower',
            'single_af': 'Focus locks when shutter pressed, good for stationary subjects',
            'continuous_af': 'Focus tracks moving subject, good for action photography',
            'af_on_button': 'Separate button for focus, allows recomposing without refocus',
            'back_button_focus': 'Focus/metering on back button, separates focus from shutter',
            'focus_lock': 'Lock focus then recompose, allows subject not in center',
            'focus_point': 'Select specific focus point from several available',
            'eye_af': 'Modern systems detect and focus on eyes, excellent for portraits',
            'focus_assist': 'Illuminators or magnified view help achieve focus',
            'focus_peaking': 'Highlights in-focus areas in real-time, manual focus aid',
            'depth_of_field_preview': 'Shows actual depth of field at shooting aperture',
            'focus_breathing': 'Lens focal length changes slightly when focusing, affects framing'
        }
    
    def _get_color_temperature(self) -> Dict[str, str]:
        """Color temperature and white balance."""
        return {
            'white_balance': 'Adjusts colors to match light source, prevents color cast',
            'daylight': 'Around 5500K, neutral white balance for sunny conditions',
            'cloudy': 'Around 6500K, slightly warmer than direct sunlight',
            'shade': 'Around 7500K, blue tone from sky light, warm white balance needed',
            'tungsten': 'Around 3200K, warm incandescent bulbs, cool white balance needed',
            'fluorescent': 'Around 4200K, green cast from fluorescent lights',
            'color_temperature': 'Measured in Kelvin, higher = warmer, lower = cooler',
            'auto_white_balance': 'Camera attempts to neutralize color cast, sometimes inaccurate',
            'preset_white_balance': 'Select specific light source (daylight, shade, tungsten)',
            'custom_white_balance': 'Photographer creates custom balance from reference',
            'white_balance_shift': 'Fine-tune white balance after capturing reference card',
            'mixed_lighting': 'Multiple light sources with different temperatures create color complexity',
            'white_balance_bracket': 'Capture multiple exposures with different white balance',
            'color_cast': 'Unwanted color tint from improper white balance',
            'warm_color_temperature': 'Orange/red tones, intimate and cozy feeling',
            'cool_color_temperature': 'Blue tones, calming and mysterious feeling'
        }
    
    def _get_photography_styles(self) -> Dict[str, str]:
        """Different photography styles and approaches."""
        return {
            'portrait': 'Focus on people, emphasizes facial features and expressions',
            'landscape': 'Wide vistas, emphasizes environment and composition',
            'macro': 'Extreme close-ups, reveals hidden details and texture',
            'street': 'Candid moments in public spaces, captures authentic moments',
            'wildlife': 'Animals in natural habitat, requires patience and fast autofocus',
            'product': 'Commercial photography, emphasizes details and appeal',
            'sports': 'Action photography, requires fast shutter and continuous autofocus',
            'architecture': 'Buildings and structures, often uses wide angles and straight lines',
            'documentary': 'Tells story through images, emphasizes authentic moments',
            'fashion': 'Clothing and accessories, emphasizes styling and aesthetics',
            'food': 'Culinary photography, emphasizes texture and appetizing presentation',
            'travel': 'Captures places and moments, combines landscape and portrait elements',
            'fine_art': 'Artistic expression, follows personal vision rather than commercial needs',
            'abstract': 'Non-representational imagery, emphasizes form and color'
        }
    
    def _get_camera_settings(self) -> Dict[str, str]:
        """Camera settings and modes."""
        return {
            'aperture_priority': 'Photographer sets aperture, camera chooses shutter speed',
            'shutter_priority': 'Photographer sets shutter speed, camera chooses aperture',
            'manual_mode': 'Photographer controls both aperture and shutter speed',
            'program_mode': 'Camera selects both settings, limited photographer control',
            'metering_mode': 'How camera meters light (evaluative, spot, center-weighted)',
            'focus_mode': 'How camera focuses (single, continuous, manual)',
            'drive_mode': 'Single shot, continuous burst, or self-timer',
            'raw_format': 'Unprocessed sensor data, maximum post-processing flexibility',
            'jpeg_format': 'Compressed processed data, smaller file size, less editing latitude',
            'raw_jpeg': 'Capture both simultaneously for convenience and flexibility',
            'image_stabilization': 'Compensates for camera shake, allows slower shutter',
            'custom_white_balance': 'Create personalized white balance profile'
        }
    
    def _get_post_processing(self) -> Dict[str, str]:
        """Post-processing and editing techniques."""
        return {
            'exposure_adjustment': 'Brighten or darken image overall or selectively',
            'contrast': 'Increase or decrease difference between light and dark',
            'highlights_shadows': 'Recover detail in overexposed or underexposed areas',
            'clarity': 'Increase local contrast, enhances texture and detail',
            'saturation': 'Increase or decrease color intensity',
            'vibrance': 'Saturation without affecting skin tones as much',
            'color_grading': 'Artistic color adjustments to establish mood',
            'sharpening': 'Enhance edge detail, critical for image perceived quality',
            'noise_reduction': 'Remove grain and noise, balance with detail preservation',
            'cropping': 'Improve composition after the fact',
            'straightening': 'Correct horizon tilt in landscape photos',
            'lens_correction': 'Fix distortion, vignette, and chromatic aberration',
            'cloning_healing': 'Remove unwanted elements or imperfections',
            'selective_editing': 'Edit specific parts of image differently'
        }
    
    def _get_lenses(self) -> Dict[str, str]:
        """Lens types and characteristics."""
        return {
            'prime_lens': 'Fixed focal length, sharper than zoom, smaller and lighter',
            'zoom_lens': 'Variable focal length, flexible framing, heavier and larger',
            'wide_angle': '14-35mm, exaggerates depth, emphasizes environment',
            'standard_lens': '35-70mm, natural human perspective',
            'telephoto': '70-200mm+, compresses distance, isolates subject',
            'macro_lens': 'Extreme close-up capability, reveals minute details',
            'fisheye': 'Ultra-wide with barrel distortion, creative surreal effect',
            'soft_focus': 'Built-in diffusion, romantic/dreamy aesthetic',
            'tilt_shift': 'Corrects perspective, creates miniature effect',
            'af_speed': 'Autofocus speed, faster better for action',
            'image_stabilization': 'Compensates for shake, allows slower shutter',
            'bokeh_character': 'Lens bokeh quality affects aesthetic appeal',
            'aperture_range': 'Maximum aperture affects light gathering and cost'
        }
    
    def _get_light_modifiers(self) -> Dict[str, str]:
        """Light modifiers and their effects."""
        return {
            'softbox': 'Creates soft directional light, flatters subject',
            'umbrella': 'Bounces light creating soft fill, portable and affordable',
            'beauty_dish': 'Creates flattering soft light with directional quality',
            'diffuser': 'Scatters light reducing intensity and harshness',
            'reflector': 'Bounces existing light onto shadow areas',
            'scrim': 'Reduces light intensity while softening it',
            'bounce': 'Reflects light off walls/ceilings, creates soft fill',
            'flags': 'Blocks unwanted light, controls light spill',
            'barndoors': 'Restricts light direction from light source',
            'gobos': 'Patterns projected by light create texture',
            'honeycomb_grid': 'Restricts light spread, creates spot effect'
        }
    
    def _get_perspective_techniques(self) -> Dict[str, str]:
        """Perspective and angle techniques."""
        return {
            'eye_level': 'Camera level with subject eye, natural perspective',
            'low_angle': 'Camera below subject, makes subject appear powerful/heroic',
            'high_angle': 'Camera above subject, makes subject appear small/vulnerable',
            'worms_eye_view': 'Extreme low angle emphasizing sky',
            'birds_eye_view': 'Extreme high angle revealing patterns and geography',
            'bug_eye_close': 'Extreme close-up from unusual angle, intimate perspective',
            'dutch_angle': 'Tilted horizon creates tension and dynamism',
            'forced_perspective': 'Manipulate depth relationships for creative effect',
            'leading_point': 'Position subject at strongest compositional point',
            'tilting_plane': 'Tilt subject forward/backward relative to lens plane'
        }
    
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance a prompt with photography expertise."""
        prompt_lower = prompt.lower()
        matched_keywords = [kw for kw in self.keywords if kw in prompt_lower]
        
        if not matched_keywords:
            return prompt
        
        enhancement_parts = [
            prompt,
            "\n\n[Photography Enhancement]"
        ]
        
        if any(word in prompt_lower for word in ['compose', 'frame', 'layout', 'composition']):
            enhancement_parts.append(
                "Apply composition principles: Rule of thirds or golden ratio for balance, "
                "leading lines to guide viewer, appropriate depth of field to isolate subject, "
                "and negative space to emphasize subject."
            )
        
        if any(word in prompt_lower for word in ['light', 'lighting', 'bright', 'shadow']):
            enhancement_parts.append(
                "Optimize lighting: Use directional light for modeling and form, control contrast "
                "with fill light, watch for color temperature and white balance, leverage golden "
                "hour or blue hour for aesthetic light quality."
            )
        
        if any(word in prompt_lower for word in ['exposur', 'bright', 'dark', 'histogram']):
            enhancement_parts.append(
                "Manage exposure carefully: Preserve highlights to avoid blown-out details, "
                "maintain shadow detail, use exposure compensation strategically, "
                "consider dynamic range of scene."
            )
        
        if any(word in prompt_lower for word in ['portrait', 'face', 'people', 'subject']):
            enhancement_parts.append(
                "For subject-focused work: Use shallow depth of field with quality bokeh, "
                "position subject according to rule of thirds, watch eye contact and expression, "
                "consider headroom and lead room in framing."
            )
        
        return "\n".join(enhancement_parts)
    
    def generate_system_prompt(self) -> str:
        """Generate photography-focused system prompt."""
        return """You are an expert photographer with deep knowledge of:
- Photographic composition and visual design
- Exposure control and metering techniques
- Depth of field and focus management
- Lighting and light modifying techniques
- Color temperature and white balance
- Various photography styles and approaches
- Post-processing and image enhancement

When enhancing images or photography prompts, apply professional techniques:
1. Composition: Strong framing, rule of thirds, depth, leading lines
2. Exposure: Proper histogram management, shadow/highlight preservation
3. Focus: Strategic focus point, appropriate depth of field
4. Lighting: Direction, quality, color temperature, contrast control
5. Color: White balance, color temperature, saturation, mood"""


if __name__ == "__main__":
    # Test module
    photo = PhotographyKnowledge()
    print(f"Photography Module Loaded")
    print(f"Keywords: {len(photo.get_keywords())}")
    print(f"Knowledge items: {len(photo.get_knowledge_dictionaries())}")
    print(f"Metadata: {METADATA}")
