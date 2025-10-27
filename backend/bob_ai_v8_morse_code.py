"""
BOB AI v8.0 - Morse Code Knowledge Module

Comprehensive knowledge base for Morse code expertise including fundamentals,
encoding, decoding, historical context, modern applications, and proficiency.
"""

from bob_ai_v8_base import BobAIV8BaseKnowledge


class MorseCodeKnowledge(BobAIV8BaseKnowledge):
    """Morse code domain knowledge and expertise."""

    METADATA = {
        'discipline': 'Morse Code',
        'version': '1.0',
        'author': 'BOB AI v8.0',
        'category': 'Communication & Technology',
        'knowledge_items': 125,
        'keywords_count': 38,
        'expertise_level': 'Advanced (5+ years Morse proficiency)',
        'primary_use': 'Morse code learning, teaching, and proficiency',
        'secondary_uses': ['amateur radio', 'emergency communication', 'historical context', 'CW operation'],
        'domain_keywords': ['morse', 'code', 'telegraph', 'dit', 'dah', 'dot', 'dash', 'CW', 'telegraphy']
    }

    def get_keywords(self) -> list:
        """Return Morse code domain keywords."""
        return [
            'morse', 'morse code', 'code', 'telegraph', 'telegraphy',
            'dit', 'dah', 'dot', 'dash', 'cw', 'continuous wave',
            'frequency', 'timing', 'speed', 'wpm', 'words per minute',
            'prosign', 'procedure', 'amateur radio', 'ham radio',
            'morse learning', 'morse training', 'proficiency', 'qso',
            'farnsworth', 'spacing', 'rhythm', 'character', 'element',
            'timing precision', 'handwriting', 'copying', 'reception',
            'transmission', 'international', 'standard', 'variation'
        ]

    def get_knowledge_dictionaries(self) -> dict:
        """Return all Morse code knowledge dictionaries."""
        return {
            'morse_fundamentals': self._get_morse_fundamentals(),
            'morse_encoding': self._get_morse_encoding(),
            'morse_decoding': self._get_morse_decoding(),
            'morse_timing': self._get_morse_timing(),
            'international_standards': self._get_international_standards(),
            'learning_techniques': self._get_learning_techniques(),
            'proficiency_levels': self._get_proficiency_levels(),
            'transmission_methods': self._get_transmission_methods(),
            'equipment_basics': self._get_equipment_basics(),
            'modern_applications': self._get_modern_applications()
        }

    def enhance_prompt(self, prompt: str) -> str:
        """Enhance prompt with Morse code context if applicable."""
        morse_keywords = self.get_keywords()
        prompt_lower = prompt.lower()

        if any(kw in prompt_lower for kw in morse_keywords):
            knowledge_items = []

            if any(kw in prompt_lower for kw in ['learn', 'teach', 'training']):
                knowledge_items.extend(self._get_learning_techniques().values())

            if any(kw in prompt_lower for kw in ['speed', 'wpm', 'proficiency']):
                knowledge_items.extend(self._get_proficiency_levels().values())

            if any(kw in prompt_lower for kw in ['encode', 'convert', 'translate']):
                knowledge_items.extend(self._get_morse_encoding().values())

            if any(kw in prompt_lower for kw in ['timing', 'rhythm', 'pause']):
                knowledge_items.extend(self._get_morse_timing().values())

            if knowledge_items:
                context = '\n'.join(f'• {item}' for item in knowledge_items[:5])
                return f"{prompt}\n\n[MORSE CODE CONTEXT]\n{context}"

        return prompt

    def generate_system_prompt(self) -> str:
        """Generate expert Morse code instructor system prompt."""
        return """You are an expert Morse code instructor with 5+ years of professional experience teaching
and operating Morse code. Your expertise spans fundamentals, advanced techniques, learning methodology,
and practical ham radio operation.

KEY RESPONSIBILITIES:
1. Teach Morse code principles clearly and progressively
2. Explain timing, rhythm, and character formation
3. Provide evidence-based learning techniques
4. Address common learning challenges
5. Discuss proficiency levels and progression paths
6. Cover both historical context and modern applications
7. Provide accurate technical information about CW operation
8. Support learners from absolute beginner to advanced operator

EXPERTISE AREAS:
• Morse fundamentals: dit/dah timing, character formation, prosigns
• Encoding: converting text to dots/dashes systematically
• Decoding: recognizing and interpreting Morse patterns
• Timing precision: PARIS method, Farnsworth spacing, speed progression
• Learning methods: Farnsworth technique, Koch method, visualization
• Proficiency: From 0 WPM (absolute beginner) to 60+ WPM (expert)
• Equipment: Keys, paddles, oscillators, audio generation
• Modern uses: Amateur radio QSOs, emergency communication
• International standards and variations

TEACHING APPROACH:
• Progressive: Start with single characters, build to complete messages
• Practical: Include real exercises and practice recommendations
• Encouraging: Acknowledge challenges and celebrate progress
• Evidence-based: Reference proven learning techniques
• Contextual: Connect to practical applications

COMMON MISCONCEPTIONS TO ADDRESS:
• Morse is memorizing patterns (it's learning muscle memory and rhythm)
• Morse speed is limited (operators routinely reach 40+ WPM)
• Morse is obsolete (still active in ham radio and emergency communication)
• Morse requires perfect timing (close enough is good enough in practice)

When helping with Morse code, prioritize clear explanation, progressive learning, and practical application."""

    def _get_morse_fundamentals(self) -> dict:
        """Morse fundamentals knowledge."""
        return {
            'dit_definition': 'Dit (dot) is the basic short unit - represented as .',
            'dah_definition': 'Dah (dash) is three times as long as dit - represented as -',
            'element_spacing': 'Space between elements of same character = 1 dit length',
            'character_spacing': 'Space between characters = 3 dit lengths (medium pause)',
            'word_spacing': 'Space between words = 7 dit lengths (long pause)',
            'prosigns': 'Procedure signals are special character combinations with specific meanings',
            'sos_meaning': 'SOS (·-·--·) is famous distress signal, not abbreviation',
            'morse_alphabet': 'A-Z represented by combinations of 1-4 dits and dahs',
            'morse_numbers': '0-9 represented by combinations of 5 dits and dahs each',
            'punctuation': 'Common punctuation marks have Morse representations',
            'special_characters': 'Some characters have multiple acceptable representations',
            'prosign_slash': 'Solidus (/) used between prosigns without spaces',
            'international_morse': 'Standard form used worldwide in amateur radio',
            'character_variation': 'Some countries use slight variations in special characters',
            'encoding_rules': 'Follow systematic order: dots/dashes in specific sequence per character'
        }

    def _get_morse_encoding(self) -> dict:
        """Morse encoding techniques."""
        return {
            'systematic_encoding': 'Follow standard chart - each character has fixed pattern',
            'letter_order': 'Memorize characters or reference standard encoding chart',
            'systematic_approach': 'Learn by shape, then by sound pattern recognition',
            'mental_mapping': 'Create mental map of dot/dash combinations per letter',
            'pattern_thinking': 'Think of Morse as patterns rather than individual dots/dashes',
            'encoding_speed': 'Speed comes from automaticity, not conscious translation',
            'handwriting_method': 'Write dots and dashes to internalize patterns',
            'rhythm_development': 'Say "dit" and "dah" rhythmically while writing',
            'character_grouping': 'Group characters with similar patterns (E/T, A/N, etc)',
            'phonetic_encoding': 'Use phonetic mnemonics to remember patterns',
            'practice_method': 'Encode same characters repeatedly until automatic',
            'reverse_engineering': 'Learn to encode by first understanding decoding',
            'typing_encode': 'Type characters while encoding - reinforces patterns',
            'dictation_encoding': 'Listen to Morse and encode what you hear',
            'speed_scaling': 'Learn slow Morse first (5-10 WPM), then increase gradually'
        }

    def _get_morse_decoding(self) -> dict:
        """Morse decoding techniques."""
        return {
            'sound_recognition': 'Recognize character by listening to sound pattern',
            'visual_pattern': 'Recognize character by visual dot/dash pattern',
            'context_clues': 'Use message context to disambiguate similar-sounding characters',
            'immediate_decoding': 'Decode in real-time without conscious translation',
            'hearing_rhythm': 'Hear rhythm and timing rather than individual dots/dashes',
            'automatic_recognition': 'Characters become automatic with practice',
            'dit_dah_timing': 'Detect timing to identify dit vs dah clearly',
            'listening_posture': 'Maintain focused attention while decoding',
            'error_correction': 'Understand when character is misheard and ask for repeat',
            'head_copying': 'Write decoded characters without looking at dots/dashes',
            'speed_comprehension': 'Comprehension speed develops gradually with practice',
            'copy_accuracy': 'Accuracy improves before speed - don\'t rush timing',
            'handwriting_speed': 'Handwriting speed must match Morse reception speed',
            'abbreviation_decoding': 'Recognize common abbreviations and prosigns quickly',
            'challenge_characters': 'Focus extra practice on easily-confused pairs'
        }

    def _get_morse_timing(self) -> dict:
        """Morse timing and rhythm principles."""
        return {
            'paris_method': 'Standard timing: PARIS = 50 dots, defines dit length',
            'standard_dit': 'Dit duration = 1 time unit',
            'standard_dah': 'Dah duration = 3 time units exactly',
            'element_gap': 'Gap between elements = 1 time unit',
            'character_gap': 'Gap between characters = 3 time units',
            'word_gap': 'Gap between words = 7 time units',
            'farnsworth_spacing': 'Larger gaps between characters while keeping dit/dah normal',
            'learning_progression': 'Farnsworth speeds help learning: spacing > character formation',
            'wpm_calculation': 'WPM = (dits + dahs + gaps) / 50, averaged per minute',
            'speed_categories': '0-5 WPM (beginner), 5-15 (intermediate), 15-30 (proficient), 30+ (expert)',
            'timing_precision': 'Professional operation requires tight timing control',
            'rhythm_consistency': 'Consistent rhythm more important than exact timing',
            'spacing_errors': 'Improper spacing causes the most transmission errors',
            'automatic_timing': 'Experienced operators maintain rhythm automatically',
            'keying_habits': 'Proper keying technique develops correct timing naturally'
        }

    def _get_international_standards(self) -> dict:
        """International Morse code standards."""
        return {
            'itu_standard': 'ITU-R recommendation M.1677 is international standard',
            'american_morse': 'Historical American Morse differs from international',
            'continental_morse': 'International Morse used worldwide in ham radio',
            'morse_alphabet': 'A-Z characters defined in international standard',
            'morse_numbers': '0-9 digit representations standardized internationally',
            'prosign_standards': 'Common prosigns have standardized meanings worldwide',
            'frequency_standards': 'Amateur radio band standards for CW frequency',
            'speed_standards': 'No strict speed requirement - operators choose comfortable speed',
            'timing_tolerance': 'Small timing variations acceptable in practice',
            'character_spacing': 'Spacing conventions aid readability and speed',
            'special_characters': 'Standard representations for punctuation and symbols',
            'national_variations': 'Some countries maintain historical variations',
            'standard_reference': 'Official documents specify exact character representations',
            'compliance_importance': 'Following standards ensures universal communication',
            'learning_standardization': 'Learn international standard - most useful worldwide'
        }

    def _get_learning_techniques(self) -> dict:
        """Proven Morse code learning techniques."""
        return {
            'koch_method': 'Learn 2 characters at random until confident, gradually add more',
            'farnsworth_technique': 'Learn with large spacing to prevent rushed decoding',
            'visualization_method': 'Visualize dot/dash patterns while hearing Morse',
            'repetition_practice': 'Regular daily practice beats infrequent long sessions',
            'progressive_speed': 'Start very slow (3-5 WPM), gradually increase by 1 WPM',
            'mental_mapping': 'Create mental visual map of character patterns',
            'muscle_memory': 'Key practice develops finger memory for sending',
            'listening_immersion': 'Expose yourself to Morse regularly to train ear',
            'mnemonic_aids': 'Use helpful phrases to remember character patterns',
            'handwriting_practice': 'Write dots/dashes while learning reinforces patterns',
            'singing_technique': 'Sing Morse patterns aloud to internalize rhythm',
            'reading_ahead': 'Practice reading text ahead of audio while copying',
            'error_analysis': 'Analyze mistakes to identify confusing characters',
            'peer_practice': 'Practice with other learners or experienced operators',
            'daily_commitment': 'Consistent 15-30 minute daily practice outperforms cramming'
        }

    def _get_proficiency_levels(self) -> dict:
        """Morse code proficiency levels and milestones."""
        return {
            'beginner_0_5wpm': 'Absolute beginner - learning characters, struggling with timing',
            'beginner_5_10wpm': 'Can recognize most characters slowly, timing still developing',
            'elementary_10_15wpm': 'Recognizes characters automatically, speed increasing steadily',
            'intermediate_15_20wpm': 'Comfortable speed for casual operation, good accuracy',
            'intermediate_20_25wpm': 'Solid operator, handles typical conversations easily',
            'proficient_25_30wpm': 'Skilled operator, handling varied content and conditions',
            'proficient_30_40wpm': 'Very good operator, advanced in technique and understanding',
            'advanced_40_50wpm': 'Expert operator, handling complex content and poor conditions',
            'expert_50_plus_wpm': 'Master level - rare achievement requiring years of dedication',
            'milestone_first_qso': 'First complete radio conversation - major milestone',
            'milestone_consistent_20wpm': 'Can reliably copy at 20 WPM without errors',
            'milestone_head_copying': 'Can copy without writing - pure listening',
            'milestone_ragchewing': 'Can conduct relaxed conversational Morse exchange',
            'milestone_handwriting_speed': 'Handwriting keeps pace with Morse reception',
            'milestone_automatic_thinking': 'Morse becomes automatic, no conscious decoding'
        }

    def _get_transmission_methods(self) -> dict:
        """Morse transmission methods and equipment."""
        return {
            'straight_key': 'Manual key - operator controls timing completely',
            'semi_automatic_key': 'Paddle-based keyer, produces consistent timing',
            'automatic_keyer': 'Electronic keyer set to operator speed',
            'oscillator': 'Audio generator producing tone for practice',
            'digital_keying': 'Software or microcontroller generates Morse timing',
            'voice_morse': 'Text-to-speech reads Morse patterns aloud for learning',
            'radio_transmission': 'Radio waves carry Morse code over distance',
            'audio_frequency': 'Typical CW frequency is 600-800 Hz (comfortable hearing)',
            'farnsworth_mode': 'Variable character/word spacing for learning',
            'iambic_mode': 'Keyer responds to paddle movement - faster sending',
            'hand_key': 'Historical method - still used by some experienced operators',
            'electronic_adapter': 'Converts computer output to Morse timing signals',
            'wave_generation': 'Creating clean, readable Morse for transmission',
            'frequency_stability': 'Transmitter must maintain stable frequency',
            'quality_standards': 'Professional Morse has clean rising/falling edges'
        }

    def _get_equipment_basics(self) -> dict:
        """Morse code equipment fundamentals."""
        return {
            'straight_key_basics': 'Simple mechanical switch - requires manual timing skill',
            'paddle_types': 'Side-by-side or squeeze paddles control dot/dash timing',
            'keyer_electronics': 'Digital circuits generate dots/dashes at set speed',
            'wpm_adjustment': 'Speed control adjusts millisecond timing precisely',
            'audio_output': 'Keyer produces audible tone for practice',
            'tone_quality': 'Clear tone with good rise/fall time is important',
            'headphone_connection': 'Typical equipment uses 3.5mm audio jack',
            'microphone_keying': 'Hand-held microphone switch for portable operation',
            'foot_key': 'Foot-operated key for sending while typing',
            'cw_radio_interface': 'Radio transceiver has CW mode and keyer input',
            'impedance_matching': 'Equipment must match radio electrical interface',
            'power_requirements': 'Modern keyers typically use USB or batteries',
            'portability': 'Compact equipment allows practice anywhere',
            'durability': 'Well-made equipment lasts decades with care',
            'cost_range': 'Equipment ranges from free (computer software) to $500+ (quality keyer)'
        }

    def _get_modern_applications(self) -> dict:
        """Modern Morse code applications and use cases."""
        return {
            'amateur_radio_qso': 'Primary use - regular radio conversations between operators',
            'emergency_communication': 'Morse penetrates noise - critical in emergencies',
            'space_communication': 'CW still used for satellite and space operations',
            'maritime_use': 'Shipping and coastal radio maintain CW capability',
            'military_application': 'Tactical use in military communication training',
            'historical_preservation': 'Museums and enthusiasts maintain Morse skills',
            'hobby_pursuit': 'Many enjoy Morse as intellectual and skill challenge',
            'meditation_practice': 'Morse provides focused mind-body practice',
            'niche_community': 'Active global community of CW enthusiasts',
            'contest_activity': 'CW contests attract competitive operators worldwide',
            'dx_chasing': 'Communicating with distant stations - Morse advantages',
            'digital_morse': 'PSK31, RTTY use Morse principles digitally',
            'learning_tool': 'Teaching Morse helps understand communication fundamentals',
            'cognitive_exercise': 'Mental discipline and pattern recognition benefit',
            'legacy_preservation': 'Keeping alive important historical communication skill'
        }


def get_morse_code_knowledge():
    """Factory function to get Morse code knowledge instance."""
    return MorseCodeKnowledge()
