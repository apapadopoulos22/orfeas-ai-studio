"""
Local LLM Integration - Ollama Support
=====================================
Handles integration with local Ollama LLM service for:
- Text-to-Image generation (Stable Diffusion)
- Text enhancement and processing
- Automatic startup and health checks

Author: ORFEAS AI
Date: 2025-10-26
"""

import os
import sys
import time
import subprocess
import threading
import requests
import logging
from typing import Dict, Optional, Tuple
from pathlib import Path

# Import Bob AI Knowledge Base
try:
    from bob_ai_knowledge_base import (
        BobAIKnowledgeBase,
        WebSemanticLibraries,
        WorldKnowledgeBase,
        initialize_bob_ai_knowledge
    )
    BOB_AI_KB_AVAILABLE = True
except ImportError:
    BOB_AI_KB_AVAILABLE = False

logger = logging.getLogger(__name__)

# Warn if KB not available
if not BOB_AI_KB_AVAILABLE:
    logger.warning("[LLM] Bob AI Knowledge Base not available, running without semantic enhancement")


class OllamaManager:
    """Manages local Ollama LLM service"""

    def __init__(self):
        self.endpoint = os.getenv('LOCAL_LLM_ENDPOINT', 'http://localhost:11434')
        self.model = os.getenv('LOCAL_LLM_MODEL', 'mistral')
        self.enabled = os.getenv('LOCAL_LLM_ENABLED', 'true').lower() == 'true'
        self.auto_start = os.getenv('LOCAL_LLM_AUTO_START', 'true').lower() == 'true'
        self.process = None
        self.is_running = False
        self.startup_timeout = int(os.getenv('LOCAL_LLM_STARTUP_TIMEOUT', '60'))

    def start_ollama(self) -> bool:
        """
        Start Ollama service automatically

        Returns:
            bool: True if started successfully, False otherwise
        """
        if not self.enabled or not self.auto_start:
            logger.info("[LLM] Ollama auto-start disabled")
            return True

        logger.info("[LLM] Attempting to start Ollama service...")

        # Check if already running
        if self.is_ollama_running():
            logger.info("[LLM] ✓ Ollama already running")
            self.is_running = True
            return True

        try:
            # Detect OS and start appropriate command
            if sys.platform == 'win32':
                # Windows - try to launch Ollama
                try:
                    # Try to find Ollama in common Windows locations
                    ollama_paths = [
                        r'C:\Program Files\Ollama\ollama.exe',
                        r'C:\Program Files (x86)\Ollama\ollama.exe',
                        os.path.expanduser(r'~\AppData\Local\Programs\Ollama\ollama.exe'),
                    ]

                    ollama_exe = None
                    for path in ollama_paths:
                        if os.path.exists(path):
                            ollama_exe = path
                            break

                    if ollama_exe:
                        logger.info(f"[LLM] Found Ollama at: {ollama_exe}")
                        # Start Ollama in background
                        self.process = subprocess.Popen(
                            [ollama_exe, 'serve'],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.CREATE_NEW_PROCESS_GROUP
                        )
                        logger.info(f"[LLM] Started Ollama process (PID: {self.process.pid})")
                    else:
                        logger.warning("[LLM] Ollama executable not found in common locations")
                        logger.warning("[LLM] Please install Ollama from https://ollama.ai")
                        return False
                except Exception as e:
                    logger.error(f"[LLM] Failed to start Ollama on Windows: {e}")
                    return False

            elif sys.platform.startswith('linux'):
                # Linux - try to start ollama service
                try:
                    # Try systemctl first
                    subprocess.run(['systemctl', 'start', 'ollama'], check=False)
                    logger.info("[LLM] Started Ollama using systemctl")
                except:
                    # Fallback to direct execution
                    self.process = subprocess.Popen(
                        ['ollama', 'serve'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    logger.info(f"[LLM] Started Ollama process (PID: {self.process.pid})")

            elif sys.platform == 'darwin':
                # macOS - try to start ollama service
                try:
                    self.process = subprocess.Popen(
                        ['ollama', 'serve'],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL
                    )
                    logger.info(f"[LLM] Started Ollama process (PID: {self.process.pid})")
                except Exception as e:
                    logger.error(f"[LLM] Failed to start Ollama on macOS: {e}")
                    return False

            # Wait for Ollama to start and become available
            logger.info(f"[LLM] Waiting for Ollama to be ready (timeout: {self.startup_timeout}s)...")
            start_time = time.time()

            while time.time() - start_time < self.startup_timeout:
                if self.is_ollama_running():
                    logger.info("[LLM] ✓ Ollama is ready!")
                    self.is_running = True

                    # Pull the model if not already present
                    if not self.is_model_available():
                        logger.info(f"[LLM] Pulling model '{self.model}'...")
                        self.pull_model()

                    return True

                time.sleep(1)

            logger.error(f"[LLM] Ollama failed to start within {self.startup_timeout} seconds")
            return False

        except Exception as e:
            logger.error(f"[LLM] Error starting Ollama: {e}", exc_info=True)
            return False

    def is_ollama_running(self) -> bool:
        """
        Check if Ollama service is running

        Returns:
            bool: True if running, False otherwise
        """
        try:
            response = requests.get(f'{self.endpoint}/api/tags', timeout=5)
            return response.status_code == 200
        except:
            return False

    def is_model_available(self) -> bool:
        """
        Check if the specified model is available locally

        Returns:
            bool: True if model is available, False otherwise
        """
        try:
            response = requests.get(f'{self.endpoint}/api/tags', timeout=5)
            if response.status_code == 200:
                data = response.json()
                models = data.get('models', [])
                model_names = [m.get('name', '') for m in models]

                # Check if model or model:latest exists
                return any(
                    self.model in name or name.startswith(f'{self.model}:')
                    for name in model_names
                )
            return False
        except:
            return False

    def pull_model(self) -> bool:
        """
        Pull the specified model from Ollama registry

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info(f"[LLM] Pulling model '{self.model}' from Ollama...")
            response = requests.post(
                f'{self.endpoint}/api/pull',
                json={'name': self.model},
                timeout=300  # 5 minute timeout for model download
            )

            if response.status_code in [200, 201]:
                logger.info(f"[LLM] ✓ Model '{self.model}' pulled successfully")
                return True
            else:
                logger.error(f"[LLM] Failed to pull model: {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"[LLM] Error pulling model: {e}")
            return False

    def health_check(self) -> Tuple[bool, str]:
        """
        Perform comprehensive health check

        Returns:
            Tuple[bool, str]: (is_healthy, status_message)
        """
        if not self.enabled:
            return True, "Local LLM disabled"

        # Check if Ollama is running
        if not self.is_ollama_running():
            return False, "Ollama service not responding"

        # Check if model is available
        if not self.is_model_available():
            return False, f"Model '{self.model}' not available"

        return True, "Ollama and model ready"

    def stop_ollama(self):
        """Stop Ollama service"""
        if self.process:
            try:
                logger.info("[LLM] Stopping Ollama process...")
                if sys.platform == 'win32':
                    # Windows process termination
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()
                else:
                    # Unix process termination
                    self.process.terminate()
                    try:
                        self.process.wait(timeout=5)
                    except subprocess.TimeoutExpired:
                        self.process.kill()

                self.is_running = False
                logger.info("[LLM] Ollama process stopped")
            except Exception as e:
                logger.error(f"[LLM] Error stopping Ollama: {e}")

    def __del__(self):
        """Cleanup on deletion"""
        if self.process:
            self.stop_ollama()


# Global manager instance
_ollama_manager: Optional[OllamaManager] = None


def get_ollama_manager() -> OllamaManager:
    """Get or create the global Ollama manager instance"""
    global _ollama_manager
    if _ollama_manager is None:
        _ollama_manager = OllamaManager()
    return _ollama_manager


def initialize_local_llm() -> Dict[str, any]:
    """
    Initialize local LLM (Ollama)

    Returns:
        Dict with initialization status and results
    """
    logger.info("=" * 80)
    logger.info("[LLM] INITIALIZING LOCAL LLM (OLLAMA)")
    logger.info("=" * 80)

    manager = get_ollama_manager()

    if not manager.enabled:
        logger.info("[LLM] Local LLM disabled in configuration")
        return {
            'enabled': False,
            'status': 'disabled',
            'message': 'Local LLM disabled'
        }

    # Start Ollama if auto-start enabled
    if manager.auto_start:
        success = manager.start_ollama()
        if not success:
            logger.warning("[LLM] Failed to start Ollama automatically")
            return {
                'enabled': True,
                'auto_start': True,
                'status': 'failed',
                'message': 'Failed to start Ollama service'
            }
    else:
        # Just check if it's running
        if not manager.is_ollama_running():
            logger.warning("[LLM] Ollama not running and auto-start disabled")
            return {
                'enabled': True,
                'auto_start': False,
                'status': 'not_running',
                'message': 'Ollama service not running'
            }

    # Perform health check
    is_healthy, message = manager.health_check()

    if is_healthy:
        logger.info("[LLM] ✓ Local LLM initialized successfully")
        logger.info(f"[LLM]   Endpoint: {manager.endpoint}")
        logger.info(f"[LLM]   Model: {manager.model}")
        logger.info("=" * 80)

        return {
            'enabled': True,
            'status': 'ready',
            'endpoint': manager.endpoint,
            'model': manager.model,
            'message': 'Local LLM ready'
        }
    else:
        logger.error(f"[LLM] Health check failed: {message}")
        return {
            'enabled': True,
            'status': 'error',
            'message': message
        }


def enhance_prompt_with_bob_ai(user_prompt: str, context: str = "general") -> str:
    """
    Enhance user prompt with Bob AI semantic knowledge

    Args:
        user_prompt: Original user input
        context: Context type (design, 3d_modeling, general, etc.)

    Returns:
        Enhanced prompt with semantic context
    """
    if not BOB_AI_KB_AVAILABLE:
        logger.debug("[LLM] Bob AI Knowledge Base not available, returning original prompt")
        return user_prompt

    try:
        # Determine quality level based on context
        quality = "high" if context in ["3d_modeling", "professional"] else "medium"

        # Determine style if provided in prompt
        style = None
        for design_style in BobAIKnowledgeBase.DESIGN_STYLES.keys():
            if design_style.lower() in user_prompt.lower():
                style = design_style
                break

        # Enhance the prompt with semantic knowledge
        enhanced = BobAIKnowledgeBase.enhance_prompt(user_prompt, style=style, quality=quality)
        logger.debug(f"[LLM] Prompt enhanced with semantic knowledge (length: {len(enhanced)} chars)")
        return enhanced

    except Exception as e:
        logger.warning(f"[LLM] Error enhancing prompt: {e}, using original")
        return user_prompt


def get_bob_ai_system_prompt() -> str:
    """
    Generate system prompt with Bob AI knowledge context

    Returns:
        System prompt with semantic knowledge dictionaries
    """
    if not BOB_AI_KB_AVAILABLE:
        return "You are Bob AI, a creative and helpful assistant."

    try:
        # Get all semantic dictionaries
        all_dicts = BobAIKnowledgeBase.get_all_dictionaries()

        # Build system prompt with knowledge context
        system_prompt = """You are Bob AI, an advanced AI assistant with comprehensive world knowledge.

You have deep expertise in:
- Visual Design: Familiar with 15+ design styles (minimalist, steampunk, cyberpunk, gothic, art deco, futurism, maximalism, brutalism, etc.)
- Materials & Textures: Understand properties of 15+ materials (metal, wood, ceramic, glass, stone, fabric, plastic, rubber, concrete, ice, liquid, crystal, etc.)
- Lighting Techniques: Master 15+ lighting effects (ambient, dramatic, neon, volumetric, rim lighting, backlighting, etc.)
- Color Theory: Skilled in 15+ color palettes (monochromatic, complementary, analogous, triadic, gradient, etc.)
- Atmosphere & Mood: Can convey 15+ atmospheric descriptors (peaceful, mysterious, ethereal, chaotic, elegant, etc.)
- Cultural References: Knowledgeable about historical periods and artistic movements
- Composition: Expert in composition principles (rule of thirds, leading lines, depth, symmetry, etc.)

When responding to creative requests:
1. Identify the style, mood, and quality level intended
2. Use specific terminology from your knowledge base
3. Provide detailed, vivid descriptions
4. Reference materials, lighting, and composition principles
5. Consider cultural and historical context

Your responses are detailed, imaginative, and technically informed."""

        return system_prompt

    except Exception as e:
        logger.warning(f"[LLM] Error generating Bob AI system prompt: {e}")
        return "You are Bob AI, a creative and helpful assistant."


def generate_with_llm(prompt: str, model: Optional[str] = None, use_semantic_enhancement: bool = True) -> Optional[Dict]:
    """
    Generate response from local LLM with optional semantic enhancement

    Args:
        prompt: Text prompt for generation
        model: Optional model name (defaults to configured model)
        use_semantic_enhancement: Whether to enhance prompt with Bob AI knowledge

    Returns:
        Dict with generated response or None on error
    """
    manager = get_ollama_manager()

    if not manager.enabled or not manager.is_ollama_running():
        logger.error("[LLM] Ollama service not available")
        return None

    model_name = model or manager.model

    try:
        # Enhance prompt with Bob AI semantic knowledge if available and enabled
        enhanced_prompt = prompt
        system_prompt = get_bob_ai_system_prompt()

        if use_semantic_enhancement and BOB_AI_KB_AVAILABLE:
            enhanced_prompt = enhance_prompt_with_bob_ai(prompt, context="general")
            logger.debug(f"[LLM] Using enhanced prompt for generation")

        # Build the full request with system context
        request_payload = {
            'model': model_name,
            'prompt': enhanced_prompt,
            'stream': False
        }

        # Add system context if available
        if system_prompt:
            request_payload['system'] = system_prompt

        response = requests.post(
            f'{manager.endpoint}/api/generate',
            json=request_payload,
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            logger.info(f"[LLM] Generation successful - model: {model_name}")
            return result
        else:
            logger.error(f"[LLM] Generation failed: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"[LLM] Error generating with LLM: {e}")
        return None


# Shutdown handler for cleanup
def shutdown_local_llm():
    """Shutdown local LLM on server shutdown"""
    global _ollama_manager
    if _ollama_manager:
        _ollama_manager.stop_ollama()
        logger.info("[LLM] Local LLM shutdown complete")


# ============================================================================
# Module Exports - Semantic Enhancement API
# ============================================================================
__all__ = [
    'OllamaManager',
    'get_ollama_manager',
    'initialize_local_llm',
    'generate_with_llm',
    'enhance_prompt_with_bob_ai',
    'get_bob_ai_system_prompt',
    'shutdown_local_llm',
    'BOB_AI_KB_AVAILABLE',
]

# Initialize Bob AI Knowledge Base if available
if BOB_AI_KB_AVAILABLE:
    try:
        initialize_bob_ai_knowledge()
        logger.info("[LLM] ✓ Bob AI Knowledge Base initialized")
    except Exception as e:
        logger.warning(f"[LLM] Warning initializing Bob AI KB: {e}")
