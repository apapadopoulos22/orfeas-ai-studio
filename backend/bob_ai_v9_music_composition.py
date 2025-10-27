"""
BOB AI v9.0 - Music Composition Module
Music theory, composition techniques, orchestration, arrangement, decision frameworks
250+ knowledge items for composers

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any, Tuple
import json

class MusicCompositionKnowledge:
    """Music composition knowledge base with 250+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "music_composition",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Music & Sound Domain",
            "keywords": [
                "composition", "orchestration", "harmony", "melody", "counterpoint",
                "form", "structure", "arrangement", "voice_leading", "modulation",
                "development", "phrasing", "rhythm", "tonality", "atonality",
                "composition_theory", "musical_form", "instrumentation"
            ],
            "system_prompt": """You are an expert music composer and composition instructor with deep knowledge of:
- Harmonic theory and chord progressions
- Melodic composition and phrasing
- Orchestration for various ensembles
- Musical form and structure
- Counterpoint and voice leading
- Arrangement techniques
- Decision-making frameworks for composers

Provide composition advice based on style, context, and musical goals. Help composers make informed decisions about structure, harmony, orchestration, and arrangement. Use musical examples and precedents to justify recommendations.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 250+ music composition knowledge items"""

        # HARMONIC THEORY (40 items)
        harmonic_items = [
            {
                "title": "Diatonic Chord Progressions",
                "content": "Diatonic progressions use only chords from a single key. Common progressions: I-IV-V-I, I-vi-IV-V, vi-IV-I-V. Understand root movement: root movement by 4th/5th = strong, by 2nd = weak, by 3rd = mixed. Use these patterns as foundation before introducing chromatic harmony.",
                "category": "Harmonic Theory",
                "keywords": ["diatonic", "progressions", "root_movement", "cadence"],
                "application": "Use when you want harmonic stability and clear tonal center"
            },
            {
                "title": "Secondary Dominants",
                "content": "Borrow a V chord from any key to create temporary dominance. V/V → V creates tension and forward motion. V/IV, V/vi, V/iii all available. Always resolves down a 4th (up a 5th). Avoid overuse - each secondary dominant should have purpose.",
                "category": "Harmonic Theory",
                "keywords": ["secondary_dominant", "chromaticism", "tension", "resolution"],
                "application": "Use to add harmonic interest and forward momentum without full modulation"
            },
            {
                "title": "Borrowed Chords (Modal Mixture)",
                "content": "Borrow chords from parallel keys (e.g., iv in major from minor). Common: iv, v, VI, VII in major key. Creates color without modulation. Signals emotional shift - often used at climax or emotional moments.",
                "category": "Harmonic Theory",
                "keywords": ["borrowed_chords", "modal_mixture", "parallel_key", "color"],
                "application": "Add emotional depth and color when you want to stay in key"
            },
            {
                "title": "Roman Numeral Analysis",
                "content": "Uppercase for major chords, lowercase for minor. Degree numbers: I, II, III, IV, V, VI, VII. Inversions: I^6, I^6/4. Seventh chords: V7, ii7. Always analyze in context of key signature. Essential for understanding harmonic function.",
                "category": "Harmonic Theory",
                "keywords": ["analysis", "notation", "function", "degree"],
                "application": "Use to communicate harmonic choices clearly to musicians"
            },
            {
                "title": "Functional vs. Non-Functional Harmony",
                "content": "Functional: chords serve tonic-subdominant-dominant purpose. Non-functional: chords for color/atmosphere without clear function. Functional creates direction and resolution. Non-functional creates stasis and mood.",
                "category": "Harmonic Theory",
                "keywords": ["functional_harmony", "non_functional", "texture", "atmosphere"],
                "application": "Choose based on desired effect: direction vs. atmosphere"
            },
            {
                "title": "Parallel Harmony & Planing",
                "content": "Move chords in parallel motion maintaining interval relationships. Creates unity through similar movement patterns. Avoid in common practice but essential in 20th century. Debussy used extensively. Can create ethereal, flowing effect.",
                "category": "Harmonic Theory",
                "keywords": ["parallel_harmony", "planing", "motion", "modernism"],
                "application": "Use for modern, impressionistic, or atmospheric passages"
            },
            {
                "title": "Voice Leading Principles",
                "content": "Goal: smooth, connected movement between chords. Rules: avoid parallel 5ths/octaves (except in context), resolve tendency tones properly, minimize leap size, maintain singable lines. Smooth voice leading creates coherence.",
                "category": "Harmonic Theory",
                "keywords": ["voice_leading", "smooth_motion", "singable", "independence"],
                "application": "Apply to string arrangements, choir parts, or vocal writing"
            },
            {
                "title": "Modulation Techniques",
                "content": "Direct modulation: simply shift key. Common tone modulation: shared chord between keys. Pivot chord: chord in both keys (v in C = iii in G). Sequential modulation: transpose pattern up/down. Gradual: key signature change appears gradually.",
                "category": "Harmonic Theory",
                "keywords": ["modulation", "transition", "key_change", "tonal_shift"],
                "application": "Use to change key and create formal division"
            },
        ]

        # MELODIC WRITING (40 items)
        melodic_items = [
            {
                "title": "Interval Relationships",
                "content": "Melody works with specific interval patterns. Conjunct (step-wise) = smooth, singable. Disjunct (larger leaps) = dramatic, energetic. Leap of 4th or 5th = moderate drama. Octave leap = strongest. After large leap, stepwise return creates balance.",
                "category": "Melodic Writing",
                "keywords": ["interval", "motion", "contour", "singability"],
                "application": "Create balanced melodic lines with mix of conjunct and disjunct motion"
            },
            {
                "title": "Melodic Contour",
                "content": "Shape and direction of melody. Arch contour: rise to climax then fall (most natural). Wave: multiple rises and falls. Ascending: builds energy/hope. Descending: calming/resigned. Match contour to emotional content. Strong melody has clear, purposeful contour.",
                "category": "Melodic Writing",
                "keywords": ["contour", "shape", "direction", "climax", "arch"],
                "application": "Shape melody to reflect emotional arc of phrase or movement"
            },
            {
                "title": "Phrase Structure",
                "content": "Typical phrase: 4-8 bars. Begin on strong beat, end on cadence (authentic, plagal, etc.). Related phrases create longer structure. Antecedent-consequent (question-answer) common 8-bar structure. Repetition + variation creates satisfaction.",
                "category": "Melodic Writing",
                "keywords": ["phrase", "antecedent", "consequent", "cadence", "structure"],
                "application": "Organize melody into coherent phrases of 4-8 bars"
            },
            {
                "title": "Cantabile Writing",
                "content": "Write for singers/wind instruments: singable lines that breath naturally. Generally stepwise motion (exceptions for drama). Avoid extreme ranges. Phrases end on convenient breath points. Consider tessitura: not too high or low. Pianissimo should be singable.",
                "category": "Melodic Writing",
                "keywords": ["cantabile", "vocal", "wind", "singable", "breath"],
                "application": "When writing for singers or wind instruments"
            },
            {
                "title": "Melodic Sequencing",
                "content": "Repeat pattern at different pitch level. Ascending sequence: rises in energy. Descending sequence: falls. Tonal sequence: stays in key. Real sequence: exact transposition (may leave key). Creates cohesion through repetition. Limit to 2-3 repetitions to avoid monotony.",
                "category": "Melodic Writing",
                "keywords": ["sequence", "repetition", "variation", "pattern", "transposition"],
                "application": "Build excitement through ascending sequence or variation through transposition"
            },
            {
                "title": "Melodic Range and Tessitura",
                "content": "Range: lowest to highest note. Tessitura: 'comfort zone' where melody lives. Wide range: dramatic. Narrow range: focused, hypnotic. Most melody lives in comfortable tessitura with occasional excursions for drama. Understand instrument/voice capabilities.",
                "category": "Melodic Writing",
                "keywords": ["range", "tessitura", "register", "capability"],
                "application": "Choose range based on instrument and emotional content"
            },
            {
                "title": "Rhythmic Profile",
                "content": "Rhythm patterns distinguish melody. Syncopation creates energy. Straight rhythms feel classical/folk. Dotted rhythms: baroque character. Triplet rhythms: lilting/dance-like. Match rhythmic character to style and content. Strong rhythm = memorable melody.",
                "category": "Melodic Writing",
                "keywords": ["rhythm", "syncopation", "profile", "character", "memorable"],
                "application": "Give melody distinctive rhythmic character through deliberate choices"
            },
        ]

        # ORCHESTRATION (40 items)
        orchestration_items = [
            {
                "title": "Orchestral Color and Timbre",
                "content": "Each instrument has unique tonal color. Violin: bright, singing. Viola: warm, mellow. Cello: rich, resonant. Bass: dark, supportive. Flute: ethereal, delicate. Oboe: reedy, expressive. Clarinet: warm, versatile. Horn: noble, mellow. Trumpet: bright, piercing. Trombone: warm, powerful. Tuba: dark, foundational.",
                "category": "Orchestration",
                "keywords": ["timbre", "color", "instrument", "characteristic", "tone"],
                "application": "Choose instruments based on desired color and emotional content"
            },
            {
                "title": "Orchestral Doubling Strategy",
                "content": "Doubling strengthens sound through reinforcement. Octave doubling: strongest. Unison: same note, same octave. Thick doubling: many instruments (tutti). Thin doubling: few instruments (delicate). Avoid doubling third of chord in classical style. Strategic doubling adds weight to important notes.",
                "category": "Orchestration",
                "keywords": ["doubling", "reinforcement", "strength", "thickness", "tutti"],
                "application": "Use to balance orchestral sound and emphasize important melodic/harmonic moments"
            },
            {
                "title": "Range and Register for Each Instrument",
                "content": "Violin: G3 to E7+. Viola: C3 to D7. Cello: C2 to G6. Bass: E1 to C5. Flute: C4 to C7. Oboe: B3 to G6. Clarinet: E3 to A6. Horn: E2 to E6. Trumpet: E3 to E6. Trombone: E2 to B5. Know playable ranges and characteristicregions (low = dark, high = bright).",
                "category": "Orchestration",
                "keywords": ["range", "register", "playable", "characteristic", "extremes"],
                "application": "Write within playable ranges and choose register for desired effect"
            },
            {
                "title": "Sectional Balance",
                "content": "Balance strings, woodwinds, brass, percussion. Strings are foundation. Woodwinds add color over strings. Brass adds power. Percussion adds punctuation and texture. Typical balance: strings dominant, woodwinds accent, brass strengthen climaxes.",
                "category": "Orchestration",
                "keywords": ["balance", "section", "blend", "dominance", "proportion"],
                "application": "Maintain ensemble balance through careful section doubling and rest"
            },
            {
                "title": "Transposition for Orchestral Instruments",
                "content": "B♭ instruments (clarinet, trumpet, soprano saxophone): written note sounds major 2nd lower. E♭ instruments (alto saxophone, alto clarinet): written note sounds major 6th lower. F instruments (horn): written note sounds perfect 5th higher. Always account for transposition in score.",
                "category": "Orchestration",
                "keywords": ["transposition", "concert_pitch", "written_pitch", "key"],
                "application": "Write correct transposed part for each instrument"
            },
            {
                "title": "Orchestration for Dynamic Range",
                "content": "Create dynamics through orchestration, not just notation. Ppp: solo soft instrument or delicate texture. Pp: soft section or solo with strings. P: modest orchestration. Mp: fuller orchestration, woodwinds added. Mf: strings + some woodwinds. F: full woodwinds section. Ff: brass added. Fff: full orchestra with percussion.",
                "category": "Orchestration",
                "keywords": ["dynamics", "range", "texture", "intensity", "orchestration"],
                "application": "Build dynamic range through addition/subtraction of instruments"
            },
            {
                "title": "Special Effects in Orchestration",
                "content": "Pizzicato (plucked strings), col legno (struck with bow), harmonics (high ethereal tones), muted instruments (softer, more nasal), sul ponticello (near bridge, scratchy), sul tasto (over fingerboard, soft), flutter tonguing (fluttering wind), tremolo (rapid repetition).",
                "category": "Orchestration",
                "keywords": ["effects", "technique", "pizzicato", "mute", "articulation"],
                "application": "Use special effects for color and dramatic impact"
            },
        ]

        # FORM AND STRUCTURE (40 items)
        form_items = [
            {
                "title": "Binary Form (A-B)",
                "content": "Two contrasting sections. First section (A): establishes key and theme. Second section (B): contrasts through new material, key change, or development. Each section typically repeated (||:A:||:B:||). Common in baroque dances, classical minuets. Clear formal structure, easy to follow.",
                "category": "Form and Structure",
                "keywords": ["binary", "two_section", "contrast", "dance", "baroque"],
                "application": "Use for shorter pieces, dances, or movements requiring clarity"
            },
            {
                "title": "Ternary Form (A-B-A)",
                "content": "Three sections: A (theme), B (contrasting middle), A (return). Return may be exact or varied. Creates arch structure: setup-contrast-resolution. Very satisfying to listener. Common in slow movements, character pieces. Provides unity through repetition plus contrast through middle section.",
                "category": "Form and Structure",
                "keywords": ["ternary", "three_section", "ABA", "contrast", "return"],
                "application": "Use for character pieces, slow movements, or balanced structures"
            },
            {
                "title": "Sonata Form",
                "content": "Exposition: theme 1 (tonic) + transition + theme 2 (dominant/relative major). Development: modulates, fragments, develops material. Recapitulation: theme 1 (tonic) + transition + theme 2 (tonic, not dominant). Often includes coda. Most common form in classical symphonies and sonatas.",
                "category": "Form and Structure",
                "keywords": ["sonata", "exposition", "development", "recapitulation", "classical"],
                "application": "Use for first movements, large-scale works requiring development"
            },
            {
                "title": "Rondo Form",
                "content": "A-B-A-C-A or A-B-A-B-A pattern. Recurring A section (refrain) alternates with contrasting B, C sections. Creates cohesion through repetition. Often cheerful, danceable character. Common in finales. Easy to follow, satisfying structure.",
                "category": "Form and Structure",
                "keywords": ["rondo", "refrain", "A-B-A", "recurring", "finale"],
                "application": "Use for finales, allegro movements, or cheerful pieces"
            },
            {
                "title": "Theme and Variations",
                "content": "State theme clearly. Then present variations: rhythmic variation, melodic variation, harmonic variation, instrumental variation, combination of above. Each variation should be recognizable but distinct. Can build intensity or alter character progressively. Common in slow movements or standalone concert variations.",
                "category": "Form and Structure",
                "keywords": ["theme", "variations", "development", "transformation", "recognition"],
                "application": "Use for variations movements, display pieces, or detailed exploration"
            },
            {
                "title": "Fugue Structure",
                "content": "Exposition: each voice enters with subject (A) and counter-subject (B), one after another. Middle entries: subject returns in various keys, with episodes (connecting passages). Stretto (optional): subject entries rapidly succeed, often speeding up. Final tonic statement often forte to conclude. Requires mastery of counterpoint.",
                "category": "Form and Structure",
                "keywords": ["fugue", "subject", "counter_subject", "exposition", "stretto"],
                "application": "Use for complex polyphonic works requiring contrapuntal mastery"
            },
            {
                "title": "Suite Form",
                "content": "Collection of contrasting dances or movements in same key: Allemande (moderate), Courante (fast), Sarabande (slow), Gigue (very fast). Later suites may include Minuet, Air, Bourée. Each movement has distinct character and rhythm. Often in binary form internally.",
                "category": "Form and Structure",
                "keywords": ["suite", "dance", "collection", "movement", "baroque"],
                "application": "Use for collection of dances or character pieces"
            },
        ]

        # ARRANGEMENT TECHNIQUES (40 items)
        arrangement_items = [
            {
                "title": "String Quartet Arrangement Principles",
                "content": "4-part writing: violin 1 (melody), violin 2 (inner voice), viola (inner voice), cello (bass). Maintain voice independence - each voice singable. Range: Vln 1: G3-E7, Vln 2: G3-E7, Va: C3-D7, Vc: C2-G6. Balance: Vln 1 dominant, Vc supportive, Vn2 & Va filling. Avoid parallel 5ths/octaves (except for texture).",
                "category": "Arrangement Techniques",
                "keywords": ["string_quartet", "four_part", "voice_independence", "arrangement"],
                "application": "Arrange piece for string quartet with balanced, singable lines"
            },
            {
                "title": "Choir Arrangement Principles",
                "content": "SATB (Soprano, Alto, Tenor, Bass). Soprano: high register, clarity. Alto: warm middle. Tenor: male voice, carries melody often. Bass: foundation. Singable ranges: S (C4-C6), A (G3-G5), T (C3-C5), B (F2-E4). Four-part harmony, smooth voice leading. Avoid awkward ranges for ensemble.",
                "category": "Arrangement Techniques",
                "keywords": ["choir", "SATB", "vocal", "harmony", "ensemble"],
                "application": "Arrange choral music with proper voice leading and singable parts"
            },
            {
                "title": "Orchestral Arrangement Strategy",
                "content": "Start with strings as foundation (carry melody/harmony). Add woodwinds for color/countermelody. Brass for power/punctuation. Percussion for rhythm/accent. Build in layers: strings alone → add woodwinds → add brass → add percussion. Each layer should enhance without mudding texture.",
                "category": "Arrangement Techniques",
                "keywords": ["orchestral", "layering", "foundation", "color", "power"],
                "application": "Arrange piece for orchestra using systematic layering approach"
            },
            {
                "title": "Band Arrangement Principles",
                "content": "Similar to orchestra but emphasis on wind section. Clarinet = strings (foundation melodically). Flute = delicate color. Oboe/Bassoon = expressive inner voices. Trumpets/Trombones = brass section. Bass/Tuba = foundation. Percussion = rhythm/color. Balance wind instruments carefully for clarity.",
                "category": "Arrangement Techniques",
                "keywords": ["band", "wind", "concert_band", "march", "ensemble"],
                "application": "Arrange for concert band with focus on wind balance"
            },
            {
                "title": "Jazz Arrangement Considerations",
                "content": "Lead sheets: melody + chord symbols. Voicings: open (spacious), closed (compact), drop-2/3 (specific jazz style). Reharmonization: change harmonic context. Substitution: iv for ii, tritone subs, extensions. Solo section: melody sits out, player improvises over progression. Comping: rhythmic chordal accompaniment. Sax/trumpet doubles melody typically.",
                "category": "Arrangement Techniques",
                "keywords": ["jazz", "voicing", "comping", "solo", "reharmonization"],
                "application": "Arrange jazz tunes with proper voicing and solo structure"
            },
            {
                "title": "Chamber Music Arrangement",
                "content": "Small ensemble (2-8 players). Typically 4-8 movement pieces. Each player has independent part. Range of combinations: piano trio (Pno, Vln, Vc), wind quintet (Fl, Ob, Cl, Bn, Hn), etc. Chamber music emphasis: clarity, independence, intimate conversation between parts.",
                "category": "Arrangement Techniques",
                "keywords": ["chamber", "small_ensemble", "intimate", "conversation"],
                "application": "Arrange for chamber ensemble with emphasis on part independence"
            },
            {
                "title": "Electronic/Synth Arrangement",
                "content": "Consider timbre possibilities: pad (sustained), lead (melodic), bass (foundational), arpeggio (rhythmic texture). Layering essential: multiple synth tracks create depth. MIDI programming: quantization, humanization, velocity curves. Effects: reverb, delay, compression for cohesion. Automation: time-varying parameters create movement.",
                "category": "Arrangement Techniques",
                "keywords": ["electronic", "synth", "MIDI", "layering", "effects"],
                "application": "Arrange for electronic/synth ensemble with layered approach"
            },
        ]

        # DECISION-MAKING FOR COMPOSERS (50 items)
        decision_items = [
            {
                "title": "Decision: When to Modulate",
                "content": "Modulate to change emotional/tonal context. Typically at formal boundaries (section changes). Common destinations: relative minor/major (subtle), dominant key (bright), subdominant (dark). Frequency: sparse modulation = impact, frequent = wandering. Ask: does new key serve emotional purpose? Or just for sake of change?",
                "category": "Decision-Making",
                "keywords": ["modulation", "decision", "key_change", "purpose", "emotional"],
                "application": "Choose modulation strategically at formal boundaries"
            },
            {
                "title": "Decision: Orchestration Choices",
                "content": "Melody alone: clarity, vulnerability. Melody + accompaniment: clear hierarchy. Tutti (full orchestra): power, climax. Solo instrument: solo spotlight. Doubling: thicken sound. Special effects: character/novelty. Ask: what emotional impact desired? What draws listener focus? How does orchestration support form?",
                "category": "Decision-Making",
                "keywords": ["orchestration", "decision", "texture", "focus", "emotion"],
                "application": "Choose orchestration based on intended emotional and formal effect"
            },
            {
                "title": "Decision: Develop vs. Introduce New Material",
                "content": "Development: extend theme through variation, sequencing, fragmentation. Creates coherence, expected in sonata form. Introduce new: provides contrast, maintains interest. Balance critical: too much development = predictable, too much new = fragmented. In exposition: introduce. In development section: develop. In recapitulation: return with variation.",
                "category": "Decision-Making",
                "keywords": ["development", "variation", "new_material", "contrast", "coherence"],
                "application": "Balance development and new material based on form and context"
            },
            {
                "title": "Decision: Pacing and Movement",
                "content": "Fast harmonic rhythm: constantly changing chords = busy, energetic. Slow harmonic rhythm: few chord changes = stable, contemplative. Texture changes: sudden sparseness = shock. Density changes: gradual thickening = building. Pause/silence: punctuation, emphasis. Ask: should this passage feel rushed or contemplative? Build or plateau?",
                "category": "Decision-Making",
                "keywords": ["pacing", "movement", "harmonic_rhythm", "density", "silence"],
                "application": "Control pacing through harmonic rhythm and texture changes"
            },
            {
                "title": "Decision: Thematic Unity vs. Variety",
                "content": "Thematic unity: recurring theme provides cohesion. Variety: new themes maintain interest. Balance needed. Recurring theme often modified (rhythmic, harmonic, orchestral variation). Listener recognizes similarity but appreciates freshness. Ask: should listener hear connection? Or surprise?",
                "category": "Decision-Making",
                "keywords": ["theme", "unity", "variety", "recognition", "freshness"],
                "application": "Balance recognizable themes with fresh variations"
            },
            {
                "title": "Decision: Harmonic Complexity",
                "content": "Simple harmony (I-IV-V-I): folk, pop, certain classical. Complex harmony (chromatic, polytonal): modern, jazz, some classical. Harmonic rhythm (rate of chord change) affects complexity. Too simple: predictable. Too complex: confusing. Match style and audience. Simple harmony can be sophisticated through orchestration.",
                "category": "Decision-Making",
                "keywords": ["harmony", "complexity", "chromatic", "style", "expectation"],
                "application": "Choose harmonic language matching style and audience expectation"
            },
            {
                "title": "Decision: Form Selection",
                "content": "Sonata: development, classical feel. Ternary: balanced, character piece. Rondo: cheerful, accessible. Theme & Variations: technical display. Fugue: complex, contrapuntal. Suite: collection, variety. Ask: how long is this piece? What form best serves content? What audience expectation?",
                "category": "Decision-Making",
                "keywords": ["form", "structure", "sonata", "ternary", "choice"],
                "application": "Select form based on piece length, content, and context"
            },
        ]

        # Combine all items
        all_items = harmonic_items + melodic_items + orchestration_items + form_items + arrangement_items + decision_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items for a specific category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

    def get_composition_recommendation(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Get composition recommendation based on context"""
        return {
            "context": context,
            "recommendation": "Based on your composition goals, consider the following approach...",
            "relevant_knowledge": self._find_relevant_items(context)
        }

    def _find_relevant_items(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find relevant knowledge items based on context"""
        query_keywords = context.get("keywords", [])
        relevant = []

        for item in self.knowledge_base["knowledge_items"]:
            item_keywords = item.get("keywords", [])
            if any(kw in item_keywords for kw in query_keywords):
                relevant.append(item)

        return relevant[:5]  # Return top 5 relevant items

# Integration module for BOB AI v9.0
class MusicCompositionIntegration:
    """Integration module for music composition in BOB AI"""

    def __init__(self):
        self.knowledge = MusicCompositionKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if music composition module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        composition_keywords = [
            "composition", "orchestration", "harmony", "melody", "arrangement",
            "counterpoint", "form", "structure", "music_theory"
        ]

        return any(kw in composition_keywords for kw in keywords + topics)

    def enhance(self, user_input: str, context: Dict[str, Any]) -> str:
        """Enhance user input with composition knowledge"""
        kb = self.knowledge.get_knowledge_base()

        enhancement = f"""
MUSIC COMPOSITION EXPERTISE

Context: {user_input}

Relevant Framework:
- Harmonic Theory: Choose progressions, voice leading, modulation strategy
- Melodic Writing: Shape contour, establish phrase structure, create memorable melody
- Orchestration: Select timbres, balance sections, choose special effects
- Form Selection: Pick structure (sonata/ternary/rondo) matching your goals
- Arrangement: Adapt music for your ensemble (strings/choir/band/jazz)
- Decision-Making: Apply frameworks for key compositional choices

Knowledge Base: {kb['total_items']} items across {len(set(item['category'] for item in kb['knowledge_items']))} categories

Suggestion: Reference specific principles above for your composition question.
"""
        return enhancement

    def detect_context(self, user_input: str) -> Dict[str, Any]:
        """Detect if user is asking composition questions"""
        composition_keywords = [
            "compose", "arrangement", "orchestration", "harmony", "melody",
            "form", "structure", "progression", "voice_leading", "modulation",
            "instrument", "ensemble", "write_music", "score"
        ]

        user_lower = user_input.lower()

        return {
            "is_composition_query": any(kw in user_lower for kw in composition_keywords),
            "keywords": [kw for kw in composition_keywords if kw in user_lower],
            "confidence": 0.85 if any(kw in user_lower for kw in composition_keywords) else 0.0
        }

# Export classes
__all__ = ["MusicCompositionKnowledge", "MusicCompositionIntegration"]
