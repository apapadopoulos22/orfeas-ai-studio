"""
Bob AI Advanced Prompt Enhancement Engine
==========================================
Expanded capabilities for intelligent prompt enrichment and context injection

Features:
- Multi-context prompt analysis and enrichment
- Semantic depth enhancement
- Context-aware quality boost
- Domain-specific expansion
- Creative element injection
- Technical specification enhancement
- Emotional resonance optimization
- Cultural context integration

Author: ORFEAS AI
Date: 2025-10-26
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from bob_ai_knowledge_base import BobAIKnowledgeBase

logger = logging.getLogger(__name__)


class AdvancedPromptEnhancer:
    """Advanced prompt enhancement with multiple strategies"""

    # Keywords that trigger specific enhancement strategies
    DESIGN_KEYWORDS = {
        "minimalist", "steampunk", "cyberpunk", "gothic", "art_deco", "futuristic",
        "maximalism", "brutalist", "vintage", "retro", "modern", "contemporary",
        "bohemian", "industrial", "organic", "geometric", "surreal", "noir"
    }

    QUALITY_KEYWORDS = {
        "detailed", "simple", "clean", "complex", "hyper-detailed", "photorealistic",
        "game-ready", "painted", "concept", "professional", "high-quality", "low-poly"
    }

    MATERIAL_KEYWORDS = {
        "metal", "wood", "glass", "ceramic", "stone", "plastic", "rubber", "fabric",
        "concrete", "marble", "granite", "copper", "bronze", "aluminum", "carbon"
    }

    LIGHTING_KEYWORDS = {
        "ambient", "dramatic", "warm", "cool", "rim", "volumetric", "neon",
        "chiaroscuro", "diffuse", "direct", "bioluminescent", "fluorescent",
        "candlelight", "moonlight", "spotlight"
    }

    ATMOSPHERE_KEYWORDS = {
        "peaceful", "tense", "mysterious", "ethereal", "chaotic", "elegant",
        "dark", "bright", "gloomy", "serene", "vibrant", "calm", "energetic"
    }

    @staticmethod
    def detect_prompt_context(prompt: str) -> Dict[str, any]:
        """Analyze prompt to detect context and intent"""
        context: Dict[str, any] = {
            "design_styles": [],
            "materials": [],
            "lighting": [],
            "atmosphere": [],
            "quality_levels": [],
            "scale": None,
            "has_action": False,
            "has_emotion": False,
            "has_cultural_ref": False,
        }

        prompt_lower = prompt.lower()

        # Detect design styles
        for style in AdvancedPromptEnhancer.DESIGN_KEYWORDS:
            if style.replace("_", " ") in prompt_lower or style in prompt_lower:
                context["design_styles"].append(style)

        # Detect materials
        for material in AdvancedPromptEnhancer.MATERIAL_KEYWORDS:
            if material.replace("_", " ") in prompt_lower or material in prompt_lower:
                context["materials"].append(material)

        # Detect lighting
        for lighting in AdvancedPromptEnhancer.LIGHTING_KEYWORDS:
            if lighting.replace("_", " ") in prompt_lower or lighting in prompt_lower:
                context["lighting"].append(lighting)

        # Detect atmosphere
        for atmosphere in AdvancedPromptEnhancer.ATMOSPHERE_KEYWORDS:
            if atmosphere.replace("_", " ") in prompt_lower or atmosphere in prompt_lower:
                context["atmosphere"].append(atmosphere)

        # Detect quality levels
        for quality in AdvancedPromptEnhancer.QUALITY_KEYWORDS:
            if quality.replace("_", " ") in prompt_lower or quality in prompt_lower:
                context["quality_levels"].append(quality)

        # Detect action verbs
        for action in BobAIKnowledgeBase.ACTION_VERBS.values():
            if any(verb.lower() in prompt_lower for verb in action.split(",")):
                context["has_action"] = True
                break

        # Detect emotions
        for emotion in BobAIKnowledgeBase.EMOTION_ASSOCIATIONS.keys():
            if emotion.replace("_", " ") in prompt_lower or emotion in prompt_lower:
                context["has_emotion"] = True
                break

        # Detect cultural references
        for culture in BobAIKnowledgeBase.CULTURAL_REFERENCES.keys():
            if culture.replace("_", " ") in prompt_lower or culture in prompt_lower:
                context["has_cultural_ref"] = True
                break

        return context

    @staticmethod
    def enhance_with_semantic_depth(prompt: str, context: Dict) -> str:
        """Add semantic depth to prompt based on detected context"""
        enhancements = []

        # Add design style details
        if context["design_styles"]:
            style = context["design_styles"][0]
            if style in BobAIKnowledgeBase.DESIGN_STYLES:
                style_desc = BobAIKnowledgeBase.DESIGN_STYLES[style]
                enhancements.append(f"{style} style featuring {style_desc}")

        # Add material properties
        if context["materials"]:
            material = context["materials"][0]
            if material in BobAIKnowledgeBase.MATERIAL_PROPERTIES:
                mat_desc = BobAIKnowledgeBase.MATERIAL_PROPERTIES[material]
                enhancements.append(f"crafted from {material} with {mat_desc} qualities")

        # Add lighting enhancement
        if context["lighting"]:
            lighting = context["lighting"][0]
            if lighting in BobAIKnowledgeBase.LIGHTING_EFFECTS:
                light_desc = BobAIKnowledgeBase.LIGHTING_EFFECTS[lighting]
                enhancements.append(f"{lighting} lighting ({light_desc})")
        else:
            # Default professional lighting
            enhancements.append("professional studio lighting with balanced shadows")

        # Add atmospheric enhancement
        if context["atmosphere"]:
            atmosphere = context["atmosphere"][0]
            if atmosphere in BobAIKnowledgeBase.ATMOSPHERE_DESCRIPTORS:
                atmo_desc = BobAIKnowledgeBase.ATMOSPHERE_DESCRIPTORS[atmosphere]
                enhancements.append(f"{atmosphere} atmosphere ({atmo_desc})")

        # Build enhanced prompt
        enhanced = prompt

        if enhancements:
            enhanced += ", featuring " + ", ".join(enhancements)

        return enhanced

    @staticmethod
    def enhance_with_technical_specs(prompt: str, context: Dict) -> str:
        """Add technical specifications and rendering details"""
        specs = []

        # Quality specification
        if context["quality_levels"]:
            specs.append(context["quality_levels"][0] + " quality")
        else:
            specs.append("high quality")

        # Add rendering details
        specs.append("professionally rendered")
        specs.append("detailed textures")
        specs.append("accurate proportions")

        # Add composition principle
        comp_principle = list(BobAIKnowledgeBase.COMPOSITION_PRINCIPLES.values())[0]
        specs.append(f"composition following {comp_principle}")

        # Build technical enhancement
        technical = ", with " + ", ".join(specs)
        return prompt + technical

    @staticmethod
    def enhance_with_emotional_resonance(prompt: str) -> str:
        """Inject emotional resonance and artistic direction"""
        emotions = list(BobAIKnowledgeBase.EMOTION_ASSOCIATIONS.keys())
        random_emotion = emotions[hash(prompt) % len(emotions)]
        emotion_desc = BobAIKnowledgeBase.EMOTION_ASSOCIATIONS[random_emotion]

        enhancement = f", evoking {random_emotion} ({emotion_desc})"
        return prompt + enhancement

    @staticmethod
    def enhance_with_composition_principles(prompt: str) -> str:
        """Add composition and layout principles"""
        principles = BobAIKnowledgeBase.COMPOSITION_PRINCIPLES
        principle = list(principles.values())[hash(prompt) % len(principles)]

        enhancement = f", using {principle} for visual balance"
        return prompt + enhancement

    @staticmethod
    def enhance_with_cultural_context(prompt: str) -> str:
        """Integrate cultural and historical context"""
        cultures = BobAIKnowledgeBase.CULTURAL_REFERENCES
        culture = list(cultures.values())[hash(prompt) % len(cultures)]

        enhancement = f", inspired by {culture} aesthetic"
        return prompt + enhancement

    @staticmethod
    def boost_description_density(prompt: str) -> str:
        """Increase descriptive density for richer output"""
        # Add texture descriptors
        texture = list(BobAIKnowledgeBase.TEXTURE_DESCRIPTORS.values())[hash(prompt) % 15]
        enhancement = f", with {texture} surfaces"

        # Add scale reference
        scale = list(BobAIKnowledgeBase.SIZE_SCALES.keys())[hash(prompt) % 8]
        enhancement += f", at {scale} scale"

        # Add color palette reference
        colors = list(BobAIKnowledgeBase.COLOR_PALETTES.values())[hash(prompt) % 15]
        enhancement += f", employing {colors} palette"

        return prompt + enhancement

    @staticmethod
    def generate_system_context_for_3d(context: Dict = None) -> str:
        """Generate specialized system context for 3D generation"""
        system = """You are Bob AI, specialized in 3D content generation with expertise in:

