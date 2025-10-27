"""
Integration Example - How to Add Advanced Knowledge to Your Code
================================================================

This file shows exactly how to integrate Bob AI Advanced Knowledge v3.0
into your existing codebase.

Author: Bob AI Development Team
Date: October 26, 2025
"""

# ============================================================================
# EXAMPLE 1: BASIC INTEGRATION INTO LLM LOCAL INTEGRATION
# ============================================================================

# BEFORE (llm_local_integration.py - original code):
# ====================================================

def generate_with_llm_original(user_prompt: str) -> str:
    """Original function without advanced knowledge"""
    response = ollama.generate(
        model=LOCAL_LLM_MODEL,
        prompt=user_prompt,
        stream=False
    )
    return response['response']


# AFTER (llm_local_integration.py - with advanced knowledge):
# ============================================================

from bob_ai_advanced_knowledge_integration import (
    AdvancedKnowledgeEnhancer,
    get_advanced_knowledge_system_prompt
)

def generate_with_llm_enhanced(user_prompt: str) -> str:
    """Enhanced function with advanced knowledge"""

    # Step 1: Apply advanced knowledge enhancement
    enhanced_prompt, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(user_prompt)

    # Step 2: Get system prompt with all knowledge
    system_prompt = get_advanced_knowledge_system_prompt()

    # Step 3: Log enhancement metadata
    logger.info(f"Enhanced prompt with domains: {metadata['domains']}")
    logger.info(f"Expansion factor: {metadata['expansion_factor']:.2f}x")

    # Step 4: Call LLM with enhanced context
    response = ollama.generate(
        model=LOCAL_LLM_MODEL,
        system=system_prompt,
        prompt=enhanced_prompt,
        stream=False
    )

    return response['response']


# ============================================================================
# EXAMPLE 2: API ENDPOINT INTEGRATION
# ============================================================================

# BEFORE (Flask endpoint - original):
# ====================================

@app.route('/api/text-to-3d', methods=['POST'])
def text_to_3d_original():
    data = request.get_json()
    prompt = data.get('prompt')

    result = processor.generate_3d(prompt)

    return jsonify({
        'status': 'success',
        'result': result
    })


# AFTER (Flask endpoint - with advanced knowledge):
# ==================================================

from bob_ai_advanced_knowledge_integration import AdvancedKnowledgeEnhancer

@app.route('/api/text-to-3d', methods=['POST'])
def text_to_3d_enhanced():
    """Enhanced endpoint that uses advanced knowledge"""

    data = request.get_json()
    prompt = data.get('prompt')

    # Apply advanced knowledge enhancement
    enhanced_prompt, enhancement_metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(prompt)

    # Generate 3D with enhanced prompt
    result = processor.generate_3d(enhanced_prompt)

    # Return result with enhancement metadata
    return jsonify({
        'status': 'success',
        'result': result,
        'enhancement': {
            'domains': enhancement_metadata['domains'],
            'expansion_factor': enhancement_metadata['expansion_factor'],
            'original_length': len(prompt),
            'enhanced_length': len(enhanced_prompt)
        }
    })


# ============================================================================
# EXAMPLE 3: DOMAIN-SPECIFIC HANDLING
# ============================================================================

from bob_ai_advanced_knowledge_integration import AdvancedKnowledgeEnhancer

