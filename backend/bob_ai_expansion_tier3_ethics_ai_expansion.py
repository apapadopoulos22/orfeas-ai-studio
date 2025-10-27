"""
BOB AI v10.0 - Tier 3: Ethics, AI Safety & Governance
======================================================

Wrapper module for Ethics, AI Safety & Governance tier containing 30+ disciplines.
Implements get_knowledge_base() for integration with DisciplineModuleMapper.

Disciplines:
- AI Ethics (fairness, transparency, accountability)
- AI Safety & Alignment (safety, robustness, verification)
- AI Governance (regulation, policy, oversight)
- Data Ethics (privacy, consent, security)
- Bioethics & Medical Ethics (autonomy, beneficence)
- Environmental & Applied Ethics
- Human Rights & Social Justice

Version: 10.0.0
Tier: 3
Discipline Count: 30
Knowledge Items: ~3,800+
Created: October 28, 2025
"""

from backend.bob_ai_expansion_200_disciplines import Tier3EthicsAI


class EthicsAIKnowledge:
    """Knowledge base for Tier 3: Ethics, AI Safety & Governance"""

    def get_knowledge_base(self) -> dict:
        """Returns organized knowledge base for Ethics & AI tier"""
        disciplines = Tier3EthicsAI.DISCIPLINES

        knowledge_items = []
        total_keywords = set()

        for discipline_name, discipline_data in disciplines.items():
            keywords = discipline_data.get("keywords", [])
            items_count = discipline_data.get("items", 0)

            knowledge_items.append({
                "discipline": discipline_name,
                "keywords": keywords,
                "knowledge_items": items_count,
                "description": f"{discipline_name} - Ethical frameworks and responsible AI principles"
            })

            total_keywords.update(keywords)

        knowledge_base = {
            "tier": 3,
            "discipline": "Ethics, AI Safety & Governance",
            "category": "Tier 3: Foundation - Ethical & Governance Knowledge",
            "knowledge_items": knowledge_items,
            "total_items": len(disciplines),
            "total_knowledge_count": sum(d.get("items", 0) for d in disciplines.values()),
            "keywords": list(total_keywords),
            "system_prompt": (
                "You are an expert in AI Ethics, Safety, and Governance. Provide guidance on "
                "AI fairness, transparency, accountability, safety alignment, data ethics, "
                "bioethics, human rights, and responsible AI principles. Ensure ethical considerations "
                "in all recommendations and decisions."
            ),
            "description": (
                "Tier 3 focuses on Ethics, AI Safety, and Governance. Covers AI ethics (fairness, transparency, accountability), "
                "AI safety and alignment, AI governance and regulation, data ethics and privacy, "
                "bioethics and medical ethics, environmental ethics, human rights, and applied ethical frameworks. "
                "30 ethical and governance disciplines with comprehensive coverage of responsible AI principles."
            ),
            "disciplines_list": list(disciplines.keys()),
        }

        return knowledge_base


def get_knowledge_base() -> dict:
    """Factory function to get knowledge base without instantiation"""
    knowledge = EthicsAIKnowledge()
    return knowledge.get_knowledge_base()


__all__ = ["EthicsAIKnowledge", "get_knowledge_base"]