DESIGN MASTERY:
- 15+ design styles with distinct characteristics and best practices
- Material properties and their visual/physical implications
- Professional lighting techniques and mood creation
- Color theory and psychological impact

3D GENERATION SPECIFICS:
- Polygon optimization (low-poly vs high-detail trade-offs)
- Texture mapping and UV unwrapping considerations
- Lighting setup for render engines (Arnold, V-Ray, RenderMan)
- File format considerations (OBJ, FBX, GLB, STL)
- Game engine optimization (UE5, Unity requirements)

ARTISTIC PRINCIPLES:
- Composition and visual hierarchy
- Balance between realism and stylization
- Cultural and historical authenticity
- Emotional impact through visual design

When generating 3D content, consider:
1. Geometric complexity vs performance
2. Material authenticity and realism
3. Lighting for optimal presentation
4. Composition for visual interest
5. Technical constraints of target platform

Your responses should include specific technical guidance for 3D artists."""

        return system

    @staticmethod
    def generate_system_context_for_design(context: Dict = None) -> str:
        """Generate specialized system context for design work"""
        system = """You are Bob AI, specialized in design consultation with expertise in:

DESIGN EXPERTISE:
- 15+ design styles with historical context and application
- Material selection and properties for different aesthetics
- Color psychology and palette creation
- Lighting design for mood and focus
- Composition principles for visual impact

