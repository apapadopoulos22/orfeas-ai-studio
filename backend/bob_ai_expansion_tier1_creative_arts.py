"""
BOB AI v10.0 - Tier 1: Creative Arts & Performance
===================================================

Wrapper module for Creative Arts tier containing 25+ disciplines.
Implements get_knowledge_base() for integration with DisciplineModuleMapper.

Disciplines:
- Music (Composition, Theory, History, Performance, Production)
- Visual Arts (Painting, Drawing, Digital Art)
- Cinematography & Film (Directing, Screenwriting, Cinematography)
- Theater & Performance (Drama, Dance, Acting)
- Design (Graphic, Web, Product, Animation, 3D Modeling)

Version: 10.0.0
Tier: 1
Discipline Count: 25
Knowledge Items: ~3,100+
Created: October 28, 2025
"""

from bob_ai_expansion_200_disciplines import Tier1CreativeArts


class CreativeArtsKnowledge:
    """Knowledge base for Tier 1: Creative Arts & Performance"""

    def get_knowledge_base(self) -> dict:
        """
        Returns organized knowledge base for Creative Arts tier.

        Returns:
            dict: Complete knowledge base structure with:
                - discipline: Name of tier
                - category: Tier classification
                - knowledge_items: List of disciplines with metadata
                - total_items: Count of unique disciplines
                - keywords: Relevant tags
                - system_prompt: System instruction for agents
        """
        disciplines = Tier1CreativeArts.DISCIPLINES

        # Extract all knowledge items from disciplines
        knowledge_items = []
        total_keywords = set()

        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)

            knowledge_items.append({
                "discipline": discipline_name,
                "keywords": keywords,
                "knowledge_items": items_count,
                "description": f"{discipline_name} - Professional knowledge and expertise"
            })

            total_keywords.update(keywords)

        knowledge_base = {
            "tier": 1,
            "discipline": "Creative Arts & Performance",
            "category": "Tier 1: Foundation - Creative & Artistic Knowledge",
            "knowledge_items": knowledge_items,
            "total_items": len(disciplines),
            "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()),
            "keywords": list(total_keywords),
            "system_prompt": (
                "You are an expert in Creative Arts and Performance disciplines including "
                "music composition, theory, performance, visual arts, photography, cinematography, "
                "theater, dance, and design. Provide comprehensive, creative, and technically "
                "accurate guidance on artistic expression, technical skills, and creative processes."
            ),
            "description": (
                "Tier 1 encompasses foundational creative and artistic disciplines. "
                "This knowledge base covers music (composition, theory, history, performance, production), "
                "visual arts (painting, sculpture, drawing, digital art), photography, cinematography, "
                "theater, dance, choreography, and various design disciplines (graphic, web, product, 3D modeling). "
                "Total of 25 distinct creative disciplines with 100-150 knowledge items each."
            ),
            "disciplines_list": list(disciplines.keys()),
        }

        return knowledge_base


def get_knowledge_base() -> dict:
    """Factory function to get knowledge base without instantiation"""
    knowledge = CreativeArtsKnowledge()
    return knowledge.get_knowledge_base()


# Export for module discovery
__all__ = ["CreativeArtsKnowledge", "get_knowledge_base"]
