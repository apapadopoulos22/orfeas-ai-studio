"""
ORFEAS AI 2D→3D Studio - Enterprise LLM Integration
==================================================
ORFEAS AI

Enterprise-grade Large Language Model orchestration and management for the ORFEAS platform.
Provides intelligent model selection, multi-LLM coordination, and context-aware processing.
"""

import asyncio
import hashlib
import json
import logging
import time
from typing import Dict, List, Any, Optional, Union
import openai
import anthropic
import google.generativeai as genai
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
from dataclasses import dataclass
from datetime import datetime
import os
from config import Config

logger = logging.getLogger(__name__)

@dataclass
class LLMRequest:
    """Structure for LLM requests"""
    prompt: str
    context: Dict[str, Any]
    task_type: str
    priority: str = "normal"
    max_tokens: int = 2000
    temperature: float = 0.3
    model_override: Optional[str] = None

@dataclass
class LLMResponse:
    """Structure for LLM responses"""
    content: str
    model_used: str
    processing_time: float
    token_count: int
    confidence_score: float
    metadata: Dict[str, Any]

class EnterpriseLLMManager:
    """
    Enterprise-grade Large Language Model integration and orchestration
    """

    def __init__(self):
        self.config = Config()
        self.context_manager = None  # Will be injected
        self.active_models = {
            'gpt4_turbo': None,
            'claude_3_5_sonnet': None,
            'gemini_ultra': None,
            'llama_3_1_405b': None,
            'mistral_8x22b': None,
            'deepseek_coder': None
        }
        self.model_capabilities = self.load_model_capabilities()
        self.performance_metrics = {}
        self.rate_limiters = {}
        self.initialize_clients()

    def initialize_clients(self):
        """Initialize API clients for all LLM providers"""
        try:
            # OpenAI (GPT-4 Turbo, GPT-4o)
            if os.getenv('OPENAI_API_KEY'):
                openai.api_key = os.getenv('OPENAI_API_KEY')
                self.active_models['gpt4_turbo'] = 'gpt-4-turbo'
                logger.info("[ORFEAS-LLM] OpenAI GPT-4 Turbo initialized")

            # Anthropic (Claude 3.5 Sonnet)
            if os.getenv('ANTHROPIC_API_KEY'):
                self.anthropic_client = anthropic.Anthropic(
                    api_key=os.getenv('ANTHROPIC_API_KEY')
                )
                self.active_models['claude_3_5_sonnet'] = 'claude-3-5-sonnet-20241022'
                logger.info("[ORFEAS-LLM] Anthropic Claude 3.5 Sonnet initialized")

            # Google (Gemini Ultra)
            if os.getenv('GOOGLE_API_KEY'):
                genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
                self.active_models['gemini_ultra'] = 'gemini-pro'
                logger.info("[ORFEAS-LLM] Google Gemini Ultra initialized")

            # Local models (LLaMA, Mistral, etc.)
            self.initialize_local_models()

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Failed to initialize LLM clients: {e}")

    def initialize_local_models(self):
        """Initialize local/open-source models"""
        try:
            device = "cuda" if torch.cuda.is_available() else "cpu"

            # Check if we have enough VRAM for local models
            if torch.cuda.is_available():
                total_memory = torch.cuda.get_device_properties(0).total_memory
                available_memory = total_memory - torch.cuda.memory_allocated(0)

                # Only load local models if we have sufficient VRAM (>16GB available)
                if available_memory > 16 * 1024**3:  # 16GB
                    # These would be loaded on demand to save memory
                    self.active_models['llama_3_1_405b'] = 'meta-llama/Llama-3.1-405B-Instruct'
                    self.active_models['mistral_8x22b'] = 'mistralai/Mixtral-8x22B-Instruct-v0.1'
                    logger.info("[ORFEAS-LLM] Local model support enabled")
                else:
                    logger.warning("[ORFEAS-LLM] Insufficient VRAM for local models, using API-only")

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Failed to initialize local models: {e}")

    def load_model_capabilities(self) -> Dict[str, Dict]:
        """Load model capabilities and specializations"""
        return {
            'gpt4_turbo': {
                'strengths': ['reasoning', 'code_generation', 'analysis', 'multimodal'],
                'speed': 'medium',
                'context_window': 128000,
                'best_for': ['complex_reasoning', 'code_review', 'technical_analysis']
            },
            'claude_3_5_sonnet': {
                'strengths': ['writing', 'analysis', 'code_generation', 'safety'],
                'speed': 'fast',
                'context_window': 200000,
                'best_for': ['content_creation', 'code_writing', 'creative_tasks']
            },
            'gemini_ultra': {
                'strengths': ['multimodal', 'reasoning', 'math', 'science'],
                'speed': 'medium',
                'context_window': 32000,
                'best_for': ['multimodal_tasks', 'scientific_analysis', 'math_problems']
            },
            'llama_3_1_405b': {
                'strengths': ['general_purpose', 'reasoning', 'code'],
                'speed': 'slow',
                'context_window': 128000,
                'best_for': ['offline_processing', 'privacy_sensitive']
            },
            'mistral_8x22b': {
                'strengths': ['efficiency', 'code', 'multilingual'],
                'speed': 'fast',
                'context_window': 32000,
                'best_for': ['real_time_chat', 'code_completion', 'multilingual']
            },
            'deepseek_coder': {
                'strengths': ['code_generation', 'debugging', 'code_analysis'],
                'speed': 'fast',
                'context_window': 16000,
                'best_for': ['code_debugging', 'code_generation', 'code_review']
            }
        }

    def select_optimal_llm(self, request: LLMRequest) -> str:
        """Select best LLM based on task requirements and context"""

        task_type = request.task_type
        context = request.context
        priority = request.priority

        # Override if specified
        if request.model_override and request.model_override in self.active_models:
            return request.model_override

        # Task-specific model selection
        if task_type == 'code_generation':
            if context.get('complexity_score', 0.5) > 0.8:
                return 'gpt4_turbo'  # Best for complex coding tasks
            elif context.get('language') == 'python' and 'debug' in request.prompt.lower():
                return 'deepseek_coder'  # Specialized for code debugging
            else:
                return 'claude_3_5_sonnet'  # Fast and accurate for standard code

        elif task_type == 'reasoning_analysis':
            return 'gpt4_turbo'  # Superior reasoning capabilities

        elif task_type == 'content_creation':
            return 'claude_3_5_sonnet'  # Excellent creative writing

        elif task_type == 'multimodal_understanding':
            return 'gemini_ultra'  # Best multimodal capabilities

        elif task_type == 'real_time_chat':
            max_latency = context.get('max_latency_ms', 5000)
            if max_latency < 1000:  # < 1 second
                return 'mistral_8x22b'  # Fastest response time
            else:
                return 'claude_3_5_sonnet'

        elif task_type == 'privacy_sensitive':
            # Prefer local models for sensitive data
            if self.active_models.get('llama_3_1_405b'):
                return 'llama_3_1_405b'
            else:
                return 'claude_3_5_sonnet'  # Anthropic has good privacy practices

        else:  # General purpose
            # Consider priority and system load
            if priority == 'high':
                return 'gpt4_turbo'  # Best quality for high priority
            elif priority == 'low' or context.get('system_load', 0) > 0.8:
                return 'mistral_8x22b'  # Faster for low priority or high load
            else:
                return 'claude_3_5_sonnet'  # Balanced choice

    async def process_with_llm(self, request: LLMRequest) -> LLMResponse:
        """Process request with optimal LLM selection and context awareness"""

        start_time = time.time()

        # Build comprehensive context if context manager is available
        if self.context_manager:
            processing_context = self.context_manager.build_llm_context(request.context)
        else:
            processing_context = request.context

        # Select optimal model
        selected_model = self.select_optimal_llm(request)

        # Apply context-aware prompt enhancement
        enhanced_prompt = self.enhance_prompt_with_context(request.prompt, processing_context)

        try:
            # Execute with selected LLM
            result = await self.execute_llm_request(
                model=selected_model,
                prompt=enhanced_prompt,
                request=request,
                context=processing_context
            )

            processing_time = time.time() - start_time

            # Create response
            response = LLMResponse(
                content=result['content'],
                model_used=selected_model,
                processing_time=processing_time,
                token_count=result.get('token_count', 0),
                confidence_score=result.get('confidence_score', 0.85),
                metadata={
                    'task_type': request.task_type,
                    'context_used': bool(self.context_manager),
                    'prompt_enhanced': enhanced_prompt != request.prompt,
                    'api_response_time': result.get('api_response_time', 0)
                }
            )

            # Update model performance metrics
            self.update_model_performance(selected_model, response, processing_context)

            return response

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Primary model {selected_model} failed: {e}")
            # Intelligent fallback to alternative models
            return await self.fallback_llm_processing(request, processing_context, failed_model=selected_model)

    async def execute_llm_request(self, model: str, prompt: str, request: LLMRequest, context: Dict) -> Dict:
        """Execute request with specific LLM"""

        if model == 'gpt4_turbo':
            return await self.execute_openai_request(prompt, request)
        elif model == 'claude_3_5_sonnet':
            return await self.execute_anthropic_request(prompt, request)
        elif model == 'gemini_ultra':
            return await self.execute_google_request(prompt, request)
        elif model in ['llama_3_1_405b', 'mistral_8x22b']:
            return await self.execute_local_model_request(model, prompt, request)
        elif model == 'deepseek_coder':
            return await self.execute_deepseek_request(prompt, request)
        else:
            raise ValueError(f"Unknown model: {model}")

    async def execute_openai_request(self, prompt: str, request: LLMRequest) -> Dict:
        """Execute OpenAI GPT-4 request"""
        try:
            response = await openai.ChatCompletion.acreate(
                model="gpt-4-turbo",
                messages=[
                    {"role": "system", "content": "You are ORFEAS AI, an expert assistant for 3D modeling, AI, and enterprise software development."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=request.max_tokens,
                temperature=request.temperature
            )

            return {
                'content': response.choices[0].message.content,
                'token_count': response.usage.total_tokens,
                'confidence_score': 0.9,  # GPT-4 generally high confidence
                'api_response_time': response.response_ms / 1000 if hasattr(response, 'response_ms') else 0
            }

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] OpenAI request failed: {e}")
            raise

    async def execute_anthropic_request(self, prompt: str, request: LLMRequest) -> Dict:
        """Execute Anthropic Claude request"""
        try:
            message = await self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=request.max_tokens,
                temperature=request.temperature,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return {
                'content': message.content[0].text,
                'token_count': message.usage.input_tokens + message.usage.output_tokens,
                'confidence_score': 0.88,  # Claude typically high quality
                'api_response_time': 0  # Anthropic doesn't provide timing
            }

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Anthropic request failed: {e}")
            raise

    async def execute_google_request(self, prompt: str, request: LLMRequest) -> Dict:
        """Execute Google Gemini request"""
        try:
            model = genai.GenerativeModel('gemini-pro')
            response = await model.generate_content_async(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=request.max_tokens,
                    temperature=request.temperature
                )
            )

            return {
                'content': response.text,
                'token_count': len(response.text.split()) * 1.3,  # Rough estimate
                'confidence_score': 0.85,
                'api_response_time': 0
            }

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Google request failed: {e}")
            raise

    async def execute_local_model_request(self, model: str, prompt: str, request: LLMRequest) -> Dict:
        """Execute local model request (LLaMA, Mistral, etc.)"""
        try:
            # This would load and execute local models
            # Implementation depends on your local model setup
            logger.warning(f"[ORFEAS-LLM] Local model {model} not implemented, falling back to API")

            # Fallback to Claude for now
            return await self.execute_anthropic_request(prompt, request)

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] Local model request failed: {e}")
            raise

    async def execute_deepseek_request(self, prompt: str, request: LLMRequest) -> Dict:
        """Execute DeepSeek Coder request"""
        try:
            # DeepSeek API implementation would go here
            # For now, fallback to Claude for code tasks
            logger.info("[ORFEAS-LLM] Using Claude as DeepSeek alternative for code generation")
            return await self.execute_anthropic_request(prompt, request)

        except Exception as e:
            logger.error(f"[ORFEAS-LLM] DeepSeek request failed: {e}")
            raise

    def enhance_prompt_with_context(self, prompt: str, context: Dict) -> str:
        """Enhance prompt with intelligent context injection"""

        context_template = """ORFEAS AI 2D→3D Studio Enterprise Context:
Platform: AI-powered multimedia generation platform with Hunyuan3D-2.1, Sora-inspired video composition, and intelligent code development
User Expertise: {user_expertise}
Task Complexity: {complexity_score}
Quality Requirements: {quality_requirements}
Previous Context: {previous_interactions}

Enterprise Requirements:
- Provide technically accurate, enterprise-grade responses
- Include practical code examples when relevant (Python/JavaScript/Flask preferred)
- Consider 3D modeling, AI/ML, computer vision, and multimedia processing context
- Ensure responses align with ORFEAS platform capabilities and architecture
- Follow security best practices and enterprise coding standards

User Request:
{original_prompt}

Instructions: Respond as an expert ORFEAS AI assistant with deep knowledge of 3D modeling, AI/ML, enterprise software architecture, and multimedia processing."""

        return context_template.format(
            user_expertise=context.get('user_expertise', 'intermediate'),
            complexity_score=context.get('complexity_score', 0.5),
            quality_requirements=context.get('quality_requirements', 'high'),
            previous_interactions=context.get('previous_context', 'None'),
            original_prompt=prompt
        )

    async def fallback_llm_processing(self, request: LLMRequest, context: Dict, failed_model: str) -> LLMResponse:
        """Intelligent fallback to alternative models"""

        # Define fallback chain based on failed model
        fallback_chains = {
            'gpt4_turbo': ['claude_3_5_sonnet', 'gemini_ultra', 'mistral_8x22b'],
            'claude_3_5_sonnet': ['gpt4_turbo', 'gemini_ultra', 'mistral_8x22b'],
            'gemini_ultra': ['claude_3_5_sonnet', 'gpt4_turbo', 'mistral_8x22b'],
            'mistral_8x22b': ['claude_3_5_sonnet', 'gpt4_turbo'],
            'llama_3_1_405b': ['claude_3_5_sonnet', 'gpt4_turbo'],
            'deepseek_coder': ['claude_3_5_sonnet', 'gpt4_turbo']
        }

        fallback_models = fallback_chains.get(failed_model, ['claude_3_5_sonnet'])

        for fallback_model in fallback_models:
            if fallback_model in self.active_models and self.active_models[fallback_model]:
                try:
                    logger.info(f"[ORFEAS-LLM] Attempting fallback to {fallback_model}")

                    # Create fallback request
                    fallback_request = LLMRequest(
                        prompt=request.prompt,
                        context=request.context,
                        task_type=request.task_type,
                        priority=request.priority,
                        max_tokens=min(request.max_tokens, 1000),  # Reduce tokens for fallback
                        temperature=request.temperature,
                        model_override=fallback_model
                    )

                    result = await self.execute_llm_request(
                        model=fallback_model,
                        prompt=request.prompt,
                        request=fallback_request,
                        context=context
                    )

                    # Create response with fallback metadata
                    return LLMResponse(
                        content=result['content'],
                        model_used=fallback_model,
                        processing_time=result.get('api_response_time', 0),
                        token_count=result.get('token_count', 0),
                        confidence_score=result.get('confidence_score', 0.7),  # Lower confidence for fallback
                        metadata={
                            'fallback_used': True,
                            'original_model': failed_model,
                            'fallback_reason': 'primary_model_failed'
                        }
                    )

                except Exception as e:
                    logger.warning(f"[ORFEAS-LLM] Fallback model {fallback_model} also failed: {e}")
                    continue

        # All fallbacks failed
        raise RuntimeError(f"All LLM models failed. Original error with {failed_model}")

    def update_model_performance(self, model: str, response: LLMResponse, context: Dict):
        """Update model performance metrics"""

        if model not in self.performance_metrics:
            self.performance_metrics[model] = {
                'total_requests': 0,
                'successful_requests': 0,
                'total_processing_time': 0,
                'average_confidence': 0,
                'task_performance': {}
            }

        metrics = self.performance_metrics[model]
        task_type = context.get('task_type', 'unknown')

        # Update overall metrics
        metrics['total_requests'] += 1
        metrics['successful_requests'] += 1
        metrics['total_processing_time'] += response.processing_time

        # Update confidence tracking
        total_confidence = metrics['average_confidence'] * (metrics['successful_requests'] - 1)
        metrics['average_confidence'] = (total_confidence + response.confidence_score) / metrics['successful_requests']

        # Update task-specific performance
        if task_type not in metrics['task_performance']:
            metrics['task_performance'][task_type] = {
                'requests': 0,
                'avg_time': 0,
                'avg_confidence': 0
            }

        task_metrics = metrics['task_performance'][task_type]
        task_metrics['requests'] += 1

        # Update averages
        total_time = task_metrics['avg_time'] * (task_metrics['requests'] - 1)
        task_metrics['avg_time'] = (total_time + response.processing_time) / task_metrics['requests']

        total_conf = task_metrics['avg_confidence'] * (task_metrics['requests'] - 1)
        task_metrics['avg_confidence'] = (total_conf + response.confidence_score) / task_metrics['requests']

    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary for all models"""

        summary = {
            'timestamp': datetime.utcnow().isoformat(),
            'total_active_models': len([m for m in self.active_models.values() if m]),
            'model_performance': {},
            'recommendations': []
        }

        for model, metrics in self.performance_metrics.items():
            if metrics['total_requests'] > 0:
                success_rate = metrics['successful_requests'] / metrics['total_requests']
                avg_response_time = metrics['total_processing_time'] / metrics['successful_requests']

                summary['model_performance'][model] = {
                    'success_rate': success_rate,
                    'avg_response_time': avg_response_time,
                    'avg_confidence': metrics['average_confidence'],
                    'total_requests': metrics['total_requests'],
                    'task_specializations': metrics['task_performance']
                }

                # Generate recommendations
                if success_rate < 0.9:
                    summary['recommendations'].append(f"Consider alternative to {model} (low success rate: {success_rate:.2%})")

                if avg_response_time > 10:  # >10 seconds
                    summary['recommendations'].append(f"Optimize {model} performance (slow response: {avg_response_time:.1f}s)")

        return summary

    def set_context_manager(self, context_manager):
        """Inject context manager for enhanced processing"""
        self.context_manager = context_manager
        logger.info("[ORFEAS-LLM] Context manager integrated for enhanced LLM processing")

# Global LLM manager instance
_llm_manager = None

def get_llm_manager() -> EnterpriseLLMManager:
    """Get singleton LLM manager instance"""
    global _llm_manager
    if _llm_manager is None:
        _llm_manager = EnterpriseLLMManager()
    return _llm_manager

def initialize_llm_system(context_manager=None):
    """Initialize LLM system with optional context manager"""
    llm_manager = get_llm_manager()
    if context_manager:
        llm_manager.set_context_manager(context_manager)

    logger.info("[ORFEAS-LLM] Enterprise LLM system initialized successfully")
    return llm_manager