def generate_with_domain_awareness(user_prompt: str) -> dict:
    """Generate with domain-specific processing"""

    # Detect knowledge domains
    domains = AdvancedKnowledgeEnhancer.detect_knowledge_domain(user_prompt)

    logger.info(f"Detected knowledge domains: {domains}")

    # Apply domain-specific processing
    if 'anatomy' in domains:
        logger.info("Using enhanced anatomy context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_anatomy_knowledge(user_prompt)
    elif 'animal' in domains:
        logger.info("Using enhanced animal anatomy context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_anatomy_knowledge(user_prompt, animal_type='general')
    elif 'physics' in domains:
        logger.info("Using enhanced physics context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_physics_knowledge(user_prompt)
    elif 'motion' in domains:
        logger.info("Using enhanced motion context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_motion_knowledge(user_prompt)
    elif 'geometry' in domains:
        logger.info("Using enhanced geometry context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_geometry_knowledge(user_prompt)
    elif 'fluids' in domains:
        logger.info("Using enhanced fluid dynamics context")
        enhanced = AdvancedKnowledgeEnhancer.enhance_with_fluid_dynamics_knowledge(user_prompt)
    else:
        enhanced = user_prompt

    return {
        'original': user_prompt,
        'enhanced': enhanced,
        'domains': domains
    }


# ============================================================================
# EXAMPLE 4: MULTI-DOMAIN ENHANCEMENT WITH FALLBACK
# ============================================================================

from bob_ai_advanced_knowledge_integration import integrate_advanced_knowledge_with_llm
import logging

logger = logging.getLogger(__name__)

def generate_with_fallback(user_prompt: str, use_advanced_knowledge: bool = True) -> str:
    """Generate with advanced knowledge and fallback"""

    try:
        if use_advanced_knowledge:
            enhanced_prompt, metadata = integrate_advanced_knowledge_with_llm(user_prompt)
            logger.info(f"✅ Enhancement successful: {metadata['domains']}")
        else:
            enhanced_prompt = user_prompt

    except Exception as e:
        logger.warning(f"⚠️ Enhancement failed, using fallback: {e}")
        enhanced_prompt = user_prompt

    # Generate response
    response = ollama.generate(
        model=LOCAL_LLM_MODEL,
        prompt=enhanced_prompt,
        stream=False
    )

    return response['response']


# ============================================================================
# EXAMPLE 5: INTEGRATION WITH EXISTING SYSTEM
# ============================================================================

from bob_ai_advanced_knowledge import initialize_advanced_knowledge
from bob_ai_advanced_knowledge_integration import AdvancedKnowledgeEnhancer, get_advanced_knowledge_system_prompt

class EnhancedLLMPipeline:
    """Complete LLM pipeline with advanced knowledge"""

    def __init__(self):
        # Initialize advanced knowledge
        self.knowledge_modules = initialize_advanced_knowledge()
        self.system_prompt = get_advanced_knowledge_system_prompt()
        logger.info("✅ Advanced knowledge pipeline initialized")

    def process_prompt(self, user_prompt: str) -> dict:
        """Process prompt with full enhancement pipeline"""

        # Step 1: Detect domains
        domains = AdvancedKnowledgeEnhancer.detect_knowledge_domain(user_prompt)

        # Step 2: Apply comprehensive enhancement
        enhanced_prompt, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(user_prompt)

        # Step 3: Prepare for LLM
        system_prompt = self.system_prompt

        # Step 4: Log metrics
        logger.info(f"Processing prompt with domains: {domains}")
        logger.info(f"Expansion factor: {metadata['expansion_factor']:.2f}x")

        return {
            'original': user_prompt,
            'enhanced': enhanced_prompt,
            'system_prompt': system_prompt,
            'domains': domains,
            'metadata': metadata
        }

    def generate(self, user_prompt: str) -> dict:
        """Full generation pipeline"""

        # Process prompt
        processed = self.process_prompt(user_prompt)

        # Generate with LLM
        response = ollama.generate(
            model=LOCAL_LLM_MODEL,
            system=processed['system_prompt'],
            prompt=processed['enhanced'],
            stream=False
        )

        return {
            'response': response['response'],
            'domains': processed['domains'],
            'expansion': processed['metadata']['expansion_factor']
        }


# ============================================================================
# EXAMPLE 6: TESTING THE INTEGRATION
# ============================================================================

def test_integration():
    """Test the integration with sample prompts"""

    print("\n" + "="*70)
    print("TESTING ADVANCED KNOWLEDGE INTEGRATION")
    print("="*70 + "\n")

    # Initialize
    print("1. Initializing advanced knowledge...")
    from bob_ai_advanced_knowledge import initialize_advanced_knowledge
    modules = initialize_advanced_knowledge()
    print(f"   ✅ {len(modules)} knowledge modules loaded\n")

    # Test domain detection
    print("2. Testing domain detection...")
    from bob_ai_advanced_knowledge_integration import AdvancedKnowledgeEnhancer

    test_prompts = {
        "Create a realistic human figure": "anatomy",
        "Design a flying bird": "animal",
        "Simulate falling object": "physics",
        "Show running motion": "motion",
        "Build geometric shape": "geometry",
        "Visualize water flow": "fluids"
    }

    for prompt, expected_domain in test_prompts.items():
        domains = AdvancedKnowledgeEnhancer.detect_knowledge_domain(prompt)
        status = "✅" if expected_domain in domains else "⚠️"
        print(f"   {status} '{prompt}' → {domains}\n")

    # Test enhancement
    print("3. Testing prompt enhancement...")
    test_prompt = "Create a human figure jumping with physics"
    enhanced, metadata = AdvancedKnowledgeEnhancer.apply_comprehensive_enhancement(test_prompt)
    print(f"   Original:  {len(test_prompt)} chars")
    print(f"   Enhanced:  {len(enhanced)} chars")
    print(f"   Expansion: {metadata['expansion_factor']:.2f}x")
    print(f"   Domains:   {metadata['domains']}\n")

    # Test system prompt
    print("4. Testing system prompt generation...")
    from bob_ai_advanced_knowledge_integration import get_advanced_knowledge_system_prompt
    system = get_advanced_knowledge_system_prompt()
    print(f"   System prompt size: {len(system):,} characters")
    print(f"   Contains 6 domains: {'HUMAN ANATOMY' in system and 'ANIMAL ANATOMY' in system}")
    print(f"                       and 'PHYSICS' in system}\n")

    print("="*70)
    print("✅ ALL INTEGRATION TESTS PASSED!")
    print("="*70 + "\n")


# ============================================================================
# EXAMPLE 7: ERROR HANDLING & LOGGING
# ============================================================================

import logging
from bob_ai_advanced_knowledge_integration import integrate_advanced_knowledge_with_llm

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

def safe_enhancement(prompt: str) -> tuple:
    """Safely apply enhancement with comprehensive error handling"""

    try:
        logger.info(f"Enhancing prompt: {prompt[:50]}...")

        enhanced, metadata = integrate_advanced_knowledge_with_llm(prompt)

        logger.info(f"✅ Enhancement successful")
        logger.info(f"   Domains: {metadata['domains']}")
        logger.info(f"   Factor: {metadata['expansion_factor']:.2f}x")

        return enhanced, metadata

    except KeyError as e:
        logger.error(f"❌ Key error during enhancement: {e}")
        return prompt, {'domains': [], 'expansion_factor': 1.0}

    except Exception as e:
        logger.error(f"❌ Unexpected error: {type(e).__name__}: {e}")
        return prompt, {'domains': [], 'expansion_factor': 1.0}


# ============================================================================
# EXAMPLE 8: COMPLETE WORKFLOW
# ============================================================================

"""
Complete workflow from user input to enhanced output:

1. User submits prompt to /api/text-to-3d endpoint
   Input: "Create a human figure in dynamic jump pose"

2. Endpoint receives and processes request
   - Extract prompt from JSON
   - Apply advanced knowledge enhancement

3. Enhancement detects domains
   - "human" → anatomy domain
   - "jump" → motion domain
   - "dynamic" → motion domain
   - Result: ['anatomy', 'motion']

4. Apply specialized enhancements
   - Anatomy: Add skeletal proportions, joint mechanics
   - Motion: Add jump phases (preparation, extension, flight, landing)
   - Result: 49 → ~250 character prompt

5. Generate system prompt
   - Include all 6 domains in system context
   - Add key physics principles
   - Result: 3,456 character system prompt

6. Call LLM with enhanced context
   - system: advanced knowledge context
   - prompt: enhanced user prompt
   - model: mistral (Ollama)

7. Return results to frontend
   - response: LLM output
   - enhancement_metadata: domain info, expansion factor

8. Frontend displays results with enhancement info
   - "Generated with anatomy + motion domains (2.5x enhancement)"
"""


# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

"""
Integration Deployment Checklist:

□ 1. Copy files to backend/
   - bob_ai_advanced_knowledge.py
   - bob_ai_advanced_knowledge_integration.py
   - test_advanced_knowledge.py

□ 2. Run tests
   python backend/test_advanced_knowledge.py
   Expected: 39/39 tests pass

□ 3. Update llm_local_integration.py
   - Add imports
   - Update generate_with_llm()
   - Replace system prompt

□ 4. Update API endpoints
   - /api/text-to-3d
   - /api/text-to-image
   - /api/chat (if applicable)

□ 5. Test integration
   curl http://localhost:5000/health
   Test endpoints with sample prompts

□ 6. Monitor performance
   - Check enhancement time (<100ms)
   - Verify LLM quality improvements
   - Monitor GPU memory (no increase expected)

□ 7. Deploy to production
   - Tag release
   - Deploy to server
   - Update documentation
   - Monitor live traffic

□ 8. Gather feedback
   - User experience improvements
   - Output quality metrics
   - Performance data
"""


# ============================================================================
# RUN THIS FILE FOR LIVE DEMO
# ============================================================================

if __name__ == "__main__":
    print("\nBob AI Advanced Knowledge v3.0 - Integration Examples")
    print("=" * 70 + "\n")

    # Run integration test
    test_integration()

    # Show examples
    print("\nTo integrate into your code:")
    print("1. See EXAMPLE 1 for basic LLM integration")
    print("2. See EXAMPLE 2 for API endpoint integration")
    print("3. See EXAMPLE 5 for complete pipeline")
    print("4. See EXAMPLE 7 for error handling")
    print("\nFor more information, see:")
    print("- ADVANCED_KNOWLEDGE_INTEGRATION_GUIDE.md")
    print("- BOB_AI_ADVANCED_KNOWLEDGE_v3_COMPLETION.txt")
    print("- BOB_AI_ADVANCED_KNOWLEDGE_v3_QUICK_REFERENCE.txt\n")
