"""
Bob AI Games and Concepts Knowledge Integration v4.0
=====================================================

Integration and enhancement pipeline for games, abstract concepts, and advanced knowledge.

This module connects all games and concepts knowledge modules to the LLM pipeline
for automatic prompt enhancement across 9 major knowledge domains.

Author: Bob AI Development Team
Date: October 26, 2025
Version: 4.0
"""

import logging
from typing import Dict, List, Tuple

from bob_ai_games_and_concepts_knowledge import GamesCombinedIntegration

logger = logging.getLogger(__name__)


class GamesAndConceptsEnhancer:
    """Enhances prompts with games and concepts knowledge"""

    DOMAIN_KEYWORDS = {
        "abstract_concepts": ["play", "game design", "player", "engagement", "strategy", "tactics",
                            "game theory", "rules", "objectives", "mechanics", "challenge"],
        "figurines": ["miniature", "figurine", "tabletop", "painting", "model", "scale", "base",
                     "warhammer", "necromunda", "detailed", "hand-painted"],
        "board_games": ["board game", "boardgame", "dice", "cards", "tokens", "worker placement",
                       "auction", "tile placement", "victory points", "resource", "turn structure"],
        "video_games": ["video game", "game engine", "fps", "rpg", "mmorpg", "strategy game",
                       "unity", "unreal", "gameplay", "level design", "character design"],
        "dungeons_dragons": ["d&d", "dungeons and dragons", "dnd", "class", "character sheet",
                            "spell", "combat", "monster", "quest", "campaign", "adventure"],
        "algebra": ["algebra", "equation", "polynomial", "function", "variable", "factor", "solve",
                   "quadratic", "exponential", "logarithm", "slope", "graph"],
        "chemistry": ["chemistry", "element", "atom", "molecule", "reaction", "periodic table",
                     "compound", "bonding", "acid", "base", "ph", "oxidation"],
        "encyclopedia": ["encyclopedia", "knowledge", "information", "history", "geography",
                        "culture", "science", "reference", "comprehensive", "classification"],
        "game_literature": ["rulebook", "rules", "game manual", "literature", "fantasy", "sci-fi",
                           "universe", "lore", "setting", "world-building"]
    }

    @staticmethod
    def detect_knowledge_domain(prompt: str) -> List[str]:
        """Detect which knowledge domains are relevant to the prompt"""
        prompt_lower = prompt.lower()
        detected_domains = []

        for domain, keywords in GamesAndConceptsEnhancer.DOMAIN_KEYWORDS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_domains.append(domain)

        return detected_domains if detected_domains else []

    @staticmethod
    def enhance_with_abstract_concepts(prompt: str) -> str:
        """Enhance prompt with abstract concepts knowledge"""
        enhancements = [
            "with game design principles (balance, pacing, accessibility, depth)",
            "with player engagement strategies (motivation, flow state, retention)",
            "with strategic concepts (tactics, probability, resource management)",
            "with game mechanics optimization (rules clarity, challenge balance)"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_figurines(prompt: str) -> str:
        """Enhance prompt with figurines knowledge"""
        enhancements = [
            "with miniature painting techniques (layering, washing, dry-brushing)",
            "with detailed scale representation (anatomical accuracy, proportion)",
            "with tabletop gaming mechanics (line of sight, cover, movement)",
            "with base creation and scenic display"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_board_games(prompt: str) -> str:
        """Enhance prompt with board games knowledge"""
        enhancements = [
            "with board game mechanics (worker placement, auction, tile placement, resource management)",
            "with victory condition design (points, elimination, objectives)",
            "with game component integration (cards, dice, tokens, boards)",
            "with player interaction and dynamic engagement"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_video_games(prompt: str) -> str:
        """Enhance prompt with video games knowledge"""
        enhancements = [
            "with video game mechanics (progression, combat, inventory, dialogue)",
            "with game engine considerations (Unity, Unreal optimization, cross-platform)",
            "with genre-specific mechanics (FPS shooting, RPG character development, RTS strategy)",
            "with player experience design (difficulty scaling, accessibility, UI/UX)"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_dnd(prompt: str) -> str:
        """Enhance prompt with D&D knowledge"""
        enhancements = [
            "with D&D mechanics (12+ classes, ability scores, combat system, spellcasting)",
            "with character creation and development (races, backgrounds, multiclassing)",
            "with monster mechanics and stat blocks (hit points, abilities, loot tables)",
            "with campaign and world-building (Forgotten Realms, Eberron, cosmology, adventure hooks)"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_algebra(prompt: str) -> str:
        """Enhance prompt with algebra knowledge"""
        enhancements = [
            "with algebraic concepts (equations, polynomial solving, function composition)",
            "with mathematical representations (graphing, transformations, systems of equations)",
            "with problem-solving methodology (factoring, substitution, matrix methods)",
            "with real-world applications (modeling, optimization, scientific computation)"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_chemistry(prompt: str) -> str:
        """Enhance prompt with chemistry knowledge"""
        enhancements = [
            "with chemical concepts (atomic structure, bonding, reactions, periodic table)",
            "with reaction mechanisms (oxidation-reduction, acid-base, precipitation)",
            "with thermochemistry (enthalpy, entropy, Gibbs free energy, spontaneity)",
            "with laboratory procedures (safety, measurements, calculations, analysis)"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_encyclopedia(prompt: str) -> str:
        """Enhance prompt with encyclopedia knowledge"""
        enhancements = [
            "with comprehensive knowledge (science, history, geography, culture, technology)",
            "with classification systems (scientific taxonomy, hierarchical organization)",
            "with historical context and cultural references",
            "with authoritative research-backed information"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def enhance_with_game_literature(prompt: str) -> str:
        """Enhance prompt with game literature knowledge"""
        enhancements = [
            "with rulebook structure and clarity (sections, examples, glossary)",
            "with game universe and lore (fantasy, sci-fi, horror settings)",
            "with narrative consistency and world-building (established canon, continuity)",
            "with thematic coherence and flavor text"
        ]
        return prompt + ", " + ", ".join(enhancements) if enhancements else prompt

    @staticmethod
    def apply_comprehensive_enhancement(prompt: str) -> Tuple[str, Dict[str, object]]:
        """Apply multi-domain enhancement based on detected domains"""
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)

        if not domains:
            return prompt, {
                'domains': [],
                'expansion_factor': 1.0,
                'enhancements_applied': []
            }

        enhanced = prompt
        original_length = len(prompt)
        enhancements_applied = []

        enhancement_methods = {
            'abstract_concepts': GamesAndConceptsEnhancer.enhance_with_abstract_concepts,
            'figurines': GamesAndConceptsEnhancer.enhance_with_figurines,
            'board_games': GamesAndConceptsEnhancer.enhance_with_board_games,
            'video_games': GamesAndConceptsEnhancer.enhance_with_video_games,
            'dungeons_dragons': GamesAndConceptsEnhancer.enhance_with_dnd,
            'algebra': GamesAndConceptsEnhancer.enhance_with_algebra,
            'chemistry': GamesAndConceptsEnhancer.enhance_with_chemistry,
            'encyclopedia': GamesAndConceptsEnhancer.enhance_with_encyclopedia,
            'game_literature': GamesAndConceptsEnhancer.enhance_with_game_literature
        }

        for domain in domains:
            if domain in enhancement_methods:
                enhanced = enhancement_methods[domain](enhanced)
                enhancements_applied.append(domain)

        expanded_length = len(enhanced)
        expansion_factor = expanded_length / original_length if original_length > 0 else 1.0

        return enhanced, {
            'domains': domains,
            'expansion_factor': expansion_factor,
            'enhancements_applied': enhancements_applied,
            'original_length': original_length,
            'expanded_length': expanded_length
        }


def get_games_and_concepts_system_prompt() -> str:
    """Generate system prompt with all games and concepts knowledge"""
    return """You are Bob AI, an expert system with comprehensive knowledge across multiple domains:

GAMES AND CONCEPTS EXPERTISE:

1. ABSTRACT CONCEPTS & PLAY THEORY
   - Play Types: Competitive, Cooperative, Role-Playing, Exploratory, Creative
   - Game Design: Balance, Pacing, Accessibility, Depth, Emergent Gameplay, Player Agency
   - Strategic Concepts: Strategy, Tactics, Probability, Resource Management, Territory Control
   - Player Psychology: Motivation, Engagement, Flow State, Retention

2. FIGURINES & MINIATURES
   - Painting Techniques: Priming, Base Coating, Washing, Dry-Brushing, Layering, Glazing
   - Scale Representation: Historical, Fantasy, Sci-Fi Figurines with Detailed Models
   - Tabletop Gaming: Line of Sight, Cover Mechanics, Movement, Unit Formations
   - Game Systems: Warhammer, Necromunda, Kill Team, Mordheim

3. BOARD GAMES
   - Game Mechanics: Turn Structure, Worker Placement, Auctions, Tile Placement, Resources
   - Victory Conditions: Points-Based, Elimination, Objectives, Cooperative
   - Components: Boards, Pieces, Cards, Dice, Tokens, Timers
   - Design Patterns: Progression, Balancing, Scaling, Thematic Elements, Education

4. VIDEO GAMES
   - Genres: Action (FPS/TPS), RPG (CRPG/JRPG/ARPG), Strategy (RTS/Turn-Based), Puzzle, Simulation
   - Game Engines: Unity, Unreal Engine, Godot, Custom Engines
   - Mechanics: Progression, Combat, Inventory, Dialogue, Difficulty Scaling
   - Art Direction: Visual Styles, UI Design, Level Design, Animation, Accessibility

5. DUNGEONS & DRAGONS & RPG SYSTEMS
   - Character System: 12+ Classes, Ability Scores, Races, Multiclassing
   - Combat System: Initiative, Actions, Attacks, Armor Class, Hit Points, Conditions, Spellcasting
   - Magic System: Spell Slots, 8 Schools, Saving Throws, Damage Types
   - Monsters: Creature Types, Abilities, Stat Blocks, Loot Tables
   - World-Building: Forgotten Realms, Eberron, Greyhawk, Cosmology, Lore
   - Adventuring: Travel Mechanics, Resting, Downtime, Encounters, Treasure

6. ALGEBRA & MATHEMATICS
   - Equations: Linear, Quadratic, Polynomial, Exponential, Logarithmic
   - Functions: Types, Transformations, Composition, Domain/Range
   - Systems: Linear Systems, Matrix Methods, Gaussian Elimination
   - Algebraic Structures: Groups, Fields, Vector Spaces
   - Real-World Applications: Modeling, Optimization, Scientific Computation

7. CHEMISTRY
   - Atomic Structure: Atoms, Bonding (Ionic, Covalent, Metallic, Hydrogen)
   - Periodic Table: Groups, Periods, Trends, Element Properties
   - Reactions: Types, Mechanisms, Rates, Equilibrium, Le Chatelier
   - Solutions: Concentration, Molarity, Solubility, Colligative Properties
   - Acids & Bases: pH Scale, Buffers, Titration, Strong/Weak Acids
   - Organic Chemistry: Functional Groups, Isomers, Polymerization
   - Thermochemistry: Enthalpy, Entropy, Gibbs Free Energy, Spontaneity

8. ENCYCLOPEDIA & COMPREHENSIVE KNOWLEDGE
   - Science: Physics, Chemistry, Biology, Earth Science, Astronomy
   - History: Ancient, Medieval, Modern, Contemporary Periods
   - Geography: Continents, Countries, Physical Features, Climate
   - Culture: Arts, Philosophy, Religion, Languages
   - Technology: Computing, Engineering, Transportation, Energy
   - Society: Government, Economics, Education, Health

9. GAME LITERATURE & DOCUMENTATION
   - Rulebooks: Structure, Examples, Glossary, Errata, Clarity
   - Gaming Universes: Fantasy, Sci-Fi, Horror, Superhero
   - World-Building: Lore, Canon, Cultural Coherence, Flavor

USE THESE KNOWLEDGE BASES TO:
- Create detailed game mechanics and rules
- Develop rich character backgrounds and worlds
- Design engaging gameplay experiences
- Explain complex scientific and mathematical concepts
- Provide authoritative educational content
- Integrate multiple knowledge domains for comprehensive responses
- Enhance creative writing with technical accuracy
- Generate balanced and engaging content

When responding to prompts, automatically enhance them with relevant knowledge from
these 9 domains to provide comprehensive, expert-level responses."""


def integrate_games_concepts_with_llm(prompt: str) -> Tuple[str, Dict[str, object]]:
    """Integrate games and concepts enhancement with LLM"""
    try:
        enhanced_prompt, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)
        logger.info(f"Enhancement successful: domains={metadata['domains']}")
        return enhanced_prompt, metadata
    except Exception as e:
        logger.error(f"Enhancement failed: {e}")
        return prompt, {'domains': [], 'expansion_factor': 1.0}


def test_games_concepts_knowledge():
    """Test games and concepts knowledge with sample prompts"""
    print("\n" + "="*70)
    print("TESTING GAMES AND CONCEPTS KNOWLEDGE ENHANCEMENT")
    print("="*70 + "\n")

    test_prompts = {
        "Create a strategic board game": "board_games",
        "Design a D&D campaign world": "dungeons_dragons",
        "Make an algebra equation solver": "algebra",
        "Explain a chemical reaction": "chemistry",
        "Build a video game character": "video_games",
        "Paint a fantasy miniature": "figurines",
        "Design game mechanics": "abstract_concepts",
        "Create an encyclopedia entry": "encyclopedia"
    }

    for prompt, expected_domain in test_prompts.items():
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        enhanced, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)

        status = "✅" if expected_domain in domains else "⚠️"
        print(f"{status} '{prompt}'")
        print(f"   Domains: {domains}")
        print(f"   Expansion: {metadata['expansion_factor']:.2f}x")
        enhancements_list = metadata['enhancements_applied']
        if isinstance(enhancements_list, list):
            enhancements_str = ', '.join(enhancements_list) if enhancements_list else 'none'
        else:
            enhancements_str = str(enhancements_list)
        print(f"   Enhancements: {enhancements_str}\n")

    print("="*70)
    print("✅ Games and Concepts Knowledge Testing Complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')

    # Initialize knowledge
    logger.info("Initializing games and concepts knowledge...")
    GamesCombinedIntegration.initialize_all_knowledge()
    logger.info("✅ Knowledge modules initialized\n")

    # Run tests
    test_games_concepts_knowledge()

    # Display system prompt
    print("\nSystem Prompt Generated:")
    system = get_games_and_concepts_system_prompt()
    print(f"Length: {len(system):,} characters")
    print(f"Domains Covered: 9 major knowledge domains\n")
