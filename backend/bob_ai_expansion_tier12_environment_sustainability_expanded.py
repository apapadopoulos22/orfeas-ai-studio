"""BOB AI v10.0 - Tier 12: Environment & Sustainability (25 disciplines)"""
from backend.bob_ai_expansion_200_disciplines import Tier12EnvironmentSustainability

class EnvironmentSustainabilityKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier12EnvironmentSustainability.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Environmental and sustainability expertise"})
            total_keywords.update(keywords)
        return {"tier": 12, "discipline": "Environment & Sustainability", "category": "Tier 12: Integration - Environment & Sustainability", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Climate Science, Renewable Energy, Conservation, Green Building.", "description": "25 sustainability disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return EnvironmentSustainabilityKnowledge().get_knowledge_base()

__all__ = ["EnvironmentSustainabilityKnowledge", "get_knowledge_base"]
