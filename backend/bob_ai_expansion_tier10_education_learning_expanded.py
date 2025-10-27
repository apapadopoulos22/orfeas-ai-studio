"""BOB AI v10.0 - Tier 10: Education & Learning (30 disciplines)"""
from backend.bob_ai_expansion_200_disciplines import Tier10EducationLearning

class EducationLearningKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier10EducationLearning.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Education and learning expertise"})
            total_keywords.update(keywords)
        return {"tier": 10, "discipline": "Education & Learning", "category": "Tier 10: Integration - Education & Learning", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Pedagogy, Learning Theory, Curriculum Design, Assessment.", "description": "30 education disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return EducationLearningKnowledge().get_knowledge_base()

__all__ = ["EducationLearningKnowledge", "get_knowledge_base"]
