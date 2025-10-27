"""
BOB AI v10.0 - Tier 2: Philosophy & Theoretical Frameworks
===========================================================

Wrapper module for Philosophy & Theoretical Frameworks tier containing 25+ disciplines.
Implements get_knowledge_base() for integration with DisciplineModuleMapper.

Disciplines:
- Epistemology, Metaphysics, Ontology (fundamental philosophy)
- Logic & Reasoning (formal logic, reasoning systems)
- Phenomenology, Existentialism, Stoicism (philosophical movements)
- Ethics Systems (Utilitarianism, Virtue Ethics, Deontology)
- Aesthetics & Semiotics (philosophy of art and meaning)
- Systems & Complexity Theory (emergent systems)
- Game & Decision Theory (strategic thinking)

Version: 10.0.0
Tier: 2
Discipline Count: 25
Knowledge Items: ~3,000+
Created: October 28, 2025
"""

from backend.bob_ai_expansion_200_disciplines import Tier2PhilosophyTheory


class PhilosophyTheoryKnowledge:
    """Knowledge base for Tier 2: Philosophy & Theoretical Frameworks"""

    def get_knowledge_base(self) -> dict:
        """
        Returns organized knowledge base for Philosophy & Theory tier.

        Returns:
            dict: Complete knowledge base structure with disciplines and metadata
        """
        disciplines = Tier2PhilosophyTheory.DISCIPLINES

        knowledge_items = []
        total_keywords = set()

        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)

            knowledge_items.append({
                "discipline": discipline_name,
                "keywords": keywords,
                "knowledge_items": items_count,
                "description": f"{discipline_name} - Theoretical framework and philosophical foundations"
            })

            total_keywords.update(keywords)

        knowledge_base = {
            "tier": 2,
            "discipline": "Philosophy & Theoretical Frameworks",
            "category": "Tier 2: Foundation - Philosophical & Theoretical Knowledge",
            "knowledge_items": knowledge_items,
            "total_items": len(disciplines),
            "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()),
            "keywords": list(total_keywords),
            "system_prompt": (
                "You are an expert in Philosophy and Theoretical Frameworks including "
                "epistemology, metaphysics, logic, phenomenology, existentialism, ethics systems, "
                "aesthetics, semiotics, systems theory, game theory, and decision theory. "
                "Provide deep philosophical analysis, theoretical rigor, and foundational understanding."
            ),
            "description": (
                "Tier 2 encompasses fundamental philosophical and theoretical frameworks. "
                "Covers epistemology (theory of knowledge), metaphysics (nature of reality), "
                "logic and reasoning, phenomenology and existentialism, ethics systems, "
                "aesthetics and semiotics, systems and complexity theory, game theory, "
                "and decision-making frameworks. Total of 25 theoretical disciplines "
                "with deep conceptual foundations."
            ),
            "disciplines_list": list(disciplines.keys()),
        }

        return knowledge_base


def get_knowledge_base() -> dict:
    """Factory function to get knowledge base without instantiation"""
    knowledge = PhilosophyTheoryKnowledge()
    return knowledge.get_knowledge_base()


__all__ = ["PhilosophyTheoryKnowledge", "get_knowledge_base"]
