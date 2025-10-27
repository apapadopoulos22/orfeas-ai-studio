"""
Bob AI Advanced Knowledge Integration
======================================

Integrates advanced knowledge (anatomy, physics, motion, geometry, fluid dynamics)
into LLM enhancement pipeline.

Version: 3.0
Date: October 26, 2025
"""

import logging
from typing import Dict, List, Optional, Tuple
from bob_ai_advanced_knowledge import (
    HumanAnatomyKnowledge,
    AnimalAnatomyKnowledge,
    PhysicsKnowledge,
    MotionAndDynamicsKnowledge,
    GeometryKnowledge,
    AdvancedFluidDynamicsKnowledge,
    AdvancedKnowledgeIntegration
)

logger = logging.getLogger(__name__)


class AdvancedKnowledgeEnhancer:
    """Enhances prompts with advanced domain knowledge"""

    DOMAIN_KEYWORDS = {
        "anatomy": ["anatomy", "skeleton", "muscle", "bone", "joint", "limb", "organ", "system",
                   "skeletal", "muscular", "nervous", "cardiovascular", "respiratory", "digestive",
                   "proportions", "anatomical", "body", "human", "figure", "character"],
        "animal": ["animal", "creature", "beast", "quadruped", "biped", "bird", "fish", "reptile",
                  "mammal", "amphibian", "predator", "prey", "herbivore", "carnivore", "omnivore",
                  "pet", "wildlife", "creature", "creature"],
        "physics": ["force", "motion", "energy", "momentum", "velocity", "acceleration", "gravity",
                   "pressure", "wave", "vibration", "elastic", "rigid", "dynamics", "kinematics",
                   "fall", "falling", "object", "drop", "collision", "impact"],
        "motion": ["walk", "run", "jump", "climb", "fly", "swim", "fall", "crawl", "gallop",
                  "sprint", "jog", "movement", "locomotion", "gait", "stride", "step", "running", "walking"],
        "geometry": ["triangle", "circle", "square", "cube", "sphere", "angle", "symmetry",
                    "geometric", "spatial", "dimension", "polygon", "polyhedron", "coordinate",
                    "sculpture", "shape", "form", "structure"],
        "fluids": ["flow", "water", "air", "wind", "aerodynamic", "hydrodynamic", "drag",
                  "turbulent", "laminar", "vortex", "fluid", "liquid", "gas", "current",
                  "aerodynamics", "streamlined", "streamline"]
    }

    @staticmethod
    def detect_knowledge_domain(prompt: str) -> List[str]:
        """Detect which knowledge domains are relevant to the prompt"""
        prompt_lower = prompt.lower()
        detected_domains = []

        for domain, keywords in AdvancedKnowledgeEnhancer.DOMAIN_KEYWORDS.items():
            if any(keyword in prompt_lower for keyword in keywords):
                detected_domains.append(domain)

        return detected_domains if detected_domains else ["general"]

    @staticmethod
    def enhance_with_anatomy_knowledge(prompt: str, animal_type: Optional[str] = None) -> str:
        """Enhance prompt with human/animal anatomy knowledge"""

        enhancements = []

        if "human" in prompt.lower() or "person" in prompt.lower() or not animal_type:
            # Add human anatomy context
            enhancements.append("featuring accurate human anatomy with proper skeletal proportions")
            enhancements.append("realistic muscular structure and anatomical accuracy")
            enhancements.append("correct joint articulation and movement mechanics")
            enhancements.append("anatomically sound body proportions (head=1/8 height, limb ratios correct)")

        if "animal" in prompt.lower() or animal_type:
            # Add animal anatomy context
            if "quadruped" in prompt.lower() or "four-legged" in prompt.lower():
                enhancements.append("quadrupedal anatomy with spine horizontal and limbs beneath body")
                enhancements.append("proper gait mechanics (walk, trot, canter, gallop)")

            if "bird" in prompt.lower() or "flying" in prompt.lower():
                enhancements.append("avian anatomy with hollow bones and specialized wing structure")
                enhancements.append("aerodynamic body design for flight")

            if "fish" in prompt.lower() or "swimming" in prompt.lower():
                enhancements.append("aquatic anatomy with streamlined hydrodynamic body shape")
                enhancements.append("fin structure optimized for water locomotion")

            if "predator" in prompt.lower():
                enhancements.append("predator anatomy with forward-facing eyes and powerful musculature")
                enhancements.append("specialized hunting mechanics and strike capability")

        enhanced = prompt + ", " + ", ".join(enhancements) if enhancements else prompt
        return enhanced

    @staticmethod
    def enhance_with_physics_knowledge(prompt: str) -> str:
        """Enhance prompt with physics principles"""

        enhancements = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["motion", "move", "accelerate", "speed", "velocity"]):
            enhancements.append("following Newton's laws of motion")
            enhancements.append("with accurate momentum conservation")

        if any(word in prompt_lower for word in ["force", "impact", "collision", "crash"]):
            enhancements.append("with realistic force dynamics and impact mechanics")
            enhancements.append("proper energy transfer during collision")

        if any(word in prompt_lower for word in ["jump", "fall", "gravity", "vertical"]):
            enhancements.append("subject to realistic gravitational acceleration (9.81 m/s²)")
            enhancements.append("with accurate parabolic trajectory")

        if any(word in prompt_lower for word in ["spin", "rotate", "twirl", "twist"]):
            enhancements.append("with proper angular momentum dynamics")
            enhancements.append("realistic rotational inertia effects")

        if any(word in prompt_lower for word in ["energy", "elastic", "oscillate", "vibrate"]):
            enhancements.append("with energy conservation principles")
            enhancements.append("accurate harmonic motion characteristics")

        enhanced = prompt + ", " + ", ".join(enhancements) if enhancements else prompt
        return enhanced

    @staticmethod
    def enhance_with_motion_knowledge(prompt: str) -> str:
        """Enhance prompt with motion and dynamics knowledge"""

        motion_types = {
            "walk": "bipedal gait with heel strike, mid-stance, and push-off phases",
            "run": "high-speed locomotion with flight phase and ground reaction forces",
            "jump": "explosive movement with squat preparation and takeoff power",
            "climb": "ascending movement with grip strength and core engagement",
            "fall": "downward acceleration under gravity with body control",
            "swim": "propulsive movement using limbs with hydrodynamic efficiency",
            "fly": "sustained aerial movement through wing manipulation"
        }

        prompt_lower = prompt.lower()
        enhancements = []

        for motion, description in motion_types.items():
            if motion in prompt_lower:
                enhancements.append(f"{motion} mechanics featuring {description}")

        if enhancements:
            enhanced = prompt + ", " + ", ".join(enhancements)
        else:
            enhanced = prompt

        return enhanced

    @staticmethod
    def enhance_with_geometry_knowledge(prompt: str) -> str:
        """Enhance prompt with geometry and spatial relationships"""

        enhancements = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["symmetry", "symmetrical", "mirror", "bilateral"]):
            enhancements.append("featuring bilateral symmetry and balanced proportions")

        if any(word in prompt_lower for word in ["geometric", "angular", "shape", "form"]):
            enhancements.append("with precise geometric forms and correct spatial relationships")

        if any(word in prompt_lower for word in ["sphere", "cube", "cylinder", "cone", "pyramid"]):
            enhancements.append("using perfect polyhedra and geometric solids")

        if any(word in prompt_lower for word in ["composition", "balance", "center", "alignment"]):
            enhancements.append("with proper geometric composition and balanced spatial distribution")

        if any(word in prompt_lower for word in ["perspective", "dimension", "depth", "3d"]):
            enhancements.append("accurate three-dimensional geometric perspective")

        enhanced = prompt + ", " + ", ".join(enhancements) if enhancements else prompt
        return enhanced

    @staticmethod
    def enhance_with_fluid_dynamics_knowledge(prompt: str) -> str:
        """Enhance prompt with fluid dynamics and aerodynamics"""

        enhancements = []
        prompt_lower = prompt.lower()

        if any(word in prompt_lower for word in ["aerodynamic", "air", "wind", "flow", "streamline"]):
            enhancements.append("aerodynamically optimized with reduced drag coefficient")
            enhancements.append("streamlined design following fluid flow principles")
            enhancements.append("featuring laminar flow patterns around surfaces")

        if any(word in prompt_lower for word in ["water", "swim", "marine", "hydrodynamic", "aquatic"]):
            enhancements.append("hydrodynamically efficient with water-optimized shape")
            enhancements.append("reduced drag in aquatic environments")
            enhancements.append("following swimming mechanics principles")

        if any(word in prompt_lower for word in ["vortex", "swirl", "turbulent", "eddy", "tornado"]):
            enhancements.append("featuring realistic vortex dynamics and turbulent flow")
            enhancements.append("accurate eddy formation and energy dissipation")

        if any(word in prompt_lower for word in ["lift", "wing", "flight", "hover"]):
            enhancements.append("generating aerodynamic lift through wing design")
            enhancements.append("optimized for sustained flight efficiency")

        if any(word in prompt_lower for word in ["pressure", "force", "drag", "resistance"]):
            enhancements.append("with accurate pressure distribution and drag forces")
            enhancements.append("realistic fluid resistance effects")

        enhanced = prompt + ", " + ", ".join(enhancements) if enhancements else prompt
        return enhanced

    @staticmethod
    def apply_comprehensive_enhancement(prompt: str) -> Tuple[str, Dict]:
        """Apply all relevant advanced knowledge enhancements"""

        # Detect relevant domains
        domains = AdvancedKnowledgeEnhancer.detect_knowledge_domain(prompt)

        enhanced_prompt = prompt
        applied_enhancements = {"original": prompt, "domains": domains}

        # Apply domain-specific enhancements
        if "anatomy" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_anatomy_knowledge(enhanced_prompt)
            applied_enhancements["anatomy"] = True

        if "physics" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_physics_knowledge(enhanced_prompt)
            applied_enhancements["physics"] = True

        if "motion" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_motion_knowledge(enhanced_prompt)
            applied_enhancements["motion"] = True

        if "geometry" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_geometry_knowledge(enhanced_prompt)
            applied_enhancements["geometry"] = True

        if "fluids" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_fluid_dynamics_knowledge(enhanced_prompt)
            applied_enhancements["fluids"] = True

        if "animal" in domains:
            enhanced_prompt = AdvancedKnowledgeEnhancer.enhance_with_anatomy_knowledge(
                enhanced_prompt,
                animal_type="generic_animal"
            )
            applied_enhancements["animal"] = True

        applied_enhancements["enhanced"] = enhanced_prompt
        applied_enhancements["expansion_factor"] = len(enhanced_prompt) / len(prompt) if prompt else 1

        return enhanced_prompt, applied_enhancements


