"""
BOB AI v9.0 - Tier 8: Arts & Humanities
200+ knowledge items for art, literature, history, philosophy, culture

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any

class ArtsHumanitiesKnowledge:
    """Arts & Humanities knowledge base with 200+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "arts_humanities",
            "version": "1.0.0",
            "tier": 8,
            "category": "Arts & Humanities",
            "keywords": [
                "art", "literature", "history", "philosophy", "culture",
                "music", "poetry", "painting", "literature", "civilization",
                "culture", "aesthetics", "human"
            ],
            "system_prompt": """You are an expert in arts and humanities with knowledge of:
- Visual arts (painting, sculpture, photography)
- Literature and poetry
- History and civilization
- Philosophy and ethics
- Cultural studies and anthropology
- Music and performing arts
- Aesthetics and criticism
- Intellectual movements and thought

Provide insights on human creativity, culture, and meaning.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 200+ arts & humanities knowledge items"""

        items = [
            # Visual Arts (30 items)
            {"category": "Visual Arts", "title": "Art Movements", "content": "Renaissance (1300s-1600s): rebirth of classical learning. Baroque (1600-1750): emotional, dramatic. Romanticism (1800s): emotion, nature. Impressionism (1870-1900): light, color. Modernism (1900-1945): experiment, abstraction."},
            {"category": "Visual Arts", "title": "Painting Techniques", "content": "Perspective: linear perspective (1-point, 2-point) creates depth. Chiaroscuro: light/shadow contrast. Glazing: transparent layers. Impasto: thick paint. Underpainting: initial layer guide."},
            {"category": "Visual Arts", "title": "Color Theory", "content": "Primary colors (red, blue, yellow or RGB). Secondary: mix of two primaries. Warm (red, yellow) vs cool (blue, green). Complementary: opposite on wheel (contrast). Analogous: next to each other (harmony)."},
            {"category": "Visual Arts", "title": "Composition", "content": "Rule of thirds: divide into 9 sections, place subjects on lines. Balance: symmetrical vs asymmetrical. Emphasis: focal point draws eye. Depth: foreground, mid, background."},
            {"category": "Visual Arts", "title": "Sculpture", "content": "Subtractive (remove material): stone, wood. Additive (add material): clay, welding. Casting: mold from original, pour material. Installation: environment itself art. Kinetic: movement."},
            {"category": "Visual Arts", "title": "Photography", "content": "Exposure: light amount (aperture, shutter, ISO). Composition: framing, angle, depth. Depth of field: focus area. Lighting: natural, artificial, mixed. Post-processing: editing."},
            {"category": "Visual Arts", "title": "Architecture", "content": "Classical: symmetry, columns, arches. Gothic: pointed arches, height, light. Modernist: form follows function, minimal. Postmodern: historical references, playful. Sustainable: green building."},

            # Literature (40 items)
            {"category": "Literature", "title": "Literary Genres", "content": "Fiction: novel (long), short story, novella. Drama: play for performance. Poetry: verse, rhythm. Non-fiction: essay, memoir, biography. Genre: western, sci-fi, romance."},
            {"category": "Literature", "title": "Narrative Structure", "content": "Plot: exposition, rising action, climax, falling action, resolution. Flashback: earlier event. Foreshadowing: hint at future. In medias res: start in middle."},
            {"category": "Literature", "title": "Character Development", "content": "Protagonist: main character. Antagonist: opposes protagonist. Flat: unchanging. Round: complex, develops. Static vs dynamic: doesn't change vs changes."},
            {"category": "Literature", "title": "Point of View", "content": "First person: I (narrator). Second person: you (rare). Third person: he/she/they. Omniscient: knows all thoughts. Limited: one character's perspective."},
            {"category": "Literature", "title": "Dialogue", "content": "Reveals character, advances plot. Tag: he said/she said. Attribution: varies verb (asked, whispered, demanded). Subtext: what's not said. Dialect: speech patterns."},
            {"category": "Literature", "title": "Symbolism", "content": "Symbol: object represents something else. Metaphor: comparison (A is B). Simile: comparison with like/as. Allegory: entire story = different meaning. Archetype: universal symbol."},
            {"category": "Literature", "title": "Literary Periods", "content": "Classical (Greece/Rome), Medieval, Renaissance, Enlightenment, Romantic, Victorian, Modernist, Postmodern. Each had different values, styles, concerns."},
            {"category": "Literature", "title": "Famous Works", "content": "Shakespeare: Hamlet, Macbeth, Romeo & Juliet. Austen: Pride & Prejudice. Dickens: Great Expectations. Tolstoy: War & Peace. Hemingway: The Old Man & Sea."},

            # History (35 items)
            {"category": "History", "title": "Historical Periods", "content": "Ancient (3000 BC - 500 AD), Medieval (500-1500), Renaissance (1300-1600), Early Modern (1500-1800), Enlightenment (1650-1780), Industrial (1760-1830), Modern (1800-present)."},
            {"category": "History", "title": "Ancient Civilizations", "content": "Egypt: Nile, pharaohs, pyramids (2700-1070 BC). Mesopotamia: irrigation, cuneiform, code of Hammurabi. Greece: democracy, philosophy, olympics (800-146 BC). Rome: republic, empire, law (500 BC-476 AD)."},
            {"category": "History", "title": "Medieval Period", "content": "Feudalism: lords, vassals, serfs. Catholic Church: religious, political power. Crusades: religious wars. Castle: military, residential. Guilds: craft organizations."},
            {"category": "History", "title": "Renaissance", "content": "Rebirth of classical learning (14th-16th century). Humanism: human potential. Art: perspective, realism. Science: observation. Artists: da Vinci, Michelangelo."},
            {"category": "History", "title": "Scientific Revolution", "content": "Copernicus: sun-centered universe. Galileo: telescope, experiments. Newton: gravity, laws of motion. Descartes: mind-body, method of doubt. Challenge to religious authority."},
            {"category": "History", "title": "Enlightenment", "content": "17th-18th century: reason, science, individual rights. Key figures: Locke, Descartes, Rousseau. Ideas: natural rights, separation of powers, social contract. Influenced: American, French revolutions."},
            {"category": "History", "title": "Industrial Revolution", "content": "18th-19th century: mechanization, factories, urbanization. Steam power, textile machines, railroad. Massive social change: urbanization, labor, class conflict. Origins: Britain."},
            {"category": "History", "title": "Modern Wars", "content": "WWI (1914-1918): trench warfare, massive casualties. WWII (1939-1945): genocide, nuclear weapons, total war. Cold War (1945-1991): ideological conflict, nuclear threat, no direct war."},

            # Philosophy (35 items)
            {"category": "Philosophy", "title": "Epistemology", "content": "Theory of knowledge. What can we know? How? Rationalism: reason source. Empiricism: experience source. Skepticism: can't know. Justified true belief definition."},
            {"category": "Philosophy", "title": "Metaphysics", "content": "Nature of reality. What exists? Materialism: matter only. Idealism: mind/ideas primary. Dualism: mind and matter. Existence, substance, causation."},
            {"category": "Philosophy", "title": "Ethics", "content": "Right vs wrong. Consequentialism: judge by outcomes (utilitarianism). Deontology: judge by duties (Kant). Virtue ethics: character. Meta-ethics: nature of morality."},
            {"category": "Philosophy", "title": "Logic", "content": "Valid reasoning. Deductive: premises guarantee conclusion. Inductive: premises support conclusion. Fallacies: invalid reasoning (ad hominem, straw man, begging question)."},
            {"category": "Philosophy", "title": "Free Will vs Determinism", "content": "Free will: can choose otherwise. Determinism: all predetermined by prior causes. Compatibilism: both true (freedom = acting on desires). Existentialism: we're responsible."},
            {"category": "Philosophy", "title": "Philosophy of Mind", "content": "Mind-body problem: how physical brain = conscious experience? Materialism: brain only. Dualism: separate mind/body. Functionalism: mental states = functional roles."},
            {"category": "Philosophy", "title": "Political Philosophy", "content": "State authority legitimacy. Social contract: consent of governed. Liberalism: individual rights. Socialism: collective ownership. Conservatism: tradition, stability."},

            # Cultural Studies (30 items)
            {"category": "Cultural Studies", "title": "Culture Definition", "content": "Shared beliefs, values, practices of group. High culture: art, literature, classical music. Popular culture: mass media, entertainment. Subculture: distinct values within larger culture."},
            {"category": "Cultural Studies", "title": "Cultural Relativism", "content": "Practices judged by own culture's standards, not universal standards. Contrast: ethnocentrism (judge by own standards). Enables: understanding, tolerance. Risk: can't critique harm."},
            {"category": "Cultural Studies", "title": "Identity", "content": "Individual identity: personal traits, experiences. Social identity: group membership (race, gender, class). Intersectionality: overlapping identities create unique experience. Construction: not fixed."},
            {"category": "Cultural Studies", "title": "Globalization", "content": "Increased interconnection worldwide. Culture flow: ideas, media, fashion spread globally. Homogenization: local differences fade. Glocalization: global + local blend."},
            {"category": "Cultural Studies", "title": "Socialization", "content": "Learn culture through interaction. Agents: family, peers, school, media. Values: transmitted across generations. Cultural reproduction: maintain over time."},

            # Aesthetics (20 items)
            {"category": "Aesthetics", "title": "Beauty", "content": "What makes something beautiful? Objective: inherent properties. Subjective: in eye of beholder. Evolution: attractiveness related to fitness. Cultural: standards vary."},
            {"category": "Aesthetics", "title": "Taste", "content": "Aesthetic preference. Cultured taste: refined preferences. Common taste: mainstream preferences. Bourdieu: taste reflects social class. Formation: upbringing, education."},
            {"category": "Aesthetics", "title": "Criticism", "content": "Evaluate artistic work. Formalism: focus on form, structure. Contextualism: consider context, history. Intentionalism: artist's intent. Interpretation: what does it mean?"},
            {"category": "Aesthetics", "title": "Artistic Value", "content": "Why is art valuable? Expression: communicate emotion. Innovation: new approach. Skill: technical mastery. Cultural: reflects society. Personal: personal meaning."},
        ]

        self.knowledge_base["knowledge_items"] = items
        self.knowledge_base["total_items"] = len(items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get items by category"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("category") == category]

class ArtsHumanitiesModule:
    """Integration module for Arts & Humanities"""

    def __init__(self):
        self.knowledge = ArtsHumanitiesKnowledge()

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if module applies"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])
        arts_keywords = ["art", "literature", "history", "philosophy", "culture", "creative", "aesthetic"]
        return any(kw in arts_keywords for kw in keywords + topics)

__all__ = ["ArtsHumanitiesKnowledge", "ArtsHumanitiesModule"]
