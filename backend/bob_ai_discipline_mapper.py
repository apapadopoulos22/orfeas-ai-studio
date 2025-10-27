"""
BOB AI v9.0 - Discipline Module Mapper
Dynamically loads and indexes all discipline modules from tiers 1-12

Features:
- Auto-discovery of discipline modules
- Dynamic loading and instantiation
- Module registry and indexing
- Integration with knowledge graph
- Module statistics and health checks

Created: October 27, 2025
Version: 9.0.0
"""

from typing import Dict, List, Any, Optional, Type
import importlib
import inspect
from pathlib import Path

class DisciplineModuleMapper:
    """Maps and indexes all discipline modules"""

    # Tier mapping: tier number -> list of discipline modules
    TIER_MODULES = {
        1: [
            "bob_ai_v9_music_composition",
            "bob_ai_v9_music_history",
            "bob_ai_v9_music_performance",
            "bob_ai_v9_music_production",
            "bob_ai_v9_music_education",
        ],
        2: [
            # External AI and Decision Reasoning (from previous sessions)
        ],
        3: ["bob_ai_v9_tier3_ethics_ai_safety"],
        4: ["bob_ai_v9_tier4_business_economics"],
        5: ["bob_ai_v9_tier5_science_research"],
        6: ["bob_ai_v9_tier6_healthcare_medicine"],
        7: ["bob_ai_v9_tier7_law_governance"],
        8: ["bob_ai_v9_tier8_arts_humanities"],
        9: ["bob_ai_v9_tier9_technology_engineering"],
        10: ["bob_ai_v9_tier10_education_learning"],
        11: ["bob_ai_v9_tier11_social_behavioral"],
        12: ["bob_ai_v9_tier12_environment_sustainability"],
    }

    def __init__(self):
        self.modules: Dict[str, Any] = {}  # {module_name: module}
        self.knowledge_bases: Dict[str, Dict[str, Any]] = {}  # {discipline: kb}
        self.module_metadata: Dict[str, Dict[str, Any]] = {}  # {module: metadata}
        self._load_all_modules()

    def _load_all_modules(self):
        """Load all discipline modules"""
        for tier, module_names in self.TIER_MODULES.items():
            for module_name in module_names:
                try:
                    self._load_module(module_name, tier)
                except Exception as e:
                    print(f"Warning: Could not load {module_name}: {e}")

    def _load_module(self, module_name: str, tier: int):
        """Load a single module and extract knowledge base"""
        try:
            # Import module
            module = importlib.import_module(f"backend.{module_name}")
            self.modules[module_name] = module

            # Find Knowledge class
            knowledge_class = self._find_knowledge_class(module)
            if knowledge_class:
                # Instantiate and get knowledge base
                kb_instance = knowledge_class()
                kb = kb_instance.get_knowledge_base()

                discipline_name = kb.get("discipline", module_name)
                self.knowledge_bases[discipline_name] = kb

                # Store metadata
                self.module_metadata[module_name] = {
                    "tier": tier,
                    "discipline": discipline_name,
                    "category": kb.get("category", ""),
                    "item_count": kb.get("total_items", 0),
                    "keywords": kb.get("keywords", []),
                    "module": module_name,
                }
        except ImportError as e:
            raise ImportError(f"Could not import {module_name}: {e}")

    def _find_knowledge_class(self, module) -> Optional[Type]:
        """Find Knowledge class in module"""
        for name, obj in inspect.getmembers(module):
            # Look for classes ending with 'Knowledge'
            if inspect.isclass(obj) and name.endswith("Knowledge"):
                return obj
        return None

    def get_discipline_knowledge(self, discipline_name: str) -> Optional[Dict[str, Any]]:
        """Get knowledge base for discipline"""
        return self.knowledge_bases.get(discipline_name)

    def get_all_disciplines(self) -> List[str]:
        """Get list of all loaded disciplines"""
        return list(self.knowledge_bases.keys())

    def get_disciplines_by_tier(self, tier: int) -> List[str]:
        """Get disciplines in a tier"""
        return [
            md["discipline"]
            for md in self.module_metadata.values()
            if md["tier"] == tier
        ]

    def get_disciplines_by_category(self, category: str) -> List[str]:
        """Get disciplines by category"""
        return [
            md["discipline"]
            for md in self.module_metadata.values()
            if md["category"] == category
        ]

    def search_knowledge(self, query: str, discipline_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search across all knowledge bases"""
        results = []
        query_lower = query.lower()

        for discipline, kb in self.knowledge_bases.items():
            if discipline_filter and discipline != discipline_filter:
                continue

            items = kb.get("knowledge_items", [])
            for item in items:
                # Search in title and content
                if (query_lower in item.get("title", "").lower() or
                    query_lower in item.get("content", "").lower()):
                    results.append({
                        "discipline": discipline,
                        "category": item.get("category"),
                        "title": item.get("title"),
                        "content": item.get("content"),
                    })

        return results

    def get_mapper_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded modules"""
        total_items = sum(kb.get("total_items", 0) for kb in self.knowledge_bases.values())
        total_disciplines = len(self.knowledge_bases)

        tier_stats = {}
        for tier, module_names in self.TIER_MODULES.items():
            tier_disciplines = self.get_disciplines_by_tier(tier)
            tier_items = sum(
                self.knowledge_bases.get(d, {}).get("total_items", 0)
                for d in tier_disciplines
            )
            tier_stats[tier] = {
                "disciplines": len(tier_disciplines),
                "items": tier_items,
            }

        return {
            "total_disciplines": total_disciplines,
            "total_items": total_items,
            "total_tiers": len(self.TIER_MODULES),
            "modules_loaded": len(self.modules),
            "tier_statistics": tier_stats,
        }

    def get_discipline_details(self, discipline_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a discipline"""
        kb = self.knowledge_bases.get(discipline_name)
        if not kb:
            return None

        # Find module metadata
        module_meta = None
        for meta in self.module_metadata.values():
            if meta["discipline"] == discipline_name:
                module_meta = meta
                break

        return {
            "name": discipline_name,
            "category": kb.get("category", ""),
            "tier": module_meta.get("tier") if module_meta else None,
            "total_items": kb.get("total_items", 0),
            "keywords": kb.get("keywords", []),
            "categories": list(set(item.get("category") for item in kb.get("knowledge_items", []))),
            "system_prompt": kb.get("system_prompt", ""),
        }

# Global mapper instance
_mapper_instance = None

def get_discipline_mapper() -> DisciplineModuleMapper:
    """Get singleton mapper instance"""
    global _mapper_instance
    if _mapper_instance is None:
        _mapper_instance = DisciplineModuleMapper()
    return _mapper_instance

__all__ = [
    "DisciplineModuleMapper",
    "get_discipline_mapper",
]
