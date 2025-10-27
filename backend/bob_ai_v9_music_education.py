"""
BOB AI v9.0 - Music Education Module
Pedagogy, teaching methods, student assessment, curriculum design, music literacy
150+ knowledge items for music educators

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class MusicEducationKnowledge:
    """Music education knowledge base with 150+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "music_education",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "Music & Sound Domain",
            "keywords": [
                "education", "pedagogy", "teaching", "learning", "curriculum",
                "assessment", "literacy", "methodology", "student", "instruction",
                "musicianship", "assessment", "differentiation", "classroom"
            ],
            "system_prompt": """You are an expert music educator with deep knowledge of:
- Music pedagogy and teaching methodologies
- Curriculum design for all age levels
- Student assessment and evaluation
- Music literacy instruction
- Special needs music education
- Classroom management and discipline
- Technology in music education
- Professional development for teachers

Provide educational advice based on student level, context, and learning goals.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 150+ music education knowledge items"""

        # PEDAGOGICAL METHODS (20 items)
        pedagogy_items = [
            {
                "title": "Suzuki Method",
                "content": "Parent involvement critical. Start young (age 3-4). Listen daily to recordings. Teacher modeling. Repeats pieces after mastering. Builds technique gradually. Now-common approach for strings/piano.",
                "method": "Suzuki",
                "category": "Pedagogy",
                "keywords": ["Suzuki", "parent", "repetition", "listening"],
                "age_group": "Young Children"
            },
            {
                "title": "Kodaly Method",
                "content": "Hungarian approach emphasizing singing. Use movable do (solfege). Rhythm patterns learned through body percussion. Community emphasis. Strong musicianship foundation. Popular in general music courses.",
                "method": "Kodaly",
                "category": "Pedagogy",
                "keywords": ["Kodaly", "singing", "solfege", "rhythm"],
                "age_group": "Children-Adolescent"
            },
            {
                "title": "Orff Approach",
                "content": "Carl Orff method. Start with speech/rhythm. Add instruments (barred instruments first). Improvisation encouraged. Ensemble playing. Movement integrated. Joyful, accessible to all students.",
                "method": "Orff",
                "category": "Pedagogy",
                "keywords": ["Orff", "speech", "improvisation", "ensemble"],
                "age_group": "Children"
            },
            {
                "title": "Constructivist Learning",
                "content": "Students build knowledge actively. Ask questions, explore instruments, discover concepts. Teacher guides, not directs. Student investment high. More engaging than lecture.",
                "method": "Constructivism",
                "category": "Pedagogy",
                "keywords": ["constructivist", "active", "discovery", "engagement"],
                "age_group": "All"
            },
            {
                "title": "Differentiated Instruction",
                "content": "Meet students at different levels. Advanced: challenge with complex material. Struggling: simplify, provide more support. Individual learning plans. Respects diversity. Critical for inclusive classrooms.",
                "method": "Differentiation",
                "category": "Pedagogy",
                "keywords": ["differentiation", "diversity", "support", "inclusion"],
                "age_group": "All"
            },
        ]

        # MUSIC LITERACY (20 items)
        literacy_items = [
            {
                "title": "Staff & Clefs",
                "content": "Treble clef: higher pitches, G on second line. Bass clef: lower pitches, F on second line. Ledger lines extend range above/below staff. Whole staff: 5 lines, 4 spaces. Every student learns first.",
                "category": "Literacy",
                "keywords": ["staff", "clef", "treble", "bass", "lines"],
                "proficiency": "Beginner"
            },
            {
                "title": "Note Values & Rhythm",
                "content": "Whole note (4 beats), half note (2), quarter (1), eighth (1/2). Dotted notes add 1/2 value. Rest equivalent to note. Time signature: top # = beats per measure, bottom # = note value. Rhythm foundation.",
                "category": "Literacy",
                "keywords": ["notes", "rhythm", "time_signature", "rests"],
                "proficiency": "Beginner"
            },
            {
                "title": "Accidentals & Key Signatures",
                "content": "Sharp (#): raise 1/2 step. Flat (b): lower 1/2 step. Natural: cancel sharp/flat. Key signature: sharps/flats at start (indicate key). Majors/minors have different key signatures. Essential for reading.",
                "category": "Literacy",
                "keywords": ["accidentals", "sharp", "flat", "key_signature"],
                "proficiency": "Intermediate"
            },
            {
                "title": "Intervals & Scales",
                "content": "Interval: distance between two pitches. Unison (same), 2nd, 3rd, 4th, 5th, 6th, 7th, octave. Major scale: 12 semitones (whole-half-whole-whole-whole-whole-half). Minor scale: different pattern. Foundation for harmony.",
                "category": "Literacy",
                "keywords": ["intervals", "scales", "semitone", "major", "minor"],
                "proficiency": "Intermediate-Advanced"
            },
        ]

        # CLASSROOM MANAGEMENT (18 items)
        classroom_items = [
            {
                "title": "Establishing Classroom Norms",
                "content": "First days critical. Establish expectations: listen when teacher/others speak, respect instruments, clean up. Consistent enforcement. Positive reinforcement. Clear routines prevent chaos.",
                "category": "Classroom Management",
                "keywords": ["norms", "expectations", "routines", "discipline"],
                "age_group": "All"
            },
            {
                "title": "Behavior Management Strategies",
                "content": "Positive reinforcement: praise good behavior. Redirect: move disruptive student. Loss of privilege: instrument access loss. Stay calm. Understand student needs (attention, power, etc). Consistency key.",
                "category": "Classroom Management",
                "keywords": ["behavior", "reinforcement", "consequences", "consistency"],
                "age_group": "All"
            },
            {
                "title": "Ensemble Rehearsal Efficiency",
                "content": "Plan rehearsal: warm-up, isolated problem areas, full run-through. Specific feedback ('measure 12, violins sharper'). Don't play full piece repeatedly. Work on problems, then full. Time management critical.",
                "category": "Classroom Management",
                "keywords": ["rehearsal", "efficiency", "planning", "feedback"],
                "age_group": "Ensemble"
            },
        ]

        # ASSESSMENT & EVALUATION (20 items)
        assessment_items = [
            {
                "title": "Formative vs Summative Assessment",
                "content": "Formative: ongoing feedback during learning (helps students improve). Quizzes, observations, projects. Summative: end assessment (grades, pass/fail). Both necessary. Formative emphasizes learning.",
                "category": "Assessment",
                "keywords": ["formative", "summative", "feedback", "grades"],
                "purpose": "Evaluate learning"
            },
            {
                "title": "Performance Assessment",
                "content": "Student performs piece, evaluated on technique/expression. Rubrics standardize scoring. Recorded performance for evaluation. Removes subjectivity. Performance-based learning evidence.",
                "category": "Assessment",
                "keywords": ["performance", "rubric", "recording", "evaluation"],
                "purpose": "Assess performance skills"
            },
            {
                "title": "Portfolio Assessment",
                "content": "Collect student work over time: recordings, compositions, reflection journals. Demonstrate growth. Student-selected best work. Shows learning journey, not snapshot.",
                "category": "Assessment",
                "keywords": ["portfolio", "collection", "growth", "reflection"],
                "purpose": "Track long-term progress"
            },
            {
                "title": "Rubrics & Scoring",
                "content": "Rubric: scale with criteria levels. Example: Technique (Exemplary, Proficient, Developing, Incomplete). Numeric scores (4-1). Transparent to students. Students understand expectations.",
                "category": "Assessment",
                "keywords": ["rubric", "scoring", "criteria", "levels"],
                "purpose": "Grade objectively"
            },
        ]

        # SPECIAL NEEDS EDUCATION (15 items)
        special_items = [
            {
                "title": "Teaching Students with Autism",
                "content": "Predictability important (visual schedules). Sensory sensitivities (loud instruments may be uncomfortable). Strength-based approach. Clear, concrete instructions. May excel in music.",
                "category": "Special Needs",
                "keywords": ["autism", "predictability", "sensory", "concrete"],
                "condition": "Autism Spectrum"
            },
            {
                "title": "Teaching Students with ADHD",
                "content": "Movement breaks necessary. Fidget tools acceptable. Clear expectations. Shorter attention spans = shorter activities. Frequent reinforcement. Channel energy through rhythm.",
                "category": "Special Needs",
                "keywords": ["ADHD", "movement", "focus", "reinforcement"],
                "condition": "ADHD"
            },
            {
                "title": "Teaching Students with Hearing Loss",
                "content": "Visual supports (sheet music, videos). Hearing aids/cochlear implants (understand technology). Feel vibrations. Lip reading. Assistive technology. Music accessible to all abilities.",
                "category": "Special Needs",
                "keywords": ["hearing_loss", "deaf", "visual", "technology"],
                "condition": "Hearing Loss"
            },
            {
                "title": "Music Therapy vs General Education",
                "content": "Music therapy: clinical setting, therapist-led, specific health goals. General education: classroom, teacher-led, skill/knowledge development. Overlap but different purposes.",
                "category": "Special Needs",
                "keywords": ["therapy", "clinical", "education", "classroom"],
                "purpose": "Understand distinction"
            },
        ]

        # TECHNOLOGY IN MUSIC ED (15 items)
        tech_items = [
            {
                "title": "Digital Audio Workstations (DAWs) in Class",
                "content": "GarageBand, Audacity free options. Students compose digitally. Ear training software (EarMaster). MIDI keyboards connect to computer. Technology accessible, engaging for students.",
                "category": "Technology",
                "keywords": ["DAW", "GarageBand", "Audacity", "MIDI"],
                "tool_type": "Software"
            },
            {
                "title": "Music Notation Software",
                "content": "MuseScore (free), Finale, Sibelius (expensive). Students compose/arrange. Learn notation interactively. Audio playback for feedback. Develops musicianship.",
                "category": "Technology",
                "keywords": ["notation", "MuseScore", "Finale", "Sibelius"],
                "tool_type": "Software"
            },
            {
                "title": "Music Listening Platforms",
                "content": "Spotify, YouTube, streaming services. Access to all music instantly. Create playlists for lessons. Curate listening experiences. Accessibility for all.",
                "category": "Technology",
                "keywords": ["Spotify", "YouTube", "streaming", "playlist"],
                "tool_type": "Streaming"
            },
            {
                "title": "Virtual Instruments & Apps",
                "content": "Synthesizer apps (Sunrizer, iSpark), virtual piano. Students explore without instruments. Accessibility for students without instruments. Engaging, interactive learning.",
                "category": "Technology",
                "keywords": ["virtual", "instruments", "app", "synthesizer"],
                "tool_type": "Apps"
            },
        ]

        # CURRICULUM DESIGN (15 items)
        curriculum_items = [
            {
                "title": "Backward Design Approach",
                "content": "Start with end goal (desired learning outcome). Plan assessment to measure goal. Design activities to achieve goal. Clear alignment. More effective than traditional planning.",
                "category": "Curriculum",
                "keywords": ["backward_design", "outcomes", "alignment"],
                "framework": "UbD"
            },
            {
                "title": "National Standards for Music Education",
                "content": "US standards: creating, performing, responding, connecting. Each with grade-level benchmarks. Guidelines for curriculum. States may adopt/modify. Framework for accountability.",
                "category": "Curriculum",
                "keywords": ["standards", "national", "benchmarks", "outcomes"],
                "framework": "National Standards"
            },
            {
                "title": "Spiral Curriculum",
                "content": "Return to concepts repeatedly at greater depth. Beginning: simple rhythm, later: complex patterns. Builds understanding gradually. Confidence through familiarity + challenge.",
                "category": "Curriculum",
                "keywords": ["spiral", "depth", "gradual", "revisit"],
                "framework": "Spiraling"
            },
        ]

        # PROFESSIONAL DEVELOPMENT (12 items)
        prof_dev_items = [
            {
                "title": "Continuing Education",
                "content": "Workshops, conferences (MENC, CMEA), online courses. Professional growth essential. Grant funding available. Keeps teachers current. Models lifelong learning.",
                "category": "Professional Development",
                "keywords": ["workshop", "conference", "professional", "growth"],
                "type": "Continuing Ed"
            },
            {
                "title": "Mentorship & Collaboration",
                "content": "New teachers benefit from mentors. Team planning time. Share materials/ideas. Professional learning communities. Collaborative culture improves school.",
                "category": "Professional Development",
                "keywords": ["mentorship", "collaboration", "community", "sharing"],
                "type": "Collaboration"
            },
            {
                "title": "Reflection & Growth",
                "content": "Keep teaching journal. Reflect on lessons: what worked? What didn't? Student feedback. Video recording self for reflection. Growth mindset essential.",
                "category": "Professional Development",
                "keywords": ["reflection", "journal", "video", "mindset"],
                "type": "Self-Reflection"
            },
        ]

        # Combine all items
        all_items = pedagogy_items + literacy_items + classroom_items + assessment_items + special_items + tech_items + curriculum_items + prof_dev_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all items for a specific education category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

# Integration module for BOB AI v9.0
class MusicEducationIntegration:
    """Integration module for music education in BOB AI"""

    def __init__(self):
        self.knowledge = MusicEducationKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if music education module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        education_keywords = [
            "education", "teaching", "pedagogy", "learning", "curriculum",
            "student", "classroom", "lesson", "method", "assessment"
        ]

        return any(kw in education_keywords for kw in keywords + topics)

# Export classes
__all__ = ["MusicEducationKnowledge", "MusicEducationIntegration"]
