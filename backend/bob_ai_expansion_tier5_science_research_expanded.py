"""BOB AI v10.0 - Tier 5: Science & Research (41 disciplines)"""
from backend.bob_ai_expansion_200_disciplines import Tier5ScienceResearch

class ScienceResearchKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier5ScienceResearch.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Scientific knowledge and research"})
            total_keywords.update(keywords)
        return {"tier": 5, "discipline": "Science & Research", "category": "Tier 5: Core - Science & Research", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Physics, Chemistry, Biology, Geology, Materials Science, Research Methodology.", "description": "41 scientific disciplines covering all sciences.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return ScienceResearchKnowledge().get_knowledge_base()

__all__ = ["ScienceResearchKnowledge", "get_knowledge_base"]
