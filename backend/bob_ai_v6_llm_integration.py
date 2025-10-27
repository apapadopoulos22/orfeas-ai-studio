"""
Bob AI v6.0 - LLM Pipeline Integration Module
==============================================

Integrates Bob AI v6.0 into the ORFEAS AI backend LLM pipeline.

This module provides seamless integration between:
- Flask REST API endpoints
- WebSocket event handlers
- Local LLM service (Ollama + Mistral)
- Bob AI knowledge enhancement system

Features:
- Automatic domain detection
- Multi-domain prompt enhancement
- System prompt injection
- Error handling and graceful degradation
- Performance optimization
- Comprehensive logging

Author: Bob AI Development Team
Date: October 26, 2025
Version: 6.0 Integration Module
"""

import logging
import json
from typing import Dict, Optional, Tuple, Any
from functools import wraps
import time

# Configure logging
logger = logging.getLogger(__name__)


class BobAILLMIntegration:
    """
    LLM Pipeline Integration for Bob AI v6.0

    This class handles integration with the ORFEAS AI LLM pipeline,
    providing automatic prompt enhancement and domain-aware response generation.
    """

    # Class-level cache for modules (lazy loading)
    _modules_cache = None
    _enhancer_cache = None

    @classmethod
    def get_knowledge_modules(cls):
        """Get or load knowledge modules (lazy loading)"""
        if cls._modules_cache is None:
            try:
                from bob_ai_v6_final_knowledge import GamesCombinedFinalIntegration
                cls._modules_cache = GamesCombinedFinalIntegration.initialize_all_final_knowledge()
                logger.info("✓ Bob AI v6.0 knowledge modules loaded")
            except ImportError as e:
                logger.error(f"Failed to load knowledge modules: {e}")
                cls._modules_cache = {}
        return cls._modules_cache

    @classmethod
    def get_enhancer(cls):
        """Get or initialize enhancer (lazy loading)"""
        if cls._enhancer_cache is None:
            try:
                from bob_ai_v6_integration import FinalComprehensiveEnhancer
                cls._enhancer_cache = FinalComprehensiveEnhancer
                logger.info("✓ Bob AI v6.0 enhancer initialized")
            except ImportError as e:
                logger.error(f"Failed to load enhancer: {e}")
                cls._enhancer_cache = None
        return cls._enhancer_cache

    @staticmethod
    def enhance_user_prompt(user_prompt: str, context: str = "general") -> Tuple[str, Dict]:
        """
        Enhance user prompt with Bob AI knowledge

        Args:
            user_prompt (str): Original user input
            context (str): Context type - "general", "3d_modeling", "design", "professional"

        Returns:
            Tuple[str, Dict]: (enhanced_prompt, metadata)
        """
        try:
            enhancer = BobAILLMIntegration.get_enhancer()
            if enhancer is None:
                logger.warning("Enhancer unavailable, returning original prompt")
                return user_prompt, {'status': 'enhancer_unavailable'}

            enhanced, metadata = enhancer.apply_final_enhancement(user_prompt)

            logger.info(f"Enhanced prompt: {metadata.get('domains_detected', [])}")
            return enhanced, metadata

        except Exception as e:
            logger.error(f"Prompt enhancement failed: {e}")
            return user_prompt, {'status': 'enhancement_error', 'error': str(e)}

    @staticmethod
    def get_system_prompt() -> str:
        """
        Get Bob AI v6.0 system prompt for LLM initialization

        Returns:
            str: Comprehensive system prompt (4,000+ characters)
        """
        try:
            enhancer = BobAILLMIntegration.get_enhancer()
            if enhancer is None:
                logger.warning("Enhancer unavailable, returning generic system prompt")
                return "You are Bob AI, a knowledgeable assistant with expertise across multiple domains."

            return enhancer.get_final_system_prompt()

        except Exception as e:
            logger.error(f"System prompt generation failed: {e}")
            return "You are Bob AI, a knowledgeable assistant with expertise across multiple domains."

    @staticmethod
    def integrate_with_llm(user_prompt: str, model: str = "mistral") -> Dict[str, Any]:
        """
        Complete LLM integration with enhancement

        Args:
            user_prompt (str): User's input prompt
            model (str): LLM model name (default: "mistral")

        Returns:
            Dict: {
                'status': 'success' or 'error',
                'original_prompt': str,
                'enhanced_prompt': str,
                'system_prompt': str,
                'metadata': dict,
                'domains_detected': list
            }
        """
        try:
            # Get enhancer
            enhancer = BobAILLMIntegration.get_enhancer()
            if enhancer is None:
                return {
                    'status': 'error',
                    'message': 'Bob AI enhancer unavailable',
                    'original_prompt': user_prompt
                }

            # Apply enhancement
            enhanced_prompt, metadata = enhancer.apply_final_enhancement(user_prompt)
            system_prompt = enhancer.get_final_system_prompt()

            logger.info(f"LLM integration: {metadata.get('domain_count', 0)} domains detected")

            return {
                'status': 'success',
                'original_prompt': user_prompt,
                'enhanced_prompt': enhanced_prompt,
                'system_prompt': system_prompt,
                'metadata': metadata,
                'domains_detected': metadata.get('domains_detected', []),
                'expansion_factor': metadata.get('expansion_factor', 1.0)
            }

        except Exception as e:
            logger.error(f"LLM integration failed: {e}")
            return {
                'status': 'error',
                'message': str(e),
                'original_prompt': user_prompt
            }


