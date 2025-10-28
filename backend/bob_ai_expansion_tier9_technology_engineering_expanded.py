"""BOB AI v10.0 - Tier 9: Technology & Engineering (40 disciplines)"""
from bob_ai_expansion_200_disciplines import Tier9TechnologyEngineering

class TechnologyEngineeringKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier9TechnologyEngineering.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Technology and engineering expertise"})
            total_keywords.update(keywords)
        return {"tier": 9, "discipline": "Technology & Engineering", "category": "Tier 9: Advanced - Technology & Engineering", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Software, AI/ML, Cloud, Cybersecurity, Hardware, Robotics.", "description": "40 technology disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return TechnologyEngineeringKnowledge().get_knowledge_base()

__all__ = ["TechnologyEngineeringKnowledge", "get_knowledge_base"]
