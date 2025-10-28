"""BOB AI v10.0 - Tier 7: Law & Governance (30 disciplines)"""
from bob_ai_expansion_200_disciplines import Tier7LawGovernance

class LawGovernanceKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier7LawGovernance.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({"discipline": discipline_name, "keywords": keywords, "knowledge_items": items_count, "description": f"{discipline_name} - Legal and governance expertise"})
            total_keywords.update(keywords)
        return {"tier": 7, "discipline": "Law & Governance", "category": "Tier 7: Advanced - Law & Governance", "knowledge_items": knowledge_items, "total_items": len(disciplines), "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()), "keywords": list(total_keywords), "system_prompt": "Expert in Constitutional Law, Corporate Law, International Law, Policy.", "description": "30 legal and governance disciplines.", "disciplines_list": list(disciplines.keys())}

def get_knowledge_base() -> dict:
    return LawGovernanceKnowledge().get_knowledge_base()

__all__ = ["LawGovernanceKnowledge", "get_knowledge_base"]
