"""BOB AI v10.0 - Tier 11: Social & Behavioral Sciences (35 disciplines)"""
from backend.bob_ai_expansion_200_disciplines import Tier11SocialBehavioral

class SocialBehavioralKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier11SocialBehavioral.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Social and behavioral expertise"})
            total_keywords.update(keywords)
        return {"tier": 11, "discipline": "Social & Behavioral Sciences", "category": "Tier 11: Integration - Social & Behavioral", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Psychology, Sociology, Anthropology, Communication.", "description": "35 social science disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return SocialBehavioralKnowledge().get_knowledge_base()

__all__ = ["SocialBehavioralKnowledge", "get_knowledge_base"]
