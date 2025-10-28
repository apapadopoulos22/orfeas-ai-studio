"""BOB AI v10.0 - Tier 6: Healthcare & Medicine (35 disciplines)"""
from bob_ai_expansion_200_disciplines import Tier6HealthcareMedicine

class HealthcareMedicineKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier6HealthcareMedicine.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Healthcare and medical expertise"})
            total_keywords.update(keywords)
        return {"tier": 6, "discipline": "Healthcare & Medicine", "category": "Tier 6: Core - Healthcare & Medicine", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Medicine, Surgery, Psychiatry, Pharmacology, Public Health.", "description": "35 healthcare disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return HealthcareMedicineKnowledge().get_knowledge_base()

__all__ = ["HealthcareMedicineKnowledge", "get_knowledge_base"]