def get_advanced_knowledge_system_prompt() -> str:
    """Generate comprehensive system prompt with all advanced knowledge"""

    return AdvancedKnowledgeIntegration.export_knowledge_context()


def integrate_advanced_knowledge_with_llm(prompt: str, use_advanced_knowledge: bool = True) -> str:
    """
    Integrate advanced knowledge into LLM prompt enhancement

    Args:
        prompt: Original user prompt
        use_advanced_knowledge: Whether to apply advanced knowledge enhancement

    Returns:
        Enhanced prompt with advanced knowledge
    """

    if not use_advanced_knowledge:
        return prompt

    try:
        enhanced_prompt, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(prompt)

        logger.info(f"Advanced Knowledge Enhancement Applied:")
        logger.info(f"  Domains detected: {metadata['domains']}")
        logger.info(f"  Expansion factor: {metadata['expansion_factor']:.2f}x")

        return enhanced_prompt

    except Exception as e:
        logger.error(f"Error applying advanced knowledge: {e}")
        return prompt


def test_advanced_knowledge():
    """Test advanced knowledge enhancement with sample prompts"""

    test_prompts = [
        "Create a human figure in a dynamic jump pose",
        "Design a predatory quadruped creature with powerful muscles",
        "Render a bird in flight with realistic wing aerodynamics",
        "Visualize a water droplet collision with hydrodynamic effects",
        "Design an object falling under gravity with correct physics",
        "Create a geometric sculpture with perfect symmetry",
        "Visualize air flow around a streamlined object"
    ]

    print("\n" + "="*70)
    print("ADVANCED KNOWLEDGE ENHANCEMENT TEST")
    print("="*70 + "\n")

    for i, prompt in enumerate(test_prompts, 1):
        enhanced, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(prompt)

        print(f"Test {i}: {prompt}")
        print(f"  Domains: {metadata['domains']}")
        print(f"  Expansion: {metadata['expansion_factor']:.2f}x")
        print(f"  Enhanced: {enhanced[:100]}...")
        print()

    print("="*70)
    print("Advanced knowledge enhancement test complete!")
    print("="*70 + "\n")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )

    logger.info("Initializing Advanced Knowledge Integration...")

    # Initialize all knowledge modules
    modules = AdvancedKnowledgeIntegration.initialize_all_knowledge()

    logger.info("✅ Advanced Knowledge Integration initialized successfully\n")

    # Run tests
    test_advanced_knowledge()
