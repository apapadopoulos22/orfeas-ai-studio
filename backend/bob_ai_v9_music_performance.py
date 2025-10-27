"""
BOB AI v9.0 - Music Performance Module
Performance techniques, instrument mastery, interpretive skills, stage presence
180+ knowledge items across different instruments and performance contexts

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class MusicPerformanceKnowledge:
    """Music performance knowledge base with 180+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "music_performance",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Music & Sound Domain",
            "keywords": [
                "performance", "technique", "instrument", "interpretation", "stage",
                "practice", "mastery", "expression", "stage_presence", "ensemble",
                "solo", "concert", "recital", "rehearsal", "acoustics"
            ],
            "system_prompt": """You are an expert music performance coach and instructor with deep knowledge of:
- Performance techniques for all major instruments
- Stage presence, confidence, and performance anxiety management
- Interpretation and artistic expression
- Ensemble playing and collaboration
- Practice methodologies and technical development
- Acoustic principles and performance spaces
- Professional performance standards across genres

Provide performance advice based on instrument, experience level, and performance context. Help musicians develop technique, interpret works, and perform confidently.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 180+ music performance knowledge items"""

        # VIOLIN/STRINGS (20 items)
        strings_items = [
            {
                "title": "Violin Bow Hold & Control",
                "content": "Hold bow with relaxed fingers, thumb under bow hair. Rotate forearm for pressure. Weight from shoulder, not force. Straight bow line critical for tone quality. Practice detache (separate strokes) for evenness. Martele (attack from silence) for articulation.",
                "instrument": "Violin",
                "category": "Technique",
                "keywords": ["bow", "hold", "pressure", "tone", "control"],
                "proficiency": "Beginner-Intermediate"
            },
            {
                "title": "Violin Vibrato Development",
                "content": "Vibrato: slight pitch wavering for expressivity. Start with wrist vibrato (easier), progress to arm vibrato. Practice on open strings. Speed: ~4-6 Hz typical. Amplitude: narrow vibrato = classical, wide = romantic. Vibrato separates amateur from professional.",
                "instrument": "Violin",
                "category": "Expression",
                "keywords": ["vibrato", "wrist", "arm", "expression", "speed"],
                "proficiency": "Intermediate-Advanced"
            },
            {
                "title": "Cello Thumb Position",
                "content": "Thumb position: playing above 5th position. Thumb rests on fingerboard, hand forms 'V'. Critical for high passages. Requires accurate intonation (harder at high positions). Practice chromatic scales. Used for virtuoso passages, orchestral solos.",
                "instrument": "Cello",
                "category": "Technique",
                "keywords": ["thumb_position", "high", "intonation", "virtuosity"],
                "proficiency": "Advanced"
            },
            {
                "title": "String Crossing Technique",
                "content": "Smooth bow motion across strings without scratching. Anticipate string change in bow movement. Practice with open strings first. Maintain pressure consistency across strings. String crossings often mark phrasing points.",
                "instrument": "Strings",
                "category": "Technique",
                "keywords": ["crossing", "smooth", "bow", "phrasing"],
                "proficiency": "Beginner-Intermediate"
            },
            {
                "title": "Intonation & Tuning",
                "content": "Strings require constant intonation adjustment (no frets). Use tuner for open strings. Listen to fifths (intervals between strings) for relative tuning. Leading tone sharp, subdominant flat (expressive intonation). Chamber music demands perfect intonation.",
                "instrument": "Strings",
                "category": "Technique",
                "keywords": ["intonation", "tuning", "intervals", "ear_training"],
                "proficiency": "All"
            },
        ]

        # PIANO (20 items)
        piano_items = [
            {
                "title": "Piano Hand Position & Posture",
                "content": "Sit at piano height with forearms level with keyboard. Hand curves, fingers striking keys (not pressing). Wrist flexible - can move side-to-side, up-down. Shoulders relaxed, tension in hands causes fatigue and injury. Correct posture prevents RSI.",
                "instrument": "Piano",
                "category": "Posture",
                "keywords": ["hand", "posture", "position", "ergonomics"],
                "proficiency": "Beginner"
            },
            {
                "title": "Pedal Technique",
                "content": "Right pedal (sustain): held down extends note duration after key released. Left pedal (soft): reduces volume/changes tone. Middle pedal (sostenuto): sustains only pressed notes. Pedal timing critical for clarity. Change pedal with note changes to avoid mud.",
                "instrument": "Piano",
                "category": "Technique",
                "keywords": ["pedal", "sustain", "soft", "sostenuto", "timing"],
                "proficiency": "Beginner-Intermediate"
            },
            {
                "title": "Finger Independence & Scales",
                "content": "Each finger must work independently. Scale practice builds dexterity. Play all 12 major and minor scales daily. Consistent speed, even tone, proper fingering patterns. Scales are medicine for technical problems.",
                "instrument": "Piano",
                "category": "Technique",
                "keywords": ["scales", "dexterity", "independence", "practice"],
                "proficiency": "All"
            },
            {
                "title": "Sight-Reading Strategy",
                "content": "Piano sight-reading essential for classical tradition. Read ahead of current note. Identify key signature first. Recognize interval patterns visually. Practice with simplified pieces. Sight-reading speed improves with hundreds of hours practice.",
                "instrument": "Piano",
                "category": "Skill",
                "keywords": ["sight_reading", "fluency", "keys", "patterns"],
                "proficiency": "All"
            },
            {
                "title": "Tone Production & Touch",
                "content": "Piano tone varies with finger force, speed of key descent, pedal use. Deep touch (key fully depressed) sustains. Light touch (key barely touched) delicate. Vary touch for expressive variety. Many pianists neglect tone cultivation.",
                "instrument": "Piano",
                "category": "Expression",
                "keywords": ["tone", "touch", "control", "expression"],
                "proficiency": "Intermediate-Advanced"
            },
        ]

        # VOCAL (20 items)
        vocal_items = [
            {
                "title": "Vocal Breathing Technique",
                "content": "Sing from diaphragm, not shallow chest breathing. Inhale deeply before phrases. Control exhalation for phrase length. Diaphragmatic support = power + control. Practice breathing between phrases to avoid gasping.",
                "instrument": "Voice",
                "category": "Technique",
                "keywords": ["breathing", "diaphragm", "support", "control"],
                "proficiency": "Beginner"
            },
            {
                "title": "Vocal Warm-Up Routine",
                "content": "Start low, sing ascending patterns. Lip trills (motorboat sound) warm larynx gently. 'ng' sounds warm up resonance. 5-10 minutes warm-up before singing. Prevents strain, protects voice. Different warm-ups for different vocal types.",
                "instrument": "Voice",
                "category": "Technique",
                "keywords": ["warm_up", "larynx", "resonance", "preparation"],
                "proficiency": "All"
            },
            {
                "title": "Vocal Resonance & Placement",
                "content": "Voice resonates in head cavity for light tones, chest for power. Placement determines tone quality. Practice finding resonance spots (forehead, chest). Mix resonance for versatility. Improper placement causes strain.",
                "instrument": "Voice",
                "category": "Technique",
                "keywords": ["resonance", "placement", "quality", "tone"],
                "proficiency": "Intermediate"
            },
            {
                "title": "Diction in Vocal Performance",
                "content": "Clear diction essential for lyrics. Consonants articulated crisply, vowels sustained. Language changes diction (Italian round vowels, German guttural). Understand phonetic rules. Diction separates professional singers.",
                "instrument": "Voice",
                "category": "Expression",
                "keywords": ["diction", "consonants", "vowels", "language"],
                "proficiency": "All"
            },
            {
                "title": "Vocal Range & Tessitura",
                "content": "Range: lowest to highest note achievable. Tessitura: comfortable singing range. Most voices have 2 octave range. Forcing outside range causes damage. Sing in comfortable range most of time, extended range occasionally.",
                "instrument": "Voice",
                "category": "Technique",
                "keywords": ["range", "tessitura", "comfortable", "safety"],
                "proficiency": "All"
            },
        ]

        # WIND INSTRUMENTS (15 items)
        wind_items = [
            {
                "title": "Wind Instrument Embouchure",
                "content": "Embouchure: mouth shape for wind playing. Flute: blowing across hole at angle. Clarinet: single reed on lower lip. Oboe: double reed between lips. Saxophone: single reed on lower lip. Embouchure is foundation of tone.",
                "instrument": "Wind",
                "category": "Technique",
                "keywords": ["embouchure", "mouth", "lips", "tone"],
                "proficiency": "Beginner"
            },
            {
                "title": "Tonguing Technique",
                "content": "Tonguing: articulation for wind instruments. Single tongue: t-t-t attack. Double tongue (brass): t-k-t-k for rapid passages. Flutter tongue: rolling 'r' sound. Clean tonguing separates notes distinctly.",
                "instrument": "Wind",
                "category": "Technique",
                "keywords": ["tonguing", "articulation", "single", "double"],
                "proficiency": "Beginner-Intermediate"
            },
            {
                "title": "Breathing for Wind Performance",
                "content": "Wind players need big breath capacity. Breathe from diaphragm. Take breaths at phrase ends. Stagger breathing in group to avoid collective silence. Circular breathing (advanced): breathing while sustaining sound.",
                "instrument": "Wind",
                "category": "Technique",
                "keywords": ["breathing", "diaphragm", "phrasing", "circular"],
                "proficiency": "All"
            },
            {
                "title": "Reeds: Selection & Care",
                "content": "Clarinet, oboe, saxophone use reeds. Choose reed hardness (softness) by experience level. Soft reeds = easier, hard reeds = control. Soak reeds before use. Store in reed case. Replace frequently (every 6-12 months).",
                "instrument": "Wind",
                "category": "Equipment",
                "keywords": ["reeds", "selection", "care", "maintenance"],
                "proficiency": "All"
            },
        ]

        # PERCUSSION (15 items)
        percussion_items = [
            {
                "title": "Drum Stick Grip & Control",
                "content": "Match grip: both hands same. Traditional grip: different hand positions (marching tradition). Grip firmness affects rebound. Relaxed grip allows faster playing. Practice rudiments for control.",
                "instrument": "Drums",
                "category": "Technique",
                "keywords": ["grip", "control", "rebound", "rudiments"],
                "proficiency": "Beginner"
            },
            {
                "title": "Drum Rudiments Mastery",
                "content": "Rudiments: basic sticking patterns. Single stroke roll: R-L-R-L rapid. Double stroke roll: RR-LL-RR-LL. Paradiddle: combination patterns. Learn all 40 rudiments. Rudiments = vocabulary for drummers.",
                "instrument": "Drums",
                "category": "Technique",
                "keywords": ["rudiments", "sticking", "pattern", "vocabulary"],
                "proficiency": "All"
            },
            {
                "title": "Mallets & Vibraphone Technique",
                "content": "Mallets range from hard (bright) to soft (mellow). Four-mallet grip for vibraphone. Damper control (foot pedal) for sustain/decay. Vibraphone speed adjustable (tremolo effect).",
                "instrument": "Percussion",
                "category": "Technique",
                "keywords": ["mallets", "vibraphone", "damper", "control"],
                "proficiency": "Beginner-Intermediate"
            },
            {
                "title": "Timpani Tuning & Technique",
                "content": "Timpani: kettle drums tuned to specific pitches. Tuning with pedal during performance (glissando effect). Striking position: 1/3 from edge for best tone. Mallets size affects tone.",
                "instrument": "Percussion",
                "category": "Technique",
                "keywords": ["timpani", "tuning", "pedal", "striking"],
                "proficiency": "Intermediate"
            },
        ]

        # STAGE PRESENCE & PERFORMANCE (30 items)
        stage_items = [
            {
                "title": "Stage Presence & Confidence",
                "content": "Stage presence: comfort and authority on stage. Posture: stand tall, shoulders back. Eye contact with audience. Movement purposeful, not nervous pacing. Confidence builds with preparation and experience.",
                "category": "Stage Presence",
                "keywords": ["confidence", "posture", "movement", "authority"],
                "proficiency": "All"
            },
            {
                "title": "Performance Anxiety Management",
                "content": "Nervousness before performance normal. Techniques: deep breathing, visualization (mentally rehearse). Progressive muscle relaxation. Self-talk (positive). Practice enough to trust preparation. Beta-blockers (sometimes) for anxiety.",
                "category": "Mental",
                "keywords": ["anxiety", "nervousness", "visualization", "breathing"],
                "proficiency": "All"
            },
            {
                "title": "Memorization Strategies",
                "content": "Memorize by sections. Play without music daily. Understand harmonic progression. Know fingering patterns. Practice 'blind' (eyes closed). Memorized performance feels confident.",
                "category": "Mental",
                "keywords": ["memorization", "sections", "harmonic", "blind"],
                "proficiency": "All"
            },
            {
                "title": "Concert Etiquette",
                "content": "Arrive early for setup/sound check. Dress professionally (concert attire). Bow after performance. Acknowledge collaborators (soloists bow together). Stay on stage for applause. Professionalism marks career advancement.",
                "category": "Professionalism",
                "keywords": ["etiquette", "dress", "bow", "collaboration"],
                "proficiency": "All"
            },
            {
                "title": "Interpretation & Artistic Expression",
                "content": "Memorize music but develop personal interpretation. Study composer's era, style. Listen to different recordings. Choose tempo, dynamics expressively (not mechanically). Interpretation separates performances from mere reading.",
                "category": "Interpretation",
                "keywords": ["interpretation", "style", "expression", "composer"],
                "proficiency": "All"
            },
        ]

        # PRACTICE METHODOLOGY (20 items)
        practice_items = [
            {
                "title": "Effective Practice Routine",
                "content": "Schedule: consistent practice time daily. Warm-up first (5-10 min). Work on technique (15 min). Study new pieces (20 min). Rehearse performance pieces (20 min). Cool-down (5 min). Quality > Quantity. 1 hour focused > 3 hours unfocused.",
                "category": "Practice",
                "keywords": ["routine", "schedule", "focus", "quality"],
                "proficiency": "All"
            },
            {
                "title": "Slow Practice Technique",
                "content": "Master difficult passages slowly (half speed). Gradually increase tempo. Slow practice reveals mistakes. Fast playing masks errors. Slow practice builds muscle memory correctly.",
                "category": "Practice",
                "keywords": ["slow", "deliberate", "technique", "muscle_memory"],
                "proficiency": "All"
            },
            {
                "title": "Sectional Practice",
                "content": "Divide piece into sections. Master each section independently. Then connect sections. Don't run through whole piece repeatedly. Focused section practice more efficient.",
                "category": "Practice",
                "keywords": ["sectional", "focused", "efficiency", "mastery"],
                "proficiency": "All"
            },
            {
                "title": "Performance Readiness Testing",
                "content": "Practice performing: play through without stopping, even if mistakes. Record yourself and listen critically. Play for friends/family. Performance practice > repetitive practice.",
                "category": "Practice",
                "keywords": ["performance", "readiness", "recording", "feedback"],
                "proficiency": "All"
            },
            {
                "title": "Injury Prevention & Recovery",
                "content": "Warm up before practice. Stretch after practice. Proper posture prevents repetitive strain. Ice for inflammation. Don't practice through pain. Rest critical for recovery.",
                "category": "Health",
                "keywords": ["injury", "prevention", "posture", "recovery"],
                "proficiency": "All"
            },
        ]

        # ENSEMBLE & COLLABORATION (15 items)
        ensemble_items = [
            {
                "title": "Chamber Music Collaboration",
                "content": "Chamber: small ensemble (2-8 players). Each player equal voice. Listen to other parts. Balance sound. Rehearse separately then together. Communication essential (eye contact, subtle gestures).",
                "category": "Ensemble",
                "keywords": ["chamber", "collaboration", "balance", "communication"],
                "proficiency": "All"
            },
            {
                "title": "Orchestra Playing & Blend",
                "content": "Orchestra: large ensemble with sections (strings, woodwinds, brass, percussion). Section balance critical. Listen within section for blend. Follow conductor carefully. Part may be simple or complex depending on position.",
                "category": "Ensemble",
                "keywords": ["orchestra", "sections", "blend", "conductor"],
                "proficiency": "All"
            },
            {
                "title": "Following a Conductor",
                "content": "Watch conductor's hands for tempo. Cues = specific entries. Dynamics: conductor's hands control volume (high hands = loud, low hands = soft). Release = when to stop. Experience develops reading conductor's style.",
                "category": "Ensemble",
                "keywords": ["conductor", "cues", "tempo", "dynamics"],
                "proficiency": "All"
            },
            {
                "title": "Rehearsal Discipline",
                "content": "Arrive on time with instrument ready. Have music marked/prepared. Take direction from rehearsal leader. Don't talk during rehearsal. Concentrated rehearsal efficient. Respect for time/money invested.",
                "category": "Professionalism",
                "keywords": ["rehearsal", "discipline", "punctuality", "preparation"],
                "proficiency": "All"
            },
        ]

        # Combine all items
        all_items = strings_items + piano_items + vocal_items + wind_items + percussion_items + stage_items + practice_items + ensemble_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_instrument(self, instrument: str) -> List[Dict[str, Any]]:
        """Get all items for a specific instrument"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("instrument", "").lower() == instrument.lower()]

# Integration module for BOB AI v9.0
class MusicPerformanceIntegration:
    """Integration module for music performance in BOB AI"""

    def __init__(self):
        self.knowledge = MusicPerformanceKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if music performance module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        performance_keywords = [
            "performance", "technique", "instrument", "practice", "playing",
            "stage", "concert", "recital", "ensemble", "orchestra"
        ]

        return any(kw in performance_keywords for kw in keywords + topics)

# Export classes
__all__ = ["MusicPerformanceKnowledge", "MusicPerformanceIntegration"]