DESIGN SPECIALIZATIONS:
- Interior Design: Spatial planning, furniture, decor
- Graphic Design: Typography, layout, visual hierarchy
- Product Design: Form, function, ergonomics, materials
- Architectural Design: Structures, landscapes, urban planning
- Fashion Design: Clothing, textures, color coordination

DESIGN PRINCIPLES:
- Balance and symmetry
- Contrast and emphasis
- Repetition and pattern
- Proportion and scale
- Unity and harmony

When providing design advice:
1. Consider target audience and context
2. Balance aesthetics with functionality
3. Account for cultural and historical influences
4. Suggest specific materials and techniques
5. Provide actionable implementation guidance

Your responses should be practical and inspiring."""

        return system

    @staticmethod
    def generate_system_context_for_creative(context: Dict = None) -> str:
        """Generate specialized system context for creative/artistic work"""
        system = """You are Bob AI, specialized in creative and artistic content with expertise in:

CREATIVE DOMAINS:
- Visual art and painting techniques
- Sculpture and 3D form
- Photography and cinematography
- Animation and motion
- Game design and interactive media

ARTISTIC ELEMENTS:
- Color theory and emotional impact
- Composition and visual storytelling
- Texture and materiality
- Lighting and atmosphere
- Cultural and artistic movements

CREATIVE PROCESS:
- Ideation and conceptualization
- Mood board creation
- Style development
- Technical execution
- Iteration and refinement

STYLE MASTERY:
- Renaissance and classical techniques
- Modern and contemporary approaches
- Experimental and avant-garde
- Cultural and indigenous aesthetics
- Digital and new media art

When assisting with creative work:
1. Encourage artistic exploration
2. Suggest technical approaches
3. Reference relevant artistic movements
4. Consider emotional impact
5. Balance innovation with craft

