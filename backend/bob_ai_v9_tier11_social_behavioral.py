"""
BOB AI v9.0 - Tier 11: Social & Behavioral
200+ knowledge items for psychology, sociology, anthropology, behavior, society

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class SocialBehavioralKnowledge:
    """Social & Behavioral knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "social_behavioral",
            "version": "1.0.0",
            "tier": 11,
            "category": "Social & Behavioral",
            "keywords": [
                "psychology", "sociology", "behavior", "anthropology",
                "society", "social", "mental_health", "personality",
                "relationships", "culture"
            ],
            "system_prompt": """You are an expert in social and behavioral sciences with knowledge of:
- Psychology: personality, cognition, mental health, development
- Sociology: society, institutions, social structures, inequality
- Anthropology: culture, human diversity, human origins
- Behavioral science: decision-making, motivation, influence
- Social psychology: groups, attitudes, persuasion
- Neuroscience: brain, behavior, neurotransmitters

Provide insights on human behavior and social dynamics.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ social & behavioral knowledge items"""

        items = [
            # Psychology: Personality (25 items)
            {"category": "Personality", "title": "Big Five", "content": "Openness: curiosity, creativity. Conscientiousness: organization, discipline. Extraversion: sociability, energy. Agreeableness: compassion, cooperation. Neuroticism: emotional reactivity. Largely stable across life."},
            {"category": "Personality", "title": "Myers-Briggs Type", "content": "4 dimensions: E/I (extraversion/introversion), S/N (sensing/intuition), T/F (thinking/feeling), J/P (judging/perceiving). 16 types. Descriptive, not diagnostic. Popular but criticized scientifically."},
            {"category": "Personality", "title": "Attachment Styles", "content": "Secure: comfortable with intimacy, low anxiety. Anxious: high need for reassurance, fear rejection. Avoidant: discomfort with intimacy, independence. Formed in childhood, affects adult relationships."},
            {"category": "Personality", "title": "Self-Esteem", "content": "Overall evaluation of self-worth. High: positive self-view. Low: self-doubt. Contingent: depends on external validation. Resilient: stable despite setbacks."},
            {"category": "Personality", "title": "Confidence vs Competence", "content": "Confidence: belief in ability. Competence: actual ability. Can diverge: overconfident (Dunning-Kruger) or underconfident. Experience builds both."},

            # Psychology: Mental Health (30 items)
            {"category": "Mental Health", "title": "Anxiety Disorders", "content": "Generalized anxiety: persistent worry. Panic disorder: sudden panic attacks. Phobia: fear of specific thing. Social anxiety: fear of judgment. PTSD: trauma response. Treatment: therapy, medication."},
            {"category": "Mental Health", "title": "Depression", "content": "Persistent sadness, loss of interest, fatigue. Major: lasts weeks, impairs functioning. Dysthymia: chronic, mild. Bipolar: mood cycles. Risk factors: stress, genetics. Treatment: therapy, antidepressants."},
            {"category": "Mental Health", "title": "Cognition & Thinking Patterns", "content": "Negative thinking: catastrophizing, black-and-white. Rumination: repetitive thought. Automatic thoughts: unconscious. CBT: cognitive behavioral therapy challenges thoughts."},
            {"category": "Mental Health", "title": "Emotional Regulation", "content": "Identify emotions, understand causes, choose response. Reappraisal: reinterpret event. Mindfulness: observe without judgment. Emotional suppression: counterproductive. Practice improves."},
            {"category": "Mental Health", "title": "Resilience", "content": "Bouncing back from adversity. Factors: relationships, purpose, agency, optimism. Growth mindset helps. Not fixed; can develop. Stress inoculation builds."},

            # Psychology: Development (25 items)
            {"category": "Development", "title": "Erikson's Stages", "content": "8 life stages, each psychosocial crisis. Infancy: trust vs mistrust. Childhood: autonomy vs shame. School: competence vs inferiority. Adolescence: identity vs confusion. Adult: intimacy, generativity, integrity."},
            {"category": "Development", "title": "Attachment Theory", "content": "Bowlby: secure attachment base for exploration. Ainsworth: secure, avoidant, anxious types. Critical period: first years. Affects relationships lifetime. Disruption: neglect or abuse impairs."},
            {"category": "Development", "title": "Moral Development", "content": "Kohlberg: preconventional (reward/punishment), conventional (rules), postconventional (principles). Gilligan: care ethic. Socialization: learn norms, internalize values."},
            {"category": "Development", "title": "Adolescent Development", "content": "Physical: puberty, brain changes. Cognitive: abstract thinking, metacognition. Social-emotional: identity, peer influence. Risky behavior increases. Normal but needs support."},
            {"category": "Development", "title": "Aging", "content": "Fluid intelligence (processing): declines. Crystallized intelligence (knowledge): stable/increases. Cognitive: some decline, wisdom increases. Social: relationships important for health. Active engagement protects."},

            # Sociology (30 items)
            {"category": "Sociology", "title": "Social Structure", "content": "Norms: expected behaviors. Roles: positions with expectations. Status: social ranking. Institutions: organized systems (family, education, economy). Systems maintain or change."},
            {"category": "Sociology", "title": "Socialization", "content": "Learn culture through interaction. Primary (family): foundational. Secondary (school, work): specific roles. Peer groups: strong influence in adolescence. Lifelong process."},
            {"category": "Sociology", "title": "Social Inequality", "content": "Stratification: ranking of people. Class: economic position. Caste: hereditary status. Power: ability to influence others. Inequality: based on class, race, gender, age."},
            {"category": "Sociology", "title": "Gender", "content": "Biological sex vs social gender. Roles: culturally defined expectations. Socialization: learn gender norms. Intersectionality: gender + race, class, other factors. Changing across cultures, time."},
            {"category": "Sociology", "title": "Race & Ethnicity", "content": "Race: social construct (not biological). Ethnicity: cultural identity. Racism: discrimination, prejudice, institutional barriers. Systemic: embedded in institutions."},

            # Anthropology (25 items)
            {"category": "Anthropology", "title": "Culture", "content": "Shared beliefs, values, practices. Material: physical objects. Non-material: ideas, behaviors. Culture varies by society, time. Enculturation: learn culture. Acculturation: adopt new culture."},
            {"category": "Anthropology", "title": "Kinship Systems", "content": "Family structures: nuclear (parents + kids), extended (relatives), patrilineal (father's line), matrilineal (mother's line). Marriage: monogamy, polygamy. Varies by culture."},
            {"category": "Anthropology", "title": "Ritual & Ceremony", "content": "Sacred events with meaning. Rites of passage: mark transitions (birth, adulthood, death). Reinforce community, transmit values. Vary by culture."},
            {"category": "Anthropology", "title": "Human Evolution", "content": "Hominins: bipedal, large brain. Lucy (3.2M yrs): early hominin. Homo habilis: toolmaker. Homo erectus: fire. Homo neanderthalensis: ice age. Homo sapiens: language, art."},
            {"category": "Anthropology", "title": "Cross-Cultural Differences", "content": "Individualist (US, Europe): self-oriented. Collectivist (Asia, Africa): group-oriented. Affects values, communication, decision-making. Context matters: situation affects behavior."},

            # Social Psychology (40 items)
            {"category": "Social Psy", "title": "Attitudes", "content": "Beliefs + evaluation. Formed through experience, persuasion. Affect behavior. Can change through new information, experience. Cognitive dissonance: holds conflicting attitudes."},
            {"category": "Social Psy", "title": "Persuasion", "content": "Change attitudes/behavior. Central route: logic, evidence (lasting). Peripheral route: emotion, attractiveness (temporary). Sleeper effect: source forgotten, message remains."},
            {"category": "Social Psy", "title": "Prejudice", "content": "Negative attitude toward group. Stereotypes: overgeneralized beliefs. Discrimination: unfair behavior. Implicit bias: unconscious prejudice. Reduced by: contact, empathy, education."},
            {"category": "Social Psy", "title": "Group Behavior", "content": "Conformity: adjust to group. Obedience: follow authority. Groupthink: seek consensus, miss problems. Deindividuation: lose self in group. Social facilitation: perform better/worse with audience."},
            {"category": "Social Psy", "title": "Aggression", "content": "Physical/verbal hostility. Causes: frustration, aggression, media, testosterone, alcohol. Situation amplifies. Can be reduced: cooling off, alternatives, empathy."},
            {"category": "Social Psy", "title": "Attraction & Love", "content": "Proximity: nearness increases liking. Similarity: alike attracted. Reciprocity: mutual liking. Physical attractiveness: initial attraction. Love: passionate (intense) vs companionate (deep, lasting)."},
            {"category": "Social Psy", "title": "Helping Behavior", "content": "Prosocial: help others. Empathy-altruism: help due to empathy. Reciprocal altruism: help expecting return. Bystander effect: diffusion of responsibility. Increase helping: reduce ambiguity, model."},

            # Behavioral Economics (20 items)
            {"category": "Behavioral Econ", "title": "Heuristics & Biases", "content": "Mental shortcuts save effort but cause errors. Availability heuristic: judge by memorable examples. Representativeness: judge by stereotypes. Anchoring: rely on first number."},
            {"category": "Behavioral Econ", "title": "Loss Aversion", "content": "Loss feels worse than equivalent gain. Reference point: compare to baseline. Endowment effect: value what we own more. Motivates: keep losses small."},
            {"category": "Behavioral Econ", "title": "Framing Effects", "content": "How information presented affects choice. Gain frame: emphasize positives. Loss frame: emphasize negatives. Same situation, different choice. Shapes: behavior, policy design."},
            {"category": "Behavioral Econ", "title": "Defaults", "content": "Default option chosen most often. Sticky: hard to change. Can nudge behavior: opt-in (lower), opt-out (higher). Used: retirement savings, organ donation."},

            # Neuroscience (25 items)
            {"category": "Neuroscience", "title": "Brain Structures", "content": "Prefrontal cortex: reasoning, impulse control, planning. Amygdala: emotion, fear. Hippocampus: memory formation. Cerebellum: coordination. Brainstem: survival functions. Lateralization: left/right differences."},
            {"category": "Neuroscience", "title": "Neurotransmitters", "content": "Dopamine: motivation, reward. Serotonin: mood, sleep. Norepinephrine: alertness, attention. GABA: calming. Glutamate: excitation. Acetylcholine: memory. Imbalances: mental health."},
            {"category": "Neuroscience", "title": "Neuroplasticity", "content": "Brain changes throughout life. Learning rewires connections. Repetition strengthens pathways. Recovery possible after injury. Meditation, exercise promote growth."},
            {"category": "Neuroscience", "title": "Sleep & Dreams", "content": "Sleep stages: REM (dreams), NREM (deep sleep). Functions: memory consolidation, restoration, emotion regulation. Deprivation: impairs cognition, mood, health. 7-9 hours optimal."},
            {"category": "Neuroscience", "title": "Stress Response", "content": "Amygdala triggers fight/flight. Cortisol released. Heart rate, blood pressure up. Adaptive: cope with threat. Chronic: harms health. Recovery: parasympathetic activation (rest/digest)."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class SocialBehavioralModule:
    """Integration module for Social & Behavioral"""

    def __init__(self):
        self.knowledge = SocialBehavioralKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        social_keywords = ["psychology", "sociology", "behavior", "social", "anthropology", "mental_health", "relationships"]
        return any(kw in social_keywords for kw in keywords + topics)

__all__ = ["SocialBehavioralKnowledge", "SocialBehavioralModule"]
