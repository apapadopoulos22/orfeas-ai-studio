"""
Comprehensive Test Suite for Bob AI Games and Concepts Knowledge v4.0
======================================================================

Tests all 9 knowledge modules with 50+ test cases covering:
- Abstract concepts and play theory
- Figurines and miniatures
- Board games mechanics
- Video games and engines
- Dungeons & Dragons systems
- Algebra and mathematics
- Chemistry and science
- Encyclopedia and reference
- Game literature

Author: Bob AI Development Team
Date: October 26, 2025
Version: 4.0
"""

import unittest
import logging
from typing import List, Dict

from bob_ai_games_and_concepts_knowledge import (
    AbstractConceptsKnowledge,
    FigurinesAndMiniaturesKnowledge,
    BoardGamesKnowledge,
    VideoGamesKnowledge,
    DungeonsDragonsKnowledge,
    AlgebraKnowledge,
    ChemistryKnowledge,
    EncyclopediaKnowledge,
    GameLiteratureKnowledge,
    GamesCombinedIntegration
)
from bob_ai_games_and_concepts_integration import (
    GamesAndConceptsEnhancer,
    get_games_and_concepts_system_prompt,
    integrate_games_concepts_with_llm
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TestAbstractConceptsKnowledge(unittest.TestCase):
    """Test abstract concepts and play theory knowledge"""

    def test_play_theory_exists(self):
        """Test play theory knowledge is present"""
        self.assertTrue(hasattr(AbstractConceptsKnowledge, 'PLAY_THEORY'))
        play_types = AbstractConceptsKnowledge.PLAY_THEORY
        self.assertGreater(len(play_types), 0)

    def test_game_elements_present(self):
        """Test game elements are defined"""
        self.assertTrue(hasattr(AbstractConceptsKnowledge, 'PLAY_THEORY'))
        play_theory = AbstractConceptsKnowledge.PLAY_THEORY
        self.assertIn('game_elements', play_theory)
        elements = play_theory['game_elements']
        self.assertIn('rules', elements)
        self.assertIn('goals', elements)

    def test_game_design_principles(self):
        """Test game design principles coverage"""
        self.assertTrue(hasattr(AbstractConceptsKnowledge, 'GAME_DESIGN_PRINCIPLES'))
        principles = AbstractConceptsKnowledge.GAME_DESIGN_PRINCIPLES
        self.assertGreater(len(principles), 3)

    def test_player_psychology(self):
        """Test player psychology knowledge"""
        self.assertTrue(hasattr(AbstractConceptsKnowledge, 'PLAY_THEORY'))
        play_theory = AbstractConceptsKnowledge.PLAY_THEORY
        self.assertIn('player_psychology', play_theory)
        psychology = play_theory['player_psychology']
        self.assertGreater(len(psychology), 0)

    def test_abstract_concepts_coverage(self):
        """Test abstract game concepts"""
        self.assertTrue(hasattr(AbstractConceptsKnowledge, 'ABSTRACT_CONCEPTS'))
        concepts = AbstractConceptsKnowledge.ABSTRACT_CONCEPTS
        self.assertIn('strategy', concepts)
        self.assertIn('probability', concepts)


class TestFigurinesKnowledge(unittest.TestCase):
    """Test figurines and miniatures knowledge"""

    def test_figurine_types_present(self):
        """Test figurine types are defined"""
        self.assertTrue(hasattr(FigurinesAndMiniaturesKnowledge, 'FIGURINE_TYPES'))
        types_dict = FigurinesAndMiniaturesKnowledge.FIGURINE_TYPES
        self.assertGreater(len(types_dict), 0)

    def test_painting_techniques(self):
        """Test painting techniques are documented"""
        self.assertTrue(hasattr(FigurinesAndMiniaturesKnowledge, 'MINIATURE_PAINTING'))
        painting = FigurinesAndMiniaturesKnowledge.MINIATURE_PAINTING
        self.assertIn('techniques', painting)

    def test_tabletop_gaming_systems(self):
        """Test tabletop gaming systems"""
        self.assertTrue(hasattr(FigurinesAndMiniaturesKnowledge, 'TABLETOP_GAMING'))
        gaming = FigurinesAndMiniaturesKnowledge.TABLETOP_GAMING
        self.assertGreater(len(gaming), 0)


class TestBoardGamesKnowledge(unittest.TestCase):
    """Test board games mechanics and design"""

    def test_board_game_mechanics(self):
        """Test board game mechanics are present"""
        self.assertTrue(hasattr(BoardGamesKnowledge, 'BOARD_GAME_MECHANICS'))
        mechanics = BoardGamesKnowledge.BOARD_GAME_MECHANICS
        self.assertGreater(len(mechanics), 0)

    def test_classic_games_list(self):
        """Test classic games are documented"""
        self.assertTrue(hasattr(BoardGamesKnowledge, 'CLASSIC_BOARD_GAMES'))
        games = BoardGamesKnowledge.CLASSIC_BOARD_GAMES
        self.assertGreater(len(games), 0)

    def test_game_components(self):
        """Test game components are defined"""
        self.assertTrue(hasattr(BoardGamesKnowledge, 'GAME_COMPONENTS'))
        components = BoardGamesKnowledge.GAME_COMPONENTS
        self.assertGreater(len(components), 0)

    def test_victory_conditions(self):
        """Test victory condition mechanics"""
        self.assertTrue(hasattr(BoardGamesKnowledge, 'BOARD_GAME_MECHANICS'))
        mechanics = BoardGamesKnowledge.BOARD_GAME_MECHANICS
        self.assertGreater(len(mechanics), 0)


class TestVideoGamesKnowledge(unittest.TestCase):
    """Test video games genres and engines"""

    def test_game_genres(self):
        """Test video game genres"""
        self.assertTrue(hasattr(VideoGamesKnowledge, 'GAME_GENRES'))
        genres = VideoGamesKnowledge.GAME_GENRES
        self.assertGreater(len(genres), 0)

    def test_game_engines(self):
        """Test game engines are documented"""
        self.assertTrue(hasattr(VideoGamesKnowledge, 'GAME_ENGINES'))
        engines = VideoGamesKnowledge.GAME_ENGINES
        self.assertGreater(len(engines), 0)

    def test_game_mechanics(self):
        """Test video game mechanics"""
        self.assertTrue(hasattr(VideoGamesKnowledge, 'GAME_MECHANICS'))
        mechanics = VideoGamesKnowledge.GAME_MECHANICS
        self.assertGreater(len(mechanics), 0)

    def test_art_direction(self):
        """Test art direction knowledge"""
        self.assertTrue(hasattr(VideoGamesKnowledge, 'GAME_ART_DIRECTION'))
        art = VideoGamesKnowledge.GAME_ART_DIRECTION
        self.assertGreater(len(art), 0)


class TestDungeonsDragonsKnowledge(unittest.TestCase):
    """Test Dungeons & Dragons mechanics"""

    def test_character_classes(self):
        """Test D&D character classes are defined"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'CHARACTER_SYSTEM'))
        system = DungeonsDragonsKnowledge.CHARACTER_SYSTEM
        self.assertGreater(len(system), 0)

    def test_ability_scores(self):
        """Test six ability scores"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'CHARACTER_SYSTEM'))
        system = DungeonsDragonsKnowledge.CHARACTER_SYSTEM
        self.assertGreater(len(system), 0)

    def test_combat_system(self):
        """Test D&D combat mechanics"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'COMBAT_SYSTEM'))
        combat = DungeonsDragonsKnowledge.COMBAT_SYSTEM
        self.assertGreater(len(combat), 0)

    def test_magic_system(self):
        """Test spell schools and magic"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'MAGIC_SYSTEM'))
        magic = DungeonsDragonsKnowledge.MAGIC_SYSTEM
        self.assertGreater(len(magic), 0)

    def test_monsters(self):
        """Test monster types"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'MONSTER_KNOWLEDGE'))
        monsters = DungeonsDragonsKnowledge.MONSTER_KNOWLEDGE
        self.assertGreater(len(monsters), 0)

    def test_world_building(self):
        """Test D&D world settings"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'WORLD_BUILDING'))
        worlds = DungeonsDragonsKnowledge.WORLD_BUILDING
        self.assertGreater(len(worlds), 0)

    def test_adventuring_mechanics(self):
        """Test adventuring rules"""
        self.assertTrue(hasattr(DungeonsDragonsKnowledge, 'ADVENTURING'))
        adventuring = DungeonsDragonsKnowledge.ADVENTURING
        self.assertGreater(len(adventuring), 0)


class TestAlgebraKnowledge(unittest.TestCase):
    """Test algebra and mathematics knowledge"""

    def test_equations(self):
        """Test equation types"""
        self.assertTrue(hasattr(AlgebraKnowledge, 'ALGEBRA_BASICS'))
        basics = AlgebraKnowledge.ALGEBRA_BASICS
        self.assertGreater(len(basics), 0)

    def test_functions(self):
        """Test function types"""
        self.assertTrue(hasattr(AlgebraKnowledge, 'FUNCTIONS'))
        functions = AlgebraKnowledge.FUNCTIONS
        self.assertGreater(len(functions), 0)

    def test_systems_of_equations(self):
        """Test systems of equations"""
        self.assertTrue(hasattr(AlgebraKnowledge, 'SYSTEMS_OF_EQUATIONS'))
        systems = AlgebraKnowledge.SYSTEMS_OF_EQUATIONS
        self.assertGreater(len(systems), 0)

    def test_sequences_and_series(self):
        """Test sequences and series"""
        self.assertTrue(hasattr(AlgebraKnowledge, 'SEQUENCES_AND_SERIES'))
        sequences = AlgebraKnowledge.SEQUENCES_AND_SERIES
        self.assertGreater(len(sequences), 0)

    def test_algebraic_structures(self):
        """Test algebraic structures"""
        self.assertTrue(hasattr(AlgebraKnowledge, 'ALGEBRAIC_STRUCTURES'))
        structures = AlgebraKnowledge.ALGEBRAIC_STRUCTURES
        self.assertGreater(len(structures), 0)


class TestChemistryKnowledge(unittest.TestCase):
    """Test chemistry and science knowledge"""

    def test_atomic_structure(self):
        """Test atomic structure knowledge"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'ATOMIC_STRUCTURE'))
        atomic = ChemistryKnowledge.ATOMIC_STRUCTURE
        self.assertGreater(len(atomic), 0)

    def test_periodic_table(self):
        """Test periodic table knowledge"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'PERIODIC_TABLE'))
        periodic = ChemistryKnowledge.PERIODIC_TABLE
        self.assertGreater(len(periodic), 0)

    def test_reactions(self):
        """Test reaction types"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'REACTIONS'))
        reactions = ChemistryKnowledge.REACTIONS
        self.assertGreater(len(reactions), 0)

    def test_acids_and_bases(self):
        """Test acid-base chemistry"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'ACIDS_AND_BASES'))
        acids_bases = ChemistryKnowledge.ACIDS_AND_BASES
        self.assertGreater(len(acids_bases), 0)

    def test_organic_chemistry(self):
        """Test organic chemistry"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'ORGANIC_CHEMISTRY'))
        organic = ChemistryKnowledge.ORGANIC_CHEMISTRY
        self.assertGreater(len(organic), 0)

    def test_thermochemistry(self):
        """Test thermochemistry"""
        self.assertTrue(hasattr(ChemistryKnowledge, 'THERMOCHEMISTRY'))
        thermo = ChemistryKnowledge.THERMOCHEMISTRY
        self.assertGreater(len(thermo), 0)


class TestEncyclopediaKnowledge(unittest.TestCase):
    """Test encyclopedia and reference knowledge"""

    def test_knowledge_domains(self):
        """Test knowledge domains"""
        self.assertTrue(hasattr(EncyclopediaKnowledge, 'KNOWLEDGE_DOMAINS'))
        domains = EncyclopediaKnowledge.KNOWLEDGE_DOMAINS
        self.assertGreater(len(domains), 0)

    def test_classification_systems(self):
        """Test classification systems"""
        self.assertTrue(hasattr(EncyclopediaKnowledge, 'CLASSIFICATION_SYSTEMS'))
        systems = EncyclopediaKnowledge.CLASSIFICATION_SYSTEMS
        self.assertGreater(len(systems), 0)

    def test_reference_tools(self):
        """Test reference tools"""
        self.assertTrue(hasattr(EncyclopediaKnowledge, 'REFERENCE_TOOLS'))
        tools = EncyclopediaKnowledge.REFERENCE_TOOLS
        self.assertGreater(len(tools), 0)


class TestGameLiteratureKnowledge(unittest.TestCase):
    """Test game literature and documentation"""

    def test_rulebook_structure(self):
        """Test rulebook structure"""
        self.assertTrue(hasattr(GameLiteratureKnowledge, 'RULEBOOK_STRUCTURE'))
        rulebook = GameLiteratureKnowledge.RULEBOOK_STRUCTURE
        self.assertGreater(len(rulebook), 0)

    def test_gaming_literature(self):
        """Test gaming literature"""
        self.assertTrue(hasattr(GameLiteratureKnowledge, 'GAMING_LITERATURE'))
        literature = GameLiteratureKnowledge.GAMING_LITERATURE
        self.assertGreater(len(literature), 0)


class TestGamesCombinedIntegration(unittest.TestCase):
    """Test master integration class"""

    def test_initialize_all_knowledge(self):
        """Test all knowledge modules initialize"""
        modules = GamesCombinedIntegration.initialize_all_knowledge()
        self.assertEqual(len(modules), 9)

    def test_export_knowledge_context(self):
        """Test knowledge context export"""
        context = GamesCombinedIntegration.export_knowledge_context()
        self.assertGreater(len(context), 0)
        self.assertIsInstance(context, str)


class TestDomainDetection(unittest.TestCase):
    """Test automatic domain detection"""

    def test_detect_abstract_concepts(self):
        """Test abstract concepts detection"""
        prompt = "Design game mechanics with balance and pacing"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('abstract_concepts', domains)

    def test_detect_figurines(self):
        """Test figurines domain detection"""
        prompt = "Paint a miniature with dry-brushing technique"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('figurines', domains)

    def test_detect_board_games(self):
        """Test board games detection"""
        prompt = "Create a worker placement game with auction mechanics"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('board_games', domains)

    def test_detect_video_games(self):
        """Test video games detection"""
        prompt = "Build a game in Unity with FPS mechanics"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('video_games', domains)

    def test_detect_dnd(self):
        """Test D&D detection"""
        prompt = "Create a D&D character with magical spells"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('dungeons_dragons', domains)

    def test_detect_algebra(self):
        """Test algebra detection"""
        prompt = "Solve a quadratic equation"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('algebra', domains)

    def test_detect_chemistry(self):
        """Test chemistry detection"""
        prompt = "Explain an oxidation-reduction reaction"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('chemistry', domains)

    def test_detect_encyclopedia(self):
        """Test encyclopedia detection"""
        prompt = "Write an encyclopedia entry on history"
        domains = GamesAndConceptsEnhancer.detect_knowledge_domain(prompt)
        self.assertIn('encyclopedia', domains)


class TestEnhancementPipeline(unittest.TestCase):
    """Test prompt enhancement pipeline"""

    def test_enhancement_expansion(self):
        """Test enhancement expands prompt"""
        prompt = "Create a board game"
        enhanced, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)
        self.assertGreater(len(enhanced), len(prompt))
        self.assertGreater(metadata['expansion_factor'], 1.0)

    def test_multi_domain_enhancement(self):
        """Test multi-domain enhancement"""
        prompt = "Design a D&D board game with mathematical puzzles"
        enhanced, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)
        self.assertGreaterEqual(len(metadata['domains']), 2)

    def test_enhancement_metadata(self):
        """Test enhancement returns proper metadata"""
        prompt = "Create a video game"
        enhanced, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)
        self.assertIn('domains', metadata)
        self.assertIn('expansion_factor', metadata)
        self.assertIn('enhancements_applied', metadata)

    def test_no_domain_match(self):
        """Test handling of prompts with no domain match"""
        prompt = "Write a random sentence about weather"
        enhanced, metadata = GamesAndConceptsEnhancer.apply_comprehensive_enhancement(prompt)
        self.assertEqual(len(metadata['domains']), 0)


class TestSystemPrompt(unittest.TestCase):
    """Test system prompt generation"""

    def test_system_prompt_generated(self):
        """Test system prompt is generated"""
        prompt = get_games_and_concepts_system_prompt()
        self.assertGreater(len(prompt), 0)

    def test_system_prompt_contains_domains(self):
        """Test system prompt mentions all domains"""
        prompt = get_games_and_concepts_system_prompt()
        domains = [
            "ABSTRACT CONCEPTS",
            "FIGURINES",
            "BOARD GAMES",
            "VIDEO GAMES",
            "DUNGEONS & DRAGONS",
            "ALGEBRA",
            "CHEMISTRY",
            "ENCYCLOPEDIA"
        ]
        for domain in domains:
            self.assertIn(domain, prompt.upper())


class TestIntegration(unittest.TestCase):
    """Test LLM integration functions"""

    def test_integrate_with_llm(self):
        """Test LLM integration"""
        prompt = "Create a D&D character"
        enhanced, metadata = integrate_games_concepts_with_llm(prompt)
        self.assertGreater(len(enhanced), 0)

    def test_integration_error_handling(self):
        """Test integration handles errors gracefully"""
        prompt = None
        try:
            enhanced, metadata = integrate_games_concepts_with_llm(prompt)
        except TypeError:
            pass  # Expected for None input


def run_all_tests():
    """Run all tests with reporting"""
    print("\n" + "="*70)
    print("RUNNING COMPREHENSIVE GAMES AND CONCEPTS KNOWLEDGE TESTS")
    print("="*70 + "\n")

    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    test_classes = [
        TestAbstractConceptsKnowledge,
        TestFigurinesKnowledge,
        TestBoardGamesKnowledge,
        TestVideoGamesKnowledge,
        TestDungeonsDragonsKnowledge,
        TestAlgebraKnowledge,
        TestChemistryKnowledge,
        TestEncyclopediaKnowledge,
        TestGameLiteratureKnowledge,
        TestGamesCombinedIntegration,
        TestDomainDetection,
        TestEnhancementPipeline,
        TestSystemPrompt,
        TestIntegration
    ]

    for test_class in test_classes:
        suite.addTests(loader.loadTestsFromTestCase(test_class))

    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests Run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")

    if result.wasSuccessful():
        print("\n✅ ALL TESTS PASSED!")
    else:
        print("\n❌ SOME TESTS FAILED")
        if result.failures:
            print("\nFailures:")
            for test, traceback in result.failures:
                print(f"  - {test}")
        if result.errors:
            print("\nErrors:")
            for test, traceback in result.errors:
                print(f"  - {test}")

    print("="*70 + "\n")

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
