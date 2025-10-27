"""
BOB AI v8.0 - Base Infrastructure

Master class structure and foundation for all v8.0 knowledge modules.
Provides unified interface for v8.0 discipline enhancement across all 13 domains.

Version: 8.0
Status: Foundation Layer
Dependencies: v1-v7 (backward compatible)
"""

import logging
from typing import Dict, List, Tuple, Optional, Any
from abc import ABC, abstractmethod
import json
from datetime import datetime

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class BobAIV8BaseKnowledge(ABC):
    """
    Abstract base class for all BOB AI v8.0 knowledge modules.

    Each discipline (Cinematography, Python, etc.) inherits from this class
    and implements discipline-specific knowledge dictionaries and enhancement logic.
    """

    def __init__(self, discipline_name: str, version: str = "8.0"):
        """Initialize base knowledge module.

        Args:
            discipline_name: Name of the discipline (e.g., 'Cinematography')
            version: Module version (default 8.0)
        """
        self.discipline_name = discipline_name
        self.version = version
        self.knowledge_items: Dict[str, Any] = {}
        self.keywords: List[str] = []
        self.categories: Dict[str, List[str]] = {}
        self.metadata = {
            'created': datetime.now().isoformat(),
            'discipline': discipline_name,
            'version': version,
            'status': 'active'
        }

    @abstractmethod
    def get_knowledge_dictionaries(self) -> Dict[str, Dict]:
        """Return all knowledge dictionaries for this discipline.

        Returns:
            Dictionary mapping category names to knowledge items
        """
        pass

    @abstractmethod
    def get_keywords(self) -> List[str]:
        """Return all keywords that trigger this discipline.

        Returns:
            List of keywords for domain detection
        """
        pass

    @abstractmethod
    def enhance_prompt(self, prompt: str) -> str:
        """Enhance a prompt with discipline-specific knowledge.

        Args:
            prompt: Input prompt to enhance

        Returns:
            Enhanced prompt with discipline-specific context
        """
        pass

    def generate_system_prompt(self) -> str:
        """Generate a system prompt incorporating this discipline's expertise.

        Returns:
            System prompt string
        """
        return f"""You are an expert in {self.discipline_name}.
        Apply deep knowledge of {self.discipline_name} principles, best practices,
        and techniques to provide expert-level guidance and enhancement."""

    def get_enhancement_context(self) -> Dict[str, Any]:
        """Get structured context for LLM enhancement.

        Returns:
            Dictionary with discipline context, keywords, categories
        """
        return {
            'discipline': self.discipline_name,
            'version': self.version,
            'keywords': self.get_keywords(),
            'categories': list(self.categories.keys()),
            'item_count': len(self.knowledge_items),
            'system_prompt': self.generate_system_prompt(),
            'metadata': self.metadata
        }

    def validate_knowledge(self) -> Tuple[bool, List[str]]:
        """Validate knowledge module completeness.

        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []

        # Check required components
        if not self.get_keywords():
            errors.append(f"No keywords defined for {self.discipline_name}")

        if not self.get_knowledge_dictionaries():
            errors.append(f"No knowledge dictionaries for {self.discipline_name}")

        if len(self.get_keywords()) < 5:
            errors.append(f"Insufficient keywords (<5) for {self.discipline_name}")

        dicts = self.get_knowledge_dictionaries()
        if dicts and len(dicts) < 3:
            errors.append(f"Insufficient categories (<3) for {self.discipline_name}")

        return len(errors) == 0, errors

    def to_dict(self) -> Dict[str, Any]:
        """Serialize module to dictionary.

        Returns:
            Dictionary representation of module
        """
        return {
            'discipline': self.discipline_name,
            'version': self.version,
            'keywords': self.get_keywords(),
            'categories': list(self.get_knowledge_dictionaries().keys()),
            'knowledge_items': len(self.knowledge_items),
            'metadata': self.metadata
        }


class BobAIV8IntegrationBase(ABC):
    """
    Base class for v8.0 discipline integration with LLM pipeline.

    Handles:
    - Auto-detection of discipline from prompts
    - Prompt enhancement with discipline knowledge
    - System prompt generation
    - Context retrieval for LLM
    """

    def __init__(self, knowledge_module: BobAIV8BaseKnowledge):
        """Initialize integration module.

        Args:
            knowledge_module: Instance of BobAIV8BaseKnowledge subclass
        """
        self.knowledge = knowledge_module
        self.discipline_name = knowledge_module.discipline_name
        self.keywords = knowledge_module.get_keywords()

    def should_apply_to_prompt(self, prompt: str) -> Tuple[bool, float]:
        """Determine if this discipline should enhance the prompt.

        Args:
            prompt: Input prompt to analyze

        Returns:
            Tuple of (should_apply, confidence_score)
        """
        prompt_lower = prompt.lower()
        keyword_matches = sum(1 for kw in self.keywords if kw.lower() in prompt_lower)

        if keyword_matches == 0:
            return False, 0.0

        # Confidence increases with more keyword matches
        confidence = min(1.0, keyword_matches / len(self.keywords))
        return True, confidence

    def enhance(self, prompt: str) -> str:
        """Enhance prompt with discipline knowledge.

        Args:
            prompt: Input prompt

        Returns:
            Enhanced prompt
        """
        should_apply, confidence = self.should_apply_to_prompt(prompt)

        if not should_apply:
            return prompt

        # Use discipline-specific enhancement
        return self.knowledge.enhance_prompt(prompt)

    @abstractmethod
    def get_discipline_specific_context(self, prompt: str) -> Dict[str, Any]:
        """Get discipline-specific context for enhancement.

        Args:
            prompt: Input prompt

        Returns:
            Dictionary with discipline-specific context
        """
        pass

    def generate_enhancement_context(self, prompt: str) -> Dict[str, Any]:
        """Generate complete enhancement context.

        Args:
            prompt: Input prompt

        Returns:
            Dictionary with all enhancement context
        """
        return {
            'discipline': self.discipline_name,
            'confidence': self.should_apply_to_prompt(prompt)[1],
            'system_prompt': self.knowledge.generate_system_prompt(),
            'keywords_matched': [kw for kw in self.keywords if kw.lower() in prompt.lower()],
            'discipline_context': self.get_discipline_specific_context(prompt),
            'keywords': self.keywords,
            'categories': list(self.knowledge.get_knowledge_dictionaries().keys())
        }


class BobAIV8MasterManager:
    """
    Master manager for all BOB AI v8.0 modules.

    Orchestrates:
    - Module loading and initialization
    - Discipline detection and routing
    - Enhancement pipeline coordination
    - Performance monitoring
    - Cross-domain linking
    """

    def __init__(self):
        """Initialize master manager."""
        self.modules: Dict[str, BobAIV8BaseKnowledge] = {}
        self.integrations: Dict[str, BobAIV8IntegrationBase] = {}
        self.keywords_to_discipline: Dict[str, str] = {}
        self.performance_metrics = {
            'total_enhancements': 0,
            'average_time_ms': 0,
            'domains_detected': {}
        }

    def register_module(self,
                       discipline_name: str,
                       knowledge: BobAIV8BaseKnowledge,
                       integration: BobAIV8IntegrationBase):
        """Register a v8.0 discipline module.

        Args:
            discipline_name: Name of discipline
            knowledge: Knowledge module instance
            integration: Integration module instance
        """
        self.modules[discipline_name] = knowledge
        self.integrations[discipline_name] = integration

        # Build keyword map
        for keyword in knowledge.get_keywords():
            self.keywords_to_discipline[keyword.lower()] = discipline_name

        logger.info(f"Registered v8.0 module: {discipline_name}")

    def detect_disciplines(self, prompt: str) -> List[Tuple[str, float]]:
        """Detect which disciplines apply to prompt.

        Args:
            prompt: Input prompt

        Returns:
            List of (discipline_name, confidence) tuples sorted by confidence
        """
        results = []

        for discipline, integration in self.integrations.items():
            should_apply, confidence = integration.should_apply_to_prompt(prompt)
            if should_apply and confidence > 0.1:
                results.append((discipline, confidence))

        # Sort by confidence descending
        return sorted(results, key=lambda x: x[1], reverse=True)

    def enhance_prompt_multi_domain(self, prompt: str) -> Tuple[str, Dict[str, Any]]:
        """Enhance prompt using all applicable disciplines.

        Args:
            prompt: Input prompt

        Returns:
            Tuple of (enhanced_prompt, metadata)
        """
        detected = self.detect_disciplines(prompt)
        metadata = {
            'disciplines_applied': [],
            'confidences': {},
            'contexts': {}
        }

        enhanced = prompt

        for discipline, confidence in detected:
            if confidence > 0.3:  # Only apply if confidence > 30%
                integration = self.integrations[discipline]
                enhanced = integration.enhance(enhanced)

                metadata['disciplines_applied'].append(discipline)
                metadata['confidences'][discipline] = confidence
                metadata['contexts'][discipline] = integration.generate_enhancement_context(prompt)

        self.performance_metrics['total_enhancements'] += 1

        return enhanced, metadata

    def get_master_system_prompt(self) -> str:
        """Get master system prompt incorporating all active disciplines.

        Returns:
            Master system prompt
        """
        disciplines = ", ".join(self.modules.keys())
        return f"""You are an expert assistant with deep knowledge across {len(self.modules)} specialized disciplines:
        {disciplines}

        Apply relevant expertise from these domains to provide comprehensive, high-quality assistance.
        Consider cross-domain connections and synthesis opportunities."""

    def get_status_report(self) -> Dict[str, Any]:
        """Get comprehensive status report.

        Returns:
            Dictionary with complete system status
        """
        return {
            'version': '8.0',
            'modules_registered': len(self.modules),
            'disciplines': list(self.modules.keys()),
            'total_keywords': len(self.keywords_to_discipline),
            'total_enhancements': self.performance_metrics['total_enhancements'],
            'module_details': {
                name: module.to_dict()
                for name, module in self.modules.items()
            }
        }


# Global instance (singleton pattern)
_master_manager: Optional[BobAIV8MasterManager] = None


def get_bob_ai_v8_manager() -> BobAIV8MasterManager:
    """Get or create the master BOB AI v8.0 manager.

    Returns:
        Global BobAIV8MasterManager instance
    """
    global _master_manager
    if _master_manager is None:
        _master_manager = BobAIV8MasterManager()
        logger.info("Initialized BOB AI v8.0 Master Manager")
    return _master_manager


if __name__ == "__main__":
    # Test basic initialization
    print("BOB AI v8.0 Base Infrastructure Initialized")
    manager = get_bob_ai_v8_manager()
    print(f"Manager status: {manager.get_status_report()}")
