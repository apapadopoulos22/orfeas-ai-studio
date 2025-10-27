"""BOB AI v10.0 - Tier 8: Arts & Humanities (40 disciplines)"""
from backend.bob_ai_expansion_200_disciplines import Tier8ArtsHumanities

class ArtsHumanitiesKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier8ArtsHumanities.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Humanities and cultural expertise"})
            total_keywords.update(keywords)
        return {"tier": 8, "discipline": "Arts & Humanities", "category": "Tier 8: Advanced - Arts & Humanities", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Literature, History, Anthropology, Religious Studies.", "description": "40 humanities disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return ArtsHumanitiesKnowledge().get_knowledge_base()

__all__ = ["ArtsHumanitiesKnowledge", "get_knowledge_base"]
