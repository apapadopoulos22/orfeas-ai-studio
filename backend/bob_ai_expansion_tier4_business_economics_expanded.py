"""BOB AI v10.0 - Tier 4: Business & Economics (35+ disciplines)"""
from bob_ai_expansion_200_disciplines import Tier4BusinessEconomics

class BusinessEconomicsKnowledge:
    def get_knowledge_base(self) -> dict:
        disciplines = Tier4BusinessEconomics.DISCIPLINES
        knowledge_items = []
        total_keywords = set()
        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)
            knowledge_items.append({
                "discipline": discipline_name,
                "keywords": keywords,
                "knowledge_items": items_count,
                "description": f"{discipline_name} - Business and economic expertise"
            })
            total_keywords.update(keywords)
        return {
            "tier": 4,
            "discipline": "Business & Economics",
            "category": "Tier 4: Core - Business & Economic Knowledge",
            "knowledge_items": knowledge_items,
            "total_items": len(disciplines),
            "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()),
            "keywords": list(total_keywords),
            "system_prompt": "Expert in Business, Economics, Finance, Management, Marketing, Operations. Provide strategic business guidance.",
            "description": "35+ disciplines covering economics, finance, business management, marketing, operations, entrepreneurship, HR, strategy.",
            "disciplines_list": list(disciplines.keys()),
        }

def get_knowledge_base() -> dict:
    return BusinessEconomicsKnowledge().get_knowledge_base()

__all__ = ["BusinessEconomicsKnowledge", "get_knowledge_base"]
