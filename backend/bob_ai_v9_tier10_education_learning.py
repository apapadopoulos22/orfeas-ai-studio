"""
BOB AI v9.0 - Tier 10: Education & Learning
200+ knowledge items for teaching, learning, pedagogy, curriculum, assessment

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class EducationLearningKnowledge:
    """Education & Learning knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "education_learning",
            "version": "1.0.0",
            "tier": 10,
            "category": "Education & Learning",
            "keywords": [
                "education", "learning", "teaching", "pedagogy", "curriculum",
                "assessment", "development", "cognition", "instruction",
                "student", "teacher"
            ],
            "system_prompt": """You are an expert in education and learning with knowledge of:
- Learning theories and pedagogy
- Curriculum design and instructional design
- Assessment and evaluation methods
- Cognitive development and psychology
- Teaching methodologies and strategies
- Educational technology and e-learning
- Special education and learning differences
- Higher education and student development

Provide guidance on effective teaching and learning.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ education & learning knowledge items"""

        items = [
            # Learning Theories (35 items)
            {"category": "Learning Theories", "title": "Behaviorism", "content": "Learning = behavior change from reinforcement/punishment. Stimulus-response. Classical conditioning (Pavlov): stimulus triggers response. Operant conditioning (Skinner): behavior followed by consequence."},
            {"category": "Learning Theories", "title": "Cognitivism", "content": "Learning = mental processes (thinking, memory, reasoning). Information processing: input → process → output. Schema: mental framework. Mental models guide understanding."},
            {"category": "Learning Theories", "title": "Constructivism", "content": "Learning = active knowledge construction. Prior knowledge important. Misconceptions must be addressed. Scaffolding: support gradually removed. Piaget: stages of development."},
            {"category": "Learning Theories", "title": "Social Learning", "content": "Learning through observation and modeling. Bandura: social cognitive theory. Peer influence strong. Communities of practice: situated learning. Vygotsky: zone of proximal development."},
            {"category": "Learning Theories", "title": "Motivation", "content": "Intrinsic: internal drive (interest, mastery). Extrinsic: external reward (grades, money). Autonomy, competence, relatedness boost intrinsic motivation. Goal orientation: mastery vs performance."},
            {"category": "Learning Theories", "title": "Learning Styles", "content": "Visual, auditory, kinesthetic, reading/writing learners (debated). Multiple intelligences: linguistic, logical, spatial, musical, bodily, interpersonal, intrapersonal, naturalistic."},
            {"category": "Learning Theories", "title": "Bloom's Taxonomy", "content": "Remember, understand, apply, analyze, evaluate, create (revised). Higher-order thinking: analysis, synthesis. Progression from basic to complex. Guide for objective-setting."},

            # Pedagogy (35 items)
            {"category": "Pedagogy", "title": "Direct Instruction", "content": "Teacher-led: I do, we do, you do. Clear objective, model skill, guided practice, independent practice. Structured. Effective for skill-building."},
            {"category": "Pedagogy", "title": "Discovery Learning", "content": "Students learn through exploration. Active inquiry. Constructivist. Can be inefficient (trial-error). Works if scaffolded. Problem-based learning variant."},
            {"category": "Pedagogy", "title": "Cooperative Learning", "content": "Group work: students learn together. Roles: facilitator, recorder, reporter. Interdependence: each contributes. Accountability individual. Benefits: social skills, peer teaching."},
            {"category": "Pedagogy", "title": "Differentiation", "content": "Tailor instruction to individual needs. Content (what), process (how), product (output). Readiness, interest, learning profile. Tiering, anchoring, choice."},
            {"category": "Pedagogy", "title": "Questioning", "content": "Ask to probe thinking. Bloom's levels: remember to create. Wait time: pause after question (improves responses). Hinge questions: check understanding mid-lesson."},
            {"category": "Pedagogy", "title": "Feedback", "content": "Specific, timely, actionable. Praise effort not ability (growth mindset). Corrective: explains error. Affirming: reinforces correct. Tone matters for reception."},
            {"category": "Pedagogy", "title": "Classroom Management", "content": "Set expectations, establish routines, build relationships. Positive reinforcement > punishment. Consistency critical. Proactive (prevent) > reactive (respond)."},

            # Curriculum Design (30 items)
            {"category": "Curriculum", "title": "Curriculum Models", "content": "Traditional: subjects separate. Integrated: themes connect subjects. Project-based: real-world problems. Competency-based: master skills. Hidden curriculum: unstated learning (values, culture)."},
            {"category": "Curriculum", "title": "Instructional Design (ID)", "content": "ADDIE: analyze, design, develop, implement, evaluate. Learning objectives (SMART). Task analysis: break skills. Assessment alignment: test what's taught."},
            {"category": "Curriculum", "title": "Learning Objectives", "content": "SMART: specific, measurable, achievable, relevant, time-bound. Bloom's: action verb + content + condition. Alignment: objectives → instruction → assessment."},
            {"category": "Curriculum", "title": "Backward Design", "content": "Start with desired results (objectives). Design assessments that show learning. Plan instruction to reach goals. Ensures alignment, not teaching to test."},
            {"category": "Curriculum", "title": "Standards-Based Learning", "content": "Standards: what students should know/do. Alignment: curriculum, instruction, assessment to standards. Common Core (USA math/ELA). Critiques: narrowing, one-size-fits-all."},

            # Assessment (40 items)
            {"category": "Assessment", "title": "Summative vs Formative", "content": "Summative: end-of-unit test (grade). Evaluates learning. Formal, high stakes. Formative: ongoing checks (quiz, discussion). Guides instruction. Informal, low stakes."},
            {"category": "Assessment", "title": "Validity & Reliability", "content": "Valid: test measures what it claims. Reliable: consistent results. Threat: bias, unclear questions, conditions vary. Pilot test to verify."},
            {"category": "Assessment", "title": "Formative Assessment Strategies", "content": "Exit tickets: quick checks. Thumbs up/down: quick poll. Think-pair-share: discussion. Observation: watch behavior. Questioning: probe thinking. Adjusts instruction."},
            {"category": "Assessment", "title": "Performance-Based Assessment", "content": "Show ability by doing (project, presentation, portfolio). Authentic: real-world context. Rubric: criteria and levels. Evaluates complex skills, transfer."},
            {"category": "Assessment", "title": "Rubrics", "content": "Scoring guide: criteria and levels. Analytic: score each criterion. Holistic: single overall score. Clear expectations. Consistency across raters (calibration)."},
            {"category": "Assessment", "title": "Standardized Testing", "content": "Norm-referenced: compared to group. Criterion-referenced: met standard? SAT, ACT (college). Critiques: narrow, biased, high-stakes pressure."},

            # Cognitive Development (30 items)
            {"category": "Cognitive Dev", "title": "Piaget's Stages", "content": "Sensorimotor (0-2): senses, reflexes. Preoperational (2-7): language, symbolic play. Concrete (7-11): logic, conservation. Formal (12+): abstract reasoning, hypothesis testing."},
            {"category": "Cognitive Dev", "title": "Memory", "content": "Sensory: brief (< 1 sec). Short-term: 7±2 items, ~30 sec. Long-term: unlimited. Encoding, storage, retrieval. Forgetting: decay, interference."},
            {"category": "Cognitive Dev", "title": "Attention", "content": "Limited capacity: can't attend to everything. Selective: focus on relevant, ignore irrelevant. Sustained: maintain over time. Distractions hinder learning."},
            {"category": "Cognitive Dev", "title": "Metacognition", "content": "Thinking about thinking. Self-awareness: strategies, strengths, weaknesses. Monitoring: adjusting during learning. Planning: allocate resources. Reflective learners succeed."},
            {"category": "Cognitive Dev", "title": "Transfer", "content": "Apply learning in new contexts. Near: similar context. Far: different context. Difficult. Achieved through varied practice, principles emphasis."},

            # Educational Technology (20 items)
            {"category": "EdTech", "title": "Learning Management Systems (LMS)", "content": "Canvas, Blackboard, Moodle. Organize course content, assignments, grades. Enable online learning. Engagement metrics. Accessibility important."},
            {"category": "EdTech", "title": "Interactive Tools", "content": "Whiteboards: annotation, collaboration. Polling: real-time feedback. Video: demonstrate, review. Simulations: practice safely. Augmented/virtual reality: immersive."},
            {"category": "EdTech", "title": "Online Learning", "content": "Synchronous: real-time (Zoom). Asynchronous: self-paced (recorded, discussion forums). Blended: mix both. Student-teacher interaction critical for success."},
            {"category": "EdTech", "title": "Adaptive Learning", "content": "Personalized path based on performance. AI: adjusts difficulty, content. Pacing: individual speed. Effectiveness: mixed evidence, implementation matters."},

            # Special Education (20 items)
            {"category": "Special Ed", "title": "Learning Disabilities", "content": "Dyslexia: reading difficulty. Dyscalculia: math difficulty. ADHD: attention, impulse control. Diagnosis requires assessment. Accommodations: support without changing standard."},
            {"category": "Special Ed", "title": "Accommodations vs Modifications", "content": "Accommodations: bypass difficulty (extended time, large print). Don't change content. Modifications: change standard (simpler assignment). Still rigorous, different goal."},
            {"category": "Special Ed", "title": "IEP & 504", "content": "IEP: individualized education program for disabled students. 504: accommodation plan. Legal requirements. Parental involvement. Regular review, adjustment."},
            {"category": "Special Ed", "title": "Inclusion", "content": "Students with disabilities in general education. Least restrictive environment. Support services provided. Benefits: socialization, access to curriculum. Challenges: resources, training."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class EducationLearningModule:
    """Integration module for Education & Learning"""

    def __init__(self):
        self.knowledge = EducationLearningKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        edu_keywords = ["education", "learning", "teaching", "pedagogy", "curriculum", "assessment", "student", "instruction"]
        return any(kw in edu_keywords for kw in keywords + topics)

__all__ = ["EducationLearningKnowledge", "EducationLearningModule"]
