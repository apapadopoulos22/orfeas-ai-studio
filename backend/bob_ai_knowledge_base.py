"""
Bob AI Knowledge Base & Semantic Enrichment
============================================
Comprehensive dictionaries and semantic libraries for Bob AI LLM enhancement
Provides world knowledge, contextual understanding, and semantic relationships

Author: ORFEAS AI
Date: 2025-10-26
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class BobAIKnowledgeBase:
    """Comprehensive knowledge base for Bob AI with semantic enhancement"""

    # === DOMAIN DICTIONARIES ===

    DESIGN_STYLES = {
        # 3D Design Styles
        "minimalist": "Clean lines, simple geometric forms, minimal details, spacious composition",
        "steampunk": "Industrial aesthetic, brass, gears, Victorian machinery, clockwork elements",
        "cyberpunk": "Futuristic, neon colors, digital effects, technology-driven, dystopian",
        "art_deco": "Geometric patterns, symmetry, luxury materials, 1920s elegance",
        "brutalist": "Raw concrete, massive forms, geometric shapes, monumental",
        "organic": "Natural curves, biological shapes, nature-inspired, flowing forms",
        "geometric": "Precise shapes, mathematical patterns, angular, systematic",
        "surreal": "Dream-like, impossible combinations, fantasy elements, abstract",
        "noir": "Dark, dramatic lighting, high contrast, mysterious, film noir aesthetic",
        "retro": "Vintage styling, 1950s-1980s aesthetics, nostalgic elements",
        "futuristic": "Advanced technology, sleek design, smooth curves, sci-fi elements",
        "gothic": "Dark, ornate, medieval elements, mysterious, dramatic",
        "baroque": "Ornate, intricate details, rich textures, elaborate decoration",
        "modern": "Contemporary, clean, functional, minimalist elements",
        "vintage": "Aged appearance, history, patina, antique qualities",
    }

    MATERIAL_PROPERTIES = {
        # Materials with physical properties
        "metal": "Reflective, conductive, strong, dense, industrial",
        "wood": "Organic, warm, grain texture, biodegradable, natural",
        "ceramic": "Brittle, smooth, clay-based, firing required, decorative",
        "glass": "Transparent, reflective, fragile, light-transmitting",
        "stone": "Solid, ancient, carved, monumental, weighty",
        "plastic": "Synthetic, lightweight, moldable, affordable, varied textures",
        "rubber": "Elastic, flexible, durable, gripping surface",
        "fabric": "Soft, textile, draping, varied patterns, tactile",
        "concrete": "Porous, urban, massive, raw appearance",
        "marble": "Smooth, elegant, veined, luxurious, durable",
        "granite": "Speckled, hard, natural stone, polished surface",
        "copper": "Reddish metal, oxidizes, conductive, valuable",
        "bronze": "Alloy, classical, patina develops, sculptural",
        "aluminum": "Lightweight metal, silvery, modern, aircraft grade",
        "carbon_fiber": "Composite, strong, expensive, modern, sleek",
    }

    LIGHTING_EFFECTS = {
        # Lighting techniques and moods
        "ambient": "Overall general lighting, soft, even distribution",
        "dramatic": "High contrast, directed light, theatrical effect",
        "warm": "Orange/red tones, cozy, inviting, emotional",
        "cool": "Blue/cyan tones, clinical, calm, professional",
        "rim_light": "Backlighting, edge highlighting, separates from background",
        "volumetric": "Rays of light through air, god rays, atmospheric",
        "neon": "Bright, saturated colors, glowing tubes, cyberpunk",
        "chiaroscuro": "Extreme contrast between light and dark, dramatic",
        "soft_diffuse": "No hard shadows, gentle, flattering, studio",
        "hard_direct": "Sharp shadows, directional, theatrical",
        "bioluminescent": "Self-glowing, organic light source, fantasy",
        "fluorescent": "Artificial, cool, clinical, commercial",
        "candlelight": "Warm, flickering, intimate, historical",
        "moonlight": "Cool blue, night, ethereal, atmospheric",
        "spotlight": "Directed beam, focused, dramatic highlighting",
    }

    COLOR_PALETTES = {
        # Color theory and psychology
        "monochromatic": "Single color variations, different shades and tints",
        "complementary": "Opposite colors on wheel, vibrant, high contrast",
        "analogous": "Adjacent colors on wheel, harmonious, cohesive",
        "triadic": "Three equally spaced colors, balanced, vibrant",
        "warm": "Reds, oranges, yellows, energetic, inviting, nostalgic",
        "cool": "Blues, cyans, purples, calm, peaceful, professional",
        "earth_tones": "Browns, ochres, siennas, natural, grounded",
        "pastel": "Soft, desaturated, gentle, dreamy, feminine",
        "vibrant": "Saturated, intense, energetic, eye-catching",
        "muted": "Desaturated, sophisticated, elegant, refined",
        "neon": "Bright, fluorescent, digital, synthwave, cyberpunk",
        "noir": "Black and white, high contrast, cinematic",
        "vintage": "Faded colors, aged appearance, historical",
        "gradient": "Smooth color transition, dynamic, modern",
        "iridescent": "Color-shifting, opalescent, magical, holographic",
    }

    ATMOSPHERE_DESCRIPTORS = {
        # Atmospheric qualities and moods
        "peaceful": "Calm, serene, tranquil, meditative",
        "tense": "Anxious, suspenseful, dramatic, uncertain",
        "mysterious": "Unknown, secretive, enigmatic, intriguing",
        "joyful": "Happy, cheerful, uplifting, celebratory",
        "melancholic": "Sad, nostalgic, reflective, bittersweet",
        "ethereal": "Heavenly, dreamlike, transcendent, otherworldly",
        "industrial": "Urban, mechanical, functional, man-made",
        "natural": "Organic, environmental, wilderness, untamed",
        "surreal": "Dream-like, illogical, impossible, fantastical",
        "chaotic": "Disordered, complex, dynamic, overwhelming",
        "precise": "Orderly, mathematical, controlled, systematic",
        "romantic": "Emotional, sensual, passionate, intimate",
        "apocalyptic": "End times, devastated, dark, post-apocalyptic",
        "utopian": "Perfect world, harmonious, optimistic, idealized",
        "gritty": "Rough, realistic, raw, unpolished, urban",
    }

    TEXTURE_DESCRIPTORS = {
        # Surface texture qualities
        "smooth": "Polished, refined, slick, no visible texture",
        "rough": "Unpolished, coarse, abrasive, weathered",
        "bumpy": "Uneven surface, protruding elements",
        "glossy": "Shiny, reflective, highly polished, lacquered",
        "matte": "Non-reflective, flat finish, light-absorbing",
        "metallic": "Mirror-like metal surface, highly reflective",
        "fabric": "Woven appearance, soft, textile quality",
        "leather": "Supple, organic grain, aged quality",
        "stone": "Carved, weathered, porous grain",
        "wood_grain": "Natural wood patterns, organic variations",
        "rusted": "Oxidized metal, aged, weathered, decaying",
        "crystalline": "Geometric structure, faceted, reflective",
        "granular": "Fine particles, sand-like, grainy",
        "organic": "Natural, biological patterns, irregular",
        "fractal": "Self-similar patterns, complex, infinite detail",
    }

    SIZE_SCALES = {
        # Scale terminology for 3D objects
        "microscopic": "Tiny, subatomic, requires magnification",
        "miniature": "Very small, collectible, detailed",
        "compact": "Small but functional, portable",
        "human_scale": "Comparable to human body, wearable",
        "monumental": "Massive, towering, architectural",
        "epic": "Extremely large, vast, overwhelming",
        "intimate": "Small, personal, detailed",
        "grand": "Large, impressive, spacious",
    }

    ACTION_VERBS = {
        # Action words for dynamic descriptions
        "moving": "Motion, velocity, direction, kinetic energy",
        "floating": "Weightless, hovering, defying gravity",
        "spinning": "Rotation, centrifugal force, dynamic",
        "exploding": "Burst, fragmentation, expansion, violent",
        "flowing": "Liquid motion, smooth transition, continuous",
        "cascading": "Waterfall effect, layered descent",
        "radiating": "Emanating outward, central energy source",
        "orbiting": "Circular motion, gravitational relationship",
        "collapsing": "Implosion, compression, density increase",
        "fragmenting": "Breaking apart, dispersal, dissolution",
    }

    CULTURAL_REFERENCES = {
        # Cultural and historical context
        "ancient_egypt": "Pyramids, hieroglyphics, pharaohs, scarabs, gold",
        "medieval_europe": "Castles, knights, heraldry, feudalism, gothic",
        "renaissance": "Classical revival, perspective, humanism, art",
        "victorian": "Industrial age, ornate, steam power, rigid morality",
        "art_nouveau": "Organic curves, nature motifs, decorative, early 1900s",
        "art_deco": "Geometric, luxury, streamline, 1920s-30s",
        "bauhaus": "Functional design, geometric, minimalist, experimental",
        "brutalism": "Raw concrete, monumental, honest materials, 1960s-70s",
        "postmodernism": "Irony, pastiche, historical references, playful",
        "cyberpunk": "High tech, low life, neon, dystopian future",
        "steampunk": "Steam power, Victorian, gears, alternative history",
        "art_decor": "Symmetrical, luxurious, geometric patterns, elegant",
        "mid_century": "Atomic age, space age, simple forms, authentic",
        "contemporary": "Current trends, mixed media, diverse influences",
    }

    QUALITY_DESCRIPTORS = {
        # Quality and detail levels
        "low_poly": "Minimal geometry, faceted appearance, video game style",
        "mid_poly": "Balanced detail, game-ready, efficient",
        "high_poly": "Detailed geometry, smooth surfaces, cinematic",
        "photorealistic": "Photographic accuracy, high detail, rendered",
        "stylized": "Artistic interpretation, exaggerated features",
        "cartoon": "Simplified, bold outlines, playful, animated",
        "abstract": "Non-representational, conceptual, simplified",
        "hyper_detailed": "Extreme detail, every element visible",
        "minimal": "Essential elements only, reductive",
    }

    EMOTION_ASSOCIATIONS = {
        # Emotional responses to visual elements
        "powerful": "Strength, dominance, confidence, authority",
        "fragile": "Delicate, vulnerable, intricate, precious",
        "elegant": "Refined, sophisticated, graceful, timeless",
        "playful": "Fun, whimsical, light-hearted, entertaining",
        "serious": "Formal, stern, professional, authoritative",
        "romantic": "Emotional, sensual, intimate, passionate",
        "aggressive": "Threatening, edgy, confrontational, dynamic",
        "peaceful": "Calm, soothing, serene, meditative",
        "exciting": "Energetic, thrilling, dynamic, adventurous",
        "ominous": "Threatening, dark, sinister, foreboding",
    }

    COMPOSITION_PRINCIPLES = {
        # Design and composition techniques
        "rule_of_thirds": "Dividing space into thirds, balanced composition",
        "golden_ratio": "1.618 proportion, naturally pleasing, mathematical",
        "symmetry": "Mirror image, balanced, formal, stable",
        "asymmetry": "Imbalanced, dynamic, informal, interesting",
        "depth": "Foreground, middle ground, background, layers",
        "negative_space": "Empty space, breathing room, clarity",
        "leading_lines": "Diagonal, curved, perspective lines guide eye",
        "focal_point": "Main subject, eye attraction, center of attention",
        "framing": "Border elements, contained composition, isolated",
        "contrast": "Difference between elements, visual interest",
    }

    # === SEMANTIC RELATIONSHIPS ===

    SEMANTIC_RELATIONSHIPS = {
        "opposite_of": {
            "small": "large",
            "bright": "dark",
            "smooth": "rough",
            "simple": "complex",
            "old": "new",
            "organic": "geometric",
        },
        "part_of": {
            "wheel": "vehicle",
            "button": "clothing",
            "beam": "building",
            "petal": "flower",
        },
        "similar_to": {
            "metal": ["aluminum", "copper", "steel"],
            "wood": ["oak", "pine", "walnut"],
            "fabric": ["cotton", "silk", "linen"],
        },
        "implies": {
            "ancient": ["weathered", "patina", "historical"],
            "futuristic": ["sleek", "technological", "minimalist"],
            "nature": ["organic", "flowing", "irregular"],
        }
    }

    # === ENHANCEMENT PROMPTS ===

    PROMPT_ENHANCERS = {
        "quality_boosters": [
            "high quality",
            "professionally rendered",
            "detailed",
            "intricate",
            "refined",
            "polished",
            "cinematic",
            "photorealistic",
            "4K resolution",
            "studio lighting",
        ],
        "style_enhancers": [
            "in the style of",
            "inspired by",
            "reminiscent of",
            "with elements of",
            "combining",
            "blending",
            "featuring",
            "characterized by",
        ],
        "emotional_enhancers": [
            "evokes",
            "conveys",
            "expresses",
            "radiates",
            "embodies",
            "captures",
            "reflects",
            "suggests",
        ],
        "technical_enhancers": [
            "with depth of field",
            "with volumetric lighting",
            "with ray tracing",
            "with subsurface scattering",
            "with ambient occlusion",
            "with physically accurate",
            "with PBR materials",
        ]
    }

    @staticmethod
    def get_style_enhancement(style: str) -> str:
        """Get enhanced description for a given style"""
        return BobAIKnowledgeBase.DESIGN_STYLES.get(style.lower(), style)

    @staticmethod
    def get_material_description(material: str) -> str:
        """Get detailed material properties"""
        return BobAIKnowledgeBase.MATERIAL_PROPERTIES.get(material.lower(), material)

    @staticmethod
    def get_lighting_mood(lighting: str) -> str:
        """Get lighting technique description"""
        return BobAIKnowledgeBase.LIGHTING_EFFECTS.get(lighting.lower(), lighting)

    @staticmethod
    def get_color_palette_description(palette: str) -> str:
        """Get color palette theory description"""
        return BobAIKnowledgeBase.COLOR_PALETTES.get(palette.lower(), palette)

    @staticmethod
    def enhance_prompt(user_prompt: str, style: str = None, quality: str = "high") -> str:
        """
        Enhance a user prompt with semantic knowledge

        Args:
            user_prompt: Original user input
            style: Design style to apply
            quality: Quality level (low, mid, high, photorealistic)

        Returns:
            Enhanced prompt with semantic enrichment
        """
        enhanced = user_prompt

        # Add quality enhancement
        if quality:
            enhanced += f", {quality} quality"

        # Add style enhancement
        if style and style in BobAIKnowledgeBase.DESIGN_STYLES:
            style_desc = BobAIKnowledgeBase.DESIGN_STYLES[style]
            enhanced += f", {style} style ({style_desc})"

        # Add technical enhancements
        enhanced += ", professionally rendered, studio lighting, detailed"

        return enhanced

    @staticmethod
    def get_all_dictionaries() -> Dict:
        """Get all available dictionaries for LLM context"""
        return {
            "design_styles": BobAIKnowledgeBase.DESIGN_STYLES,
            "materials": BobAIKnowledgeBase.MATERIAL_PROPERTIES,
            "lighting": BobAIKnowledgeBase.LIGHTING_EFFECTS,
            "colors": BobAIKnowledgeBase.COLOR_PALETTES,
            "atmosphere": BobAIKnowledgeBase.ATMOSPHERE_DESCRIPTORS,
            "textures": BobAIKnowledgeBase.TEXTURE_DESCRIPTORS,
            "scales": BobAIKnowledgeBase.SIZE_SCALES,
            "actions": BobAIKnowledgeBase.ACTION_VERBS,
            "culture": BobAIKnowledgeBase.CULTURAL_REFERENCES,
            "quality": BobAIKnowledgeBase.QUALITY_DESCRIPTORS,
            "emotions": BobAIKnowledgeBase.EMOTION_ASSOCIATIONS,
            "composition": BobAIKnowledgeBase.COMPOSITION_PRINCIPLES,
            "semantic": BobAIKnowledgeBase.SEMANTIC_RELATIONSHIPS,
        }


# === EXTERNAL KNOWLEDGE LIBRARIES ===

class WebSemanticLibraries:
    """Integration of open web semantic libraries"""

    WIKIPEDIA_CATEGORIES = {
        # Major Wikipedia category mappings
        "Animals": [
            "Mammals", "Birds", "Reptiles", "Fish", "Insects", "Arachnids",
            "Crustaceans", "Mollusks", "Amphibians"
        ],
        "Plants": [
            "Trees", "Flowers", "Herbs", "Grasses", "Ferns", "Mosses",
            "Fungi", "Algae", "Vegetables"
        ],
        "Architecture": [
            "Buildings", "Bridges", "Monuments", "Temples", "Castles",
            "Houses", "Skyscrapers", "Ancient structures"
        ],
        "Technology": [
            "Electronics", "Computers", "Robots", "Vehicles", "Spacecraft",
            "Weapons", "Machinery", "Tools"
        ],
        "Art": [
            "Paintings", "Sculptures", "Photography", "Digital art",
            "Abstract art", "Impressionism", "Surrealism", "Renaissance"
        ],
        "Nature": [
            "Landscapes", "Seascapes", "Mountains", "Forests", "Deserts",
            "Oceans", "Sky", "Weather phenomena"
        ],
    }

    WORDNET_CONCEPTS = {
        # WordNet semantic relationships
        "hypernym": "more general term",  # dog -> animal
        "hyponym": "more specific term",  # poodle -> dog
        "meronym": "component of",        # wheel -> car
        "holonym": "whole that part belongs to",  # car -> traffic
        "antonym": "opposite meaning",    # hot -> cold
        "synonym": "similar meaning",     # big -> large
    }

    DBPEDIA_ONTOLOGIES = {
        # DBpedia property mappings
        "Person": ["birthDate", "birthPlace", "deathDate", "occupation"],
        "Place": ["location", "area", "population", "elevation"],
        "Work": ["creator", "date", "subject", "type"],
        "Organization": ["founder", "location", "member", "industry"],
    }

    @staticmethod
    def get_semantic_context(term: str) -> Dict:
        """Get semantic context for a term from web libraries"""
        return {
            "term": term,
            "wikipedia_categories": WebSemanticLibraries.WIKIPEDIA_CATEGORIES,
            "wordnet": WebSemanticLibraries.WORDNET_CONCEPTS,
            "dbpedia": WebSemanticLibraries.DBPEDIA_ONTOLOGIES,
        }


# === WORLD KNOWLEDGE ENHANCEMENT ===

class WorldKnowledgeBase:
    """Comprehensive world knowledge for AI understanding"""

    GEOGRAPHICAL_KNOWLEDGE = {
        "continents": {
            "Africa": "Diverse climates, wildlife, ancient civilizations",
            "Asia": "Largest continent, varied cultures, ancient empires",
            "Europe": "Renaissance origins, historical influence, cultural centers",
            "North America": "Modern technology, diverse landscapes",
            "South America": "Amazon rainforest, Andes mountains, rich biodiversity",
            "Oceania": "Island nations, unique ecosystems, Aboriginal cultures",
            "Antarctica": "Frozen continent, research stations, penguins",
        },
        "biomes": {
            "tropical_rainforest": "Wet, dense vegetation, high biodiversity",
            "desert": "Arid, sparse vegetation, extreme temperatures",
            "savanna": "Grasslands, scattered trees, African wildlife",
            "temperate_forest": "Four seasons, mixed deciduous/coniferous",
            "tundra": "Frozen, low vegetation, polar regions",
            "ocean": "Saltwater, diverse marine life, vast",
        }
    }

    HISTORICAL_PERIODS = {
        "prehistoric": "Before written history, stone age to bronze age",
        "ancient": "Ancient Rome, Egypt, Greece, Mesopotamia",
        "medieval": "Middle Ages, feudalism, kingdoms, castles",
        "renaissance": "1300-1600, rebirth of classical learning",
        "enlightenment": "1600-1800, scientific revolution, reason",
        "industrial": "1760-1840, mechanization, factories, steam power",
        "modern": "1800s-1900s, technology, world wars, information age",
        "contemporary": "2000-present, digital age, globalization",
    }

    SCIENTIFIC_DOMAINS = {
        "physics": "Motion, forces, energy, matter, space-time",
        "chemistry": "Elements, reactions, bonding, states of matter",
        "biology": "Life, organisms, evolution, genetics, ecology",
        "astronomy": "Stars, planets, galaxies, cosmology, space",
        "geology": "Rocks, minerals, earth structure, plate tectonics",
        "meteorology": "Weather, atmosphere, climate patterns, storms",
        "botany": "Plants, photosynthesis, plant biology, ecosystems",
        "zoology": "Animals, behavior, anatomy, ecology, classification",
    }

    ARTISTIC_MOVEMENTS = {
        "impressionism": "Light, color, loose brushwork, natural scenes",
        "expressionism": "Emotion, distortion, vibrant colors, subjective",
        "cubism": "Geometric shapes, multiple perspectives, abstract",
        "surrealism": "Dreams, subconscious, irrational, fantastical",
        "abstractionism": "Non-representational, form, color, composition",
        "dadaism": "Anti-art, absurdity, chance, rebellion",
        "futurism": "Speed, motion, technology, aggression, dynamism",
        "constructivism": "Bold geometric, propaganda, social message",
        "minimalism": "Simplicity, essential forms, reduction",
        "pop_art": "Consumer culture, bright colors, mass production",
    }

    @staticmethod
    def get_historical_context(period: str) -> str:
        """Get historical context for a time period"""
        return WorldKnowledgeBase.HISTORICAL_PERIODS.get(period.lower(), period)


def initialize_bob_ai_knowledge():
    """Initialize and load all knowledge bases for Bob AI"""
    logger.info("[BOB-AI] Initializing comprehensive knowledge base...")

    kb = BobAIKnowledgeBase()
    dicts = kb.get_all_dictionaries()

    logger.info(f"[BOB-AI] Loaded {len(dicts)} semantic dictionaries")
    logger.info(f"[BOB-AI] Total knowledge entries: {sum(len(v) if isinstance(v, dict) else len(v.get('concept_map', [])) for v in dicts.values())}")
    logger.info("[BOB-AI] Knowledge base ready for LLM enhancement")

    return kb


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    kb = initialize_bob_ai_knowledge()

    # Example: Enhance a prompt
    prompt = "Create a beautiful ancient temple"
    enhanced = kb.enhance_prompt(prompt, style="gothic", quality="high")
    print(f"Original: {prompt}")
    print(f"Enhanced: {enhanced}")

    # Example: Get all dictionaries
    all_dicts = kb.get_all_dictionaries()
    print(f"\nAvailable dictionaries: {list(all_dicts.keys())}")