Your responses should inspire creativity while providing practical guidance."""

        return system


class PromptEnhancementPipeline:
    """Complete pipeline for multi-stage prompt enhancement"""

    @staticmethod
    def apply_full_enhancement(prompt: str, enhancement_level: str = "high") -> str:
        """Apply full enhancement pipeline to prompt"""

        # Stage 1: Context detection
        context = AdvancedPromptEnhancer.detect_prompt_context(prompt)

        # Stage 2: Semantic depth enhancement
        enhanced = AdvancedPromptEnhancer.enhance_with_semantic_depth(prompt, context)

        # Stage 3: Technical specifications
        enhanced = AdvancedPromptEnhancer.enhance_with_technical_specs(enhanced, context)

        # Stage 4: Emotional resonance (if requested)
        if enhancement_level in ["high", "ultra"]:
            enhanced = AdvancedPromptEnhancer.enhance_with_emotional_resonance(enhanced)

        # Stage 5: Composition principles (if requested)
        if enhancement_level in ["high", "ultra"]:
            enhanced = AdvancedPromptEnhancer.enhance_with_composition_principles(enhanced)

        # Stage 6: Description density boost
        if enhancement_level == "ultra":
            enhanced = AdvancedPromptEnhancer.boost_description_density(enhanced)

        # Stage 7: Cultural context (if requested)
        if enhancement_level == "ultra":
            enhanced = AdvancedPromptEnhancer.enhance_with_cultural_context(enhanced)

        logger.info(f"[BOB-AI] Prompt enhanced: {len(prompt)} → {len(enhanced)} chars")
        return enhanced

    @staticmethod
    def apply_domain_specific_enhancement(
        prompt: str,
        domain: str = "general",
        enhancement_level: str = "high"
    ) -> Tuple[str, str]:
        """Apply domain-specific enhancement with appropriate system context

        Args:
            prompt: User prompt to enhance
            domain: "3d", "design", "creative", "general"
            enhancement_level: "low", "medium", "high", "ultra"

        Returns:
            Tuple of (enhanced_prompt, system_context)
        """

        # Apply full enhancement
        enhanced_prompt = PromptEnhancementPipeline.apply_full_enhancement(
            prompt, enhancement_level
        )

        # Generate domain-specific system context
        if domain == "3d":
            system_context = AdvancedPromptEnhancer.generate_system_context_for_3d()
        elif domain == "design":
            system_context = AdvancedPromptEnhancer.generate_system_context_for_design()
        elif domain == "creative":
            system_context = AdvancedPromptEnhancer.generate_system_context_for_creative()
        else:
            # Generic system context
            system_context = """You are Bob AI, an advanced creative assistant with comprehensive
knowledge of design, art, materials, and visual concepts. Provide detailed,
imaginative, and technically sound responses."""

        return enhanced_prompt, system_context

    @staticmethod
    def interactive_enhancement_session(
        initial_prompt: str,
        max_refinements: int = 3
    ) -> Dict:
        """Run an interactive refinement session for progressive enhancement"""

        session = {
            "initial_prompt": initial_prompt,
            "iterations": [],
            "final_enhanced": initial_prompt,
        }

        current_prompt = initial_prompt
        context = AdvancedPromptEnhancer.detect_prompt_context(initial_prompt)

        # Progressive refinement
        for iteration in range(max_refinements):
            enhanced = PromptEnhancementPipeline.apply_full_enhancement(
                current_prompt,
                enhancement_level="high" if iteration < 2 else "ultra"
            )

            session["iterations"].append({
                "iteration": iteration + 1,
                "input": current_prompt,
                "output": enhanced,
                "context_detected": context,
            })

            current_prompt = enhanced

        session["final_enhanced"] = current_prompt
        return session


# Module initialization
def initialize_advanced_enhancer():
    """Initialize and log advanced enhancer availability"""
    logger.info("[BOB-AI] Advanced Prompt Enhancement Engine initialized")
    logger.info("[BOB-AI] Available enhancement levels: low, medium, high, ultra")
    logger.info("[BOB-AI] Available domains: general, 3d, design, creative")


if __name__ == "__main__":
    # Example usage
    initialize_advanced_enhancer()

    test_prompts = [
        "Create a minimalist house",
        "Design a steampunk robot",
        "Make a peaceful garden at sunset",
        "A cyberpunk city at night",
        "A wooden sculpture",
    ]

    print("\n" + "=" * 80)
    print("ADVANCED BOB AI PROMPT ENHANCEMENT - EXAMPLES")
    print("=" * 80 + "\n")

    for prompt in test_prompts:
        print(f"Original:  {prompt}")

        enhanced_low, _ = PromptEnhancementPipeline.apply_domain_specific_enhancement(
            prompt, domain="general", enhancement_level="low"
        )
        print(f"Enhanced:  {enhanced_low}")

        enhanced_ultra, system = PromptEnhancementPipeline.apply_domain_specific_enhancement(
            prompt, domain="3d", enhancement_level="ultra"
        )
        print(f"Ultra 3D:  {enhanced_ultra}\n")

    print("=" * 80)