# ==================== FLASK INTEGRATION HELPERS ====================

def with_bob_ai_enhancement(func):
    """
    Decorator for Flask routes to automatically apply Bob AI enhancement

    Usage:
        @app.route('/api/endpoint', methods=['POST'])
        @with_bob_ai_enhancement
        def my_endpoint(enhanced_data):
            # enhanced_data contains 'original_prompt', 'enhanced_prompt', 'metadata'
            ...
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Get request data
        from flask import request
        data = request.get_json() or {}
        user_prompt = data.get('prompt', data.get('text', ''))

        if user_prompt:
            # Apply enhancement
            enhanced_prompt, metadata = BobAILLMIntegration.enhance_user_prompt(user_prompt)

            # Add enhanced data to request
            enhanced_data = {
                'original_prompt': user_prompt,
                'enhanced_prompt': enhanced_prompt,
                'metadata': metadata,
                'enhancement_applied': metadata.get('status') != 'enhancer_unavailable'
            }

            # Call function with enhanced data
            kwargs['enhanced_data'] = enhanced_data

        return func(*args, **kwargs)

    return wrapper


# ==================== WEBSOCKET INTEGRATION HELPERS ====================

class WebSocketBobAIHelper:
    """Helper for WebSocket integration with Bob AI"""

    @staticmethod
    def enhance_and_emit(socketio, event_name: str, user_prompt: str,
                        room: Optional[str] = None, **kwargs) -> Dict:
        """
        Enhance prompt and emit via WebSocket

        Args:
            socketio: Flask-SocketIO instance
            event_name (str): Event to emit
            user_prompt (str): User's prompt
            room (str, optional): Target room
            **kwargs: Additional data to include in emission

        Returns:
            Dict: Emission result
        """
        try:
            # Enhance prompt
            enhanced_prompt, metadata = BobAILLMIntegration.enhance_user_prompt(user_prompt)

            # Prepare emission data
            emission_data = {
                'original_prompt': user_prompt,
                'enhanced_prompt': enhanced_prompt,
                'metadata': metadata,
                'domains': metadata.get('domains_detected', []),
                **kwargs
            }

            # Emit
            socketio.emit(event_name, emission_data, room=room)

            logger.info(f"WebSocket emission: {event_name} with {len(metadata.get('domains_detected', []))} domains")

            return {
                'status': 'emitted',
                'event': event_name,
                'room': room
            }

        except Exception as e:
            logger.error(f"WebSocket emission failed: {e}")
            return {
                'status': 'error',
                'message': str(e)
            }


# ==================== EXAMPLE INTEGRATION CODE ====================

def example_flask_integration():
    """
    Example of integrating Bob AI v6.0 into Flask routes

    Add this to your Flask application:
    """

    example_code = """
    # In your Flask app (main.py or routes.py):

    from bob_ai_v6_llm_integration import (
        BobAILLMIntegration,
        with_bob_ai_enhancement,
        WebSocketBobAIHelper
    )
    from flask import jsonify, request
    from flask_socketio import emit


    # Example 1: REST API with automatic enhancement
    @app.route('/api/text-to-3d', methods=['POST'])
    @with_bob_ai_enhancement
    def text_to_3d(enhanced_data):
        '''Generate 3D from text with Bob AI enhancement'''

        original = enhanced_data['original_prompt']
        enhanced = enhanced_data['enhanced_prompt']
        metadata = enhanced_data['metadata']

        # Use enhanced prompt for 3D generation
        result = generate_3d_model(enhanced)

        return jsonify({
            'status': 'success',
            'original_prompt': original,
            'enhanced_prompt': enhanced,
            'domains': metadata.get('domains_detected', []),
            'result': result
        })


    # Example 2: Direct LLM integration
    @app.route('/api/generate-text', methods=['POST'])
    def generate_text():
        '''Generate text using Bob AI-enhanced prompts'''

        user_prompt = request.json.get('prompt')

        # Get enhanced prompt and system prompt
        integration_result = BobAILLMIntegration.integrate_with_llm(user_prompt)

        if integration_result['status'] != 'success':
            return jsonify(integration_result), 400

        # Call LLM with enhanced prompt
        from llm_local_integration import generate_with_llm

        llm_response = generate_with_llm(
            integration_result['enhanced_prompt'],
            system_context=integration_result['system_prompt']
        )

        return jsonify({
            'status': 'success',
            'original_prompt': user_prompt,
            'enhanced_prompt': integration_result['enhanced_prompt'],
            'domains_detected': integration_result['domains_detected'],
            'expansion_factor': integration_result['expansion_factor'],
            'response': llm_response
        })


    # Example 3: WebSocket with real-time enhancement
    @socketio.on('enhancement_request')
    def handle_enhancement_request(data):
        '''Real-time prompt enhancement via WebSocket'''

        user_prompt = data.get('prompt')
        session_id = data.get('session_id')

        # Enhance and emit
        WebSocketBobAIHelper.enhance_and_emit(
            socketio,
            event_name='enhancement_complete',
            user_prompt=user_prompt,
            room=session_id,
            session_id=session_id
        )


    # Example 4: Using system prompt in LLM calls
    @app.route('/api/creative-generation', methods=['POST'])
    def creative_generation():
        '''Generate creative content with Bob AI knowledge'''

        from llm_local_integration import generate_with_llm

        user_prompt = request.json.get('prompt')

        # Get Bob AI system prompt
        system_prompt = BobAILLMIntegration.get_system_prompt()

        # Enhance user prompt
        enhanced_prompt, metadata = BobAILLMIntegration.enhance_user_prompt(user_prompt)

        # Call LLM with both system and enhanced prompt
        response = generate_with_llm(enhanced_prompt)

        return jsonify({
            'status': 'success',
            'original': user_prompt,
            'enhanced': enhanced_prompt,
            'domains': metadata.get('domains_detected', []),
            'response': response
        })
    """

    return example_code


def get_integration_checklist():
    """Get integration checklist for deploying v6.0"""

    checklist = """
    BOB AI v6.0 - INTEGRATION CHECKLIST
    ===================================

    STEP 1: Copy Files to Backend
    [ ] Copy bob_ai_v6_final_knowledge.py to backend/
    [ ] Copy bob_ai_v6_integration.py to backend/
    [ ] Copy bob_ai_v6_llm_integration.py to backend/
    [ ] Copy bob_ai_v6_integration_and_testing_suite.py to backend/

    STEP 2: Verify Imports
    [ ] Run: python -c "from bob_ai_v6_final_knowledge import *"
    [ ] Run: python -c "from bob_ai_v6_integration import *"
    [ ] Run: python -c "from bob_ai_v6_llm_integration import *"
    [ ] No import errors

    STEP 3: Run Tests
    [ ] Run: python backend/test_bob_ai_v6_final.py
    [ ] Verify: 51/51 tests passing
    [ ] Run: python backend/bob_ai_v6_integration_and_testing_suite.py
    [ ] Verify: All integration tests passing

    STEP 4: Update Flask Application
    [ ] Import BobAILLMIntegration in main.py
    [ ] Add @with_bob_ai_enhancement decorator to relevant routes
    [ ] Test manual API calls
    [ ] Verify enhancement in logs

    STEP 5: Update WebSocket Handlers
    [ ] Import WebSocketBobAIHelper in main.py
    [ ] Add enhancement to WebSocket event handlers
    [ ] Test real-time enhancement

    STEP 6: Performance Validation
    [ ] Measure prompt enhancement time (<100ms)
    [ ] Measure system prompt generation (<50ms)
    [ ] Verify no memory leaks
    [ ] Monitor CPU/GPU usage

    STEP 7: End-to-End Testing
    [ ] Test text-to-3D with enhancement
    [ ] Test text-to-image with enhancement
    [ ] Test WebSocket real-time enhancement
    [ ] Verify quality improvements

    STEP 8: Production Deployment
    [ ] Backup current configuration
    [ ] Deploy new modules
    [ ] Restart backend service
    [ ] Monitor error logs
    [ ] Verify all endpoints working
    [ ] Gather initial user feedback

    STEP 9: Monitor & Optimize
    [ ] Track domain detection accuracy
    [ ] Monitor performance metrics
    [ ] Collect user feedback
    [ ] Optimize keyword list if needed
    [ ] Plan Phase 2 improvements
    """

    return checklist


if __name__ == "__main__":
    print(get_integration_checklist())
    print("\n\nExample Flask Integration:")
    print("=" * 80)
    print(example_flask_integration())
