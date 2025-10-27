"""
Test Suite - Bob AI Advanced Knowledge (Anatomy, Physics, Motion, Geometry, Fluids)
===================================================================================

Tests for human anatomy, animal anatomy, physics, motion, geometry, and fluid dynamics.

Version: 3.0
Date: October 26, 2025
"""

import sys
import logging
from bob_ai_advanced_knowledge import (
    HumanAnatomyKnowledge,
    AnimalAnatomyKnowledge,
    PhysicsKnowledge,
    MotionAndDynamicsKnowledge,
    GeometryKnowledge,
    AdvancedFluidDynamicsKnowledge,
    AdvancedKnowledgeIntegration,
    initialize_advanced_knowledge
)
from bob_ai_advanced_knowledge_integration import (
    AdvancedKnowledgeEnhancer,
    get_advanced_knowledge_system_prompt,
    integrate_advanced_knowledge_with_llm
)

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
logger = logging.getLogger(__name__)


class AdvancedKnowledgeTestSuite:
    """Comprehensive test suite for advanced knowledge"""

    passed_tests = 0
    failed_tests = 0

    @staticmethod
    def test_result(test_name: str, condition: bool, details: str = ""):
        """Record and display test result"""
        if condition:
            AdvancedKnowledgeTestSuite.passed_tests += 1
            print(f"  ✓ {test_name}")
        else:
            AdvancedKnowledgeTestSuite.failed_tests += 1
            print(f"  ✗ {test_name}")
            if details:
                print(f"    Error: {details}")

    @staticmethod
    def test_human_anatomy():
        """Test human anatomy knowledge"""
        print("\n1. HUMAN ANATOMY KNOWLEDGE")
        print("-" * 60)

        # Test skeletal system
        skeletal = HumanAnatomyKnowledge.SKELETAL_SYSTEM
        AdvancedKnowledgeTestSuite.test_result(
            "Skeletal system data present",
            "skull" in skeletal and "spine" in skeletal and "limbs" in skeletal or "upper_limbs" in skeletal
        )

        # Test muscular system
        muscular = HumanAnatomyKnowledge.MUSCULAR_SYSTEM
        AdvancedKnowledgeTestSuite.test_result(
            "Muscular system data present",
            "head_neck" in muscular and "torso" in muscular and "lower_limbs" in muscular
        )

        # Test proportions
        proportions = HumanAnatomyKnowledge.PROPORTIONS
        AdvancedKnowledgeTestSuite.test_result(
            "Human proportions defined",
            "head" in proportions and "torso" in proportions and "leg" in proportions
        )

        # Test anatomy description
        desc = HumanAnatomyKnowledge.get_anatomy_description("skeleton")
        AdvancedKnowledgeTestSuite.test_result(
            "Anatomy descriptions available",
            len(desc) > 0 and "skeletal" in desc.lower()
        )

        print(f"  Skeletal system components: {len(skeletal)}")
        print(f"  Muscular system components: {len(muscular)}")
        print(f"  Proportion definitions: {len(proportions)}")

    @staticmethod
    def test_animal_anatomy():
        """Test animal anatomy knowledge"""
        print("\n2. ANIMAL ANATOMY KNOWLEDGE")
        print("-" * 60)

        # Test vertebrate anatomy
        vertebrates = AnimalAnatomyKnowledge.VERTEBRATE_ANATOMY
        AdvancedKnowledgeTestSuite.test_result(
            "Vertebrate classes defined",
            all(key in vertebrates for key in ["mammals", "birds", "reptiles", "amphibians", "fish"])
        )

        # Test quadruped locomotion
        quad_locomotion = AnimalAnatomyKnowledge.QUADRUPED_LOCOMOTION
        AdvancedKnowledgeTestSuite.test_result(
            "Quadruped locomotion mechanics defined",
            "gait_patterns" in quad_locomotion
        )

        # Test flight anatomy
        flight = AnimalAnatomyKnowledge.FLIGHT_ANATOMY
        AdvancedKnowledgeTestSuite.test_result(
            "Flight anatomy defined",
            "wing_structure" in flight and "skeletal_modifications" in flight
        )

        # Test marine locomotion
        marine = AnimalAnatomyKnowledge.MARINE_LOCOMOTION
        AdvancedKnowledgeTestSuite.test_result(
            "Marine locomotion mechanics defined",
            "fish_movement" in marine and "cetacean_movement" in marine
        )

        # Test predator anatomy
        predator = AnimalAnatomyKnowledge.PREDATOR_ANATOMY
        AdvancedKnowledgeTestSuite.test_result(
            "Predator anatomy specializations defined",
            "skeletal_specializations" in predator and "muscular_power" in predator
        )

        print(f"  Vertebrate classes: {len(vertebrates)}")
        print(f"  Specialized anatomies: 3 (Primate, Predator, Herbivore)")

    @staticmethod
    def test_physics_knowledge():
        """Test physics knowledge"""
        print("\n3. PHYSICS KNOWLEDGE")
        print("-" * 60)

        # Test mechanics
        mechanics = PhysicsKnowledge.MECHANICS
        AdvancedKnowledgeTestSuite.test_result(
            "Mechanics topics covered",
            all(key in mechanics for key in ["kinematics", "dynamics", "rotational_motion"])
        )

        # Test gravity and orbits
        gravity = PhysicsKnowledge.GRAVITY_AND_ORBITS
        AdvancedKnowledgeTestSuite.test_result(
            "Gravity and orbital mechanics defined",
            "gravitational_force" in gravity and "orbital_mechanics" in gravity
        )

        # Test waves
        waves = PhysicsKnowledge.VIBRATIONS_AND_WAVES
        AdvancedKnowledgeTestSuite.test_result(
            "Wave physics defined",
            "simple_harmonic_motion" in waves and "wave_properties" in waves
        )

        # Test physics principles
        principle = PhysicsKnowledge.get_physics_principle("newton_second")
        AdvancedKnowledgeTestSuite.test_result(
            "Physics principles accessible",
            len(principle) > 0 and "F=ma" in principle
        )

        print(f"  Mechanics sub-topics: {len(mechanics)}")
        print(f"  Physics principles: 6 available")

    @staticmethod
    def test_motion_knowledge():
        """Test motion and dynamics knowledge"""
        print("\n4. MOTION AND DYNAMICS KNOWLEDGE")
        print("-" * 60)

        # Test character motion
        motion = MotionAndDynamicsKnowledge.CHARACTER_MOTION
        AdvancedKnowledgeTestSuite.test_result(
            "Character motions defined",
            all(key in motion for key in ["walk", "run", "jump", "climb", "fall"])
        )

        # Test walk phases
        walk_phases = motion["walk"]["phases"]
        AdvancedKnowledgeTestSuite.test_result(
            "Walk gait phases defined",
            len(walk_phases) >= 6
        )

        # Test object dynamics
        objects = MotionAndDynamicsKnowledge.OBJECT_DYNAMICS
        AdvancedKnowledgeTestSuite.test_result(
            "Object dynamics covered",
            all(key in objects for key in ["projectile_motion", "rolling_motion", "collision", "spinning"])
        )

        # Test motion description
        desc = MotionAndDynamicsKnowledge.get_motion_description("run")
        AdvancedKnowledgeTestSuite.test_result(
            "Motion descriptions available",
            len(desc) > 0 and ("flight" in desc.lower() or "feet leave" in desc.lower())
        )

        print(f"  Character motions: {len(motion)}")
        print(f"  Object dynamics types: {len(objects)}")

    @staticmethod
    def test_geometry_knowledge():
        """Test geometry knowledge"""
        print("\n5. GEOMETRY KNOWLEDGE")
        print("-" * 60)

        # Test 2D shapes
        shapes_2d = GeometryKnowledge.SHAPES_2D
        AdvancedKnowledgeTestSuite.test_result(
            "2D shapes defined",
            all(key in shapes_2d for key in ["triangles", "quadrilaterals", "circles", "polygons"])
        )

        # Test 3D shapes
        shapes_3d = GeometryKnowledge.SHAPES_3D
        AdvancedKnowledgeTestSuite.test_result(
            "3D shapes defined",
            "polyhedra" in shapes_3d and "curved_surfaces" in shapes_3d
        )

        # Test polyhedra
        polyhedra = shapes_3d["polyhedra"]
        AdvancedKnowledgeTestSuite.test_result(
            "Platonic solids included",
            all(key in polyhedra for key in ["tetrahedron", "cube", "octahedron", "dodecahedron", "icosahedron"])
        )

        # Test spatial relationships
        spatial = GeometryKnowledge.SPATIAL_RELATIONSHIPS
        AdvancedKnowledgeTestSuite.test_result(
            "Spatial relationships defined",
            "position" in spatial and "distance" in spatial and "orientation" in spatial
        )

        # Test coordinate systems
        coords = GeometryKnowledge.COORDINATE_SYSTEMS
        AdvancedKnowledgeTestSuite.test_result(
            "Coordinate systems defined",
            all(key in coords for key in ["cartesian", "polar", "spherical", "cylindrical"])
        )

        print(f"  2D shape types: {len(shapes_2d)}")
        print(f"  3D shape categories: {len(shapes_3d)}")
        print(f"  Coordinate systems: {len(coords)}")

    @staticmethod
    def test_fluid_dynamics_knowledge():
        """Test fluid dynamics knowledge"""
        print("\n6. ADVANCED FLUID DYNAMICS KNOWLEDGE")
        print("-" * 60)

        # Test fundamental concepts
        fundamental = AdvancedFluidDynamicsKnowledge.FUNDAMENTAL_CONCEPTS
        AdvancedKnowledgeTestSuite.test_result(
            "Fundamental fluid concepts defined",
            all(key in fundamental for key in ["fluid_properties", "pressure", "flow_characteristics"])
        )

        # Test flow physics
        flow = AdvancedFluidDynamicsKnowledge.FLOW_PHYSICS
        AdvancedKnowledgeTestSuite.test_result(
            "Flow physics covered",
            all(key in flow for key in ["continuity_equation", "bernoulli_principle", "navier_stokes_equations"])
        )

        # Test aerodynamics
        aero = AdvancedFluidDynamicsKnowledge.AERODYNAMICS
        AdvancedKnowledgeTestSuite.test_result(
            "Aerodynamics knowledge present",
            all(key in aero for key in ["air_resistance", "lift_generation", "flow_patterns"])
        )

        # Test hydrodynamics
        hydro = AdvancedFluidDynamicsKnowledge.HYDRODYNAMICS
        AdvancedKnowledgeTestSuite.test_result(
            "Hydrodynamics knowledge present",
            all(key in hydro for key in ["water_flow", "swimming_mechanics", "wave_dynamics"])
        )

        # Test turbulence
        turbulence = AdvancedFluidDynamicsKnowledge.TURBULENCE_MODELING
        AdvancedKnowledgeTestSuite.test_result(
            "Turbulence modeling covered",
            "turbulent_characteristics" in turbulence and "eddy_viscosity" in turbulence
        )

        # Test vortex dynamics
        vortex = AdvancedFluidDynamicsKnowledge.VORTEX_DYNAMICS
        AdvancedKnowledgeTestSuite.test_result(
            "Vortex dynamics covered",
            all(key in vortex for key in ["vortex_formation", "vortex_interactions", "vortex_stability"])
        )

        # Test applications
        apps = AdvancedFluidDynamicsKnowledge.APPLICATIONS
        AdvancedKnowledgeTestSuite.test_result(
            "Real-world applications covered",
            len(apps) >= 5
        )

        print(f"  Fluid physics topics: {len(flow)}")
        print(f"  Aerodynamics components: {len(aero)}")
        print(f"  Application domains: {len(apps)}")

    @staticmethod
    def test_knowledge_enhancement():
        """Test knowledge-based prompt enhancement"""
        print("\n7. KNOWLEDGE-BASED PROMPT ENHANCEMENT")
        print("-" * 60)

        # Test domain detection
        test_prompts = {
            "human figure": "anatomy",
            "quadruped creature": "animal",
            "falling object": "physics",
            "running motion": "motion",
            "geometric sculpture": "geometry",
            "water flow": "fluids"
        }

        for prompt, expected_domain in test_prompts.items():
            domains = AdvancedKnowledgeEnhancer.detect_knowledge_domain(prompt)
            found = expected_domain in domains
            AdvancedKnowledgeTestSuite.test_result(
                f"Domain detection: '{prompt}' → {expected_domain}",
                found
            )

        # Test enhancement application
        test_prompt = "Create a human figure jumping with accurate physics"
        enhanced, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(test_prompt)

        AdvancedKnowledgeTestSuite.test_result(
            "Comprehensive enhancement works",
            len(enhanced) > len(test_prompt) and len(metadata["domains"]) > 0
        )

        AdvancedKnowledgeTestSuite.test_result(
            "Multiple domains detected",
            len(metadata["domains"]) >= 2
        )

        print(f"  Test prompts processed: 6")
        print(f"  Enhancement expansion factor: {metadata['expansion_factor']:.2f}x")

    @staticmethod
    def test_system_prompt_generation():
        """Test system prompt generation"""
        print("\n8. SYSTEM PROMPT GENERATION")
        print("-" * 60)

        system_prompt = get_advanced_knowledge_system_prompt()

        AdvancedKnowledgeTestSuite.test_result(
            "System prompt generated",
            len(system_prompt) > 1000
        )

        # Check for knowledge domain mentions
        domains_mentioned = all(domain in system_prompt for domain in [
            "HUMAN ANATOMY",
            "ANIMAL ANATOMY",
            "PHYSICS",
            "MOTION",
            "GEOMETRY",
            "FLUID DYNAMICS"
        ])

        AdvancedKnowledgeTestSuite.test_result(
            "All domains in system prompt",
            domains_mentioned
        )

        print(f"  System prompt size: {len(system_prompt):,} characters")
        print(f"  Knowledge domains covered: 6")

    @staticmethod
    def run_all_tests():
        """Run complete test suite"""
        print("\n" + "="*70)
        print("BOB AI ADVANCED KNOWLEDGE TEST SUITE")
        print("="*70)

        try:
            AdvancedKnowledgeTestSuite.test_human_anatomy()
            AdvancedKnowledgeTestSuite.test_animal_anatomy()
            AdvancedKnowledgeTestSuite.test_physics_knowledge()
            AdvancedKnowledgeTestSuite.test_motion_knowledge()
            AdvancedKnowledgeTestSuite.test_geometry_knowledge()
            AdvancedKnowledgeTestSuite.test_fluid_dynamics_knowledge()
            AdvancedKnowledgeTestSuite.test_knowledge_enhancement()
            AdvancedKnowledgeTestSuite.test_system_prompt_generation()

        except Exception as e:
            logger.error(f"Test suite error: {e}")
            AdvancedKnowledgeTestSuite.failed_tests += 1

        # Print summary
        total_tests = AdvancedKnowledgeTestSuite.passed_tests + AdvancedKnowledgeTestSuite.failed_tests
        pass_rate = (AdvancedKnowledgeTestSuite.passed_tests / total_tests * 100) if total_tests > 0 else 0

        print("\n" + "="*70)
        print("TEST SUMMARY")
        print("="*70)
        print(f"Total Tests: {total_tests}")
        print(f"Passed: {AdvancedKnowledgeTestSuite.passed_tests} ✓")
        print(f"Failed: {AdvancedKnowledgeTestSuite.failed_tests} ✗")
        print(f"Pass Rate: {pass_rate:.1f}%")

        if AdvancedKnowledgeTestSuite.failed_tests == 0:
            print("\n🎉 ALL TESTS PASSED!")
        else:
            print(f"\n⚠️ {AdvancedKnowledgeTestSuite.failed_tests} test(s) failed")

        print("="*70 + "\n")

        return AdvancedKnowledgeTestSuite.failed_tests == 0


if __name__ == "__main__":
    # Initialize knowledge
    logger.info("Initializing advanced knowledge modules...")
    initialize_advanced_knowledge()
    logger.info("✅ Knowledge modules initialized\n")

    # Run test suite
    success = AdvancedKnowledgeTestSuite.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)
