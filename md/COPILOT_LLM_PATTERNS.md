# ORFEAS AI - LLM Integration & Patterns Guide

**Document:** Large Language Model integration, multi-LLM orchestration, and prompt engineering
**Version:** 2.1 (Enterprise Edition)
**Last Updated:** October 2025

## Overview

This guide covers complete LLM integration strategies for ORFEAS AI systems.

---

## LLM Architecture

### Enterprise LLM Stack

```python

## backend/llm_integration.py

from typing import Dict, List, Optional, AsyncGenerator
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class EnterpriseLLMStack:
    """Multi-LLM orchestration for enterprise."""

    def __init__(self):
        self.primary_llm = 'gpt4_turbo'
        self.fallback_llm = 'claude_3_5_sonnet'
        self.code_llm = 'copilot_enterprise'
        self.local_llm = 'mistral_7b'  # Ollama

        self.request_count = 0
        self.error_count = 0
        self.response_times = []

    async def generate_response(
        self,
        prompt: str,
        task_type: str = 'general',
        max_tokens: int = 2000,
        temperature: float = 0.7,
        use_local: bool = False
    ) -> Dict:
        """Generate LLM response with fallback strategy."""

        try:
            self.request_count += 1
            start_time = datetime.utcnow()

            # Route to appropriate model

            if use_local or self._should_use_local():
                response = await self._call_local_llm(prompt, max_tokens, temperature)
            elif task_type == 'code':
                response = await self._call_code_llm(prompt, max_tokens, temperature)
            else:
                response = await self._call_primary_llm(prompt, max_tokens, temperature)

            # Track performance

            response_time = (datetime.utcnow() - start_time).total_seconds()
            self.response_times.append(response_time)

            response['metadata'] = {
                'response_time_seconds': response_time,
                'model': response.get('model'),
                'prompt_tokens': len(prompt.split()),
                'timestamp': start_time.isoformat()
            }

            return response

        except Exception as e:
            self.error_count += 1
            logger.error(f"[LLM] Error generating response: {e}")

            # Attempt fallback

            try:
                return await self._call_fallback_llm(prompt, max_tokens, temperature)
            except Exception as fallback_error:
                logger.error(f"[LLM] Fallback also failed: {fallback_error}")
                raise

    async def _call_primary_llm(self, prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Call primary LLM (GPT-4 Turbo)."""
        logger.info("[LLM] Calling primary: GPT-4 Turbo")

        response = {
            'text': f"[Response from GPT-4 Turbo]",
            'model': 'gpt4_turbo',
            'finish_reason': 'stop'
        }

        return response

    async def _call_fallback_llm(self, prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Call fallback LLM (Claude 3.5 Sonnet)."""
        logger.warning("[LLM] Calling fallback: Claude 3.5 Sonnet")

        response = {
            'text': f"[Response from Claude 3.5 Sonnet]",
            'model': 'claude_3_5_sonnet',
            'finish_reason': 'stop'
        }

        return response

    async def _call_code_llm(self, prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Call code-optimized LLM (GitHub Copilot)."""
        logger.info("[LLM] Calling code model: GitHub Copilot")

        response = {
            'text': f"[Code from GitHub Copilot]",
            'model': 'copilot_enterprise',
            'finish_reason': 'stop'
        }

        return response

    async def _call_local_llm(self, prompt: str, max_tokens: int, temperature: float) -> Dict:
        """Call local LLM (Ollama - Mistral 7B)."""
        logger.info("[LLM] Calling local: Mistral 7B (Ollama)")

        response = {
            'text': f"[Response from Mistral 7B]",
            'model': 'mistral_7b',
            'finish_reason': 'stop'
        }

        return response

    def _should_use_local(self) -> bool:
        """Determine if local LLM should be used."""
        import os
        return os.getenv('LOCAL_LLM_ENABLED', 'false').lower() == 'true'

    def get_metrics(self) -> Dict:
        """Get LLM stack metrics."""
        avg_response_time = sum(self.response_times) / len(self.response_times) if self.response_times else 0
        error_rate = self.error_count / self.request_count if self.request_count > 0 else 0

        return {
            'total_requests': self.request_count,
            'total_errors': self.error_count,
            'error_rate': error_rate,
            'avg_response_time_seconds': avg_response_time,
            'p95_response_time_seconds': sorted(self.response_times)[int(len(self.response_times) * 0.95)] if self.response_times else 0
        }

## Global LLM instance

llm_stack: Optional[EnterpriseLLMStack] = None

def get_llm_stack() -> EnterpriseLLMStack:
    """Get global LLM stack instance."""
    global llm_stack
    if llm_stack is None:
        llm_stack = EnterpriseLLMStack()
    return llm_stack

```text

---

## Local LLM Setup

### Ollama Integration

```python

## backend/ollama_integration.py

import requests
import json
import logging

logger = logging.getLogger(__name__)

class OllamaIntegration:
    """Local Ollama LLM integration."""

    def __init__(self, endpoint='http://localhost:11434'):
        self.endpoint = endpoint
        self.model = 'mistral'

    def check_availability(self) -> bool:
        """Check if Ollama service is available."""
        try:
            response = requests.get(f"{self.endpoint}/api/tags", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"[OLLAMA] Service unavailable: {e}")
            return False

    def pull_model(self, model_name: str = 'mistral') -> bool:
        """Pull model from Ollama library."""
        try:
            logger.info(f"[OLLAMA] Pulling model: {model_name}")
            response = requests.post(
                f"{self.endpoint}/api/pull",
                json={"name": model_name},
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    status = data.get('status', '')
                    if 'digest' in data:
                        logger.info(f"[OLLAMA] {status} {data['digest']}")

            return True
        except Exception as e:
            logger.error(f"[OLLAMA] Failed to pull model: {e}")
            return False

    def generate_response(
        self,
        prompt: str,
        model: str = 'mistral',
        temperature: float = 0.7
    ) -> str:
        """Generate response from local Ollama model."""
        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "temperature": temperature,
                    "stream": False
                }
            )

            data = response.json()
            return data.get('response', '')
        except Exception as e:
            logger.error(f"[OLLAMA] Generation failed: {e}")
            raise

    async def stream_response(
        self,
        prompt: str,
        model: str = 'mistral'
    ):
        """Stream response from Ollama."""
        try:
            response = requests.post(
                f"{self.endpoint}/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": True
                },
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    data = json.loads(line)
                    yield data.get('response', '')
        except Exception as e:
            logger.error(f"[OLLAMA] Streaming failed: {e}")
            raise

## Flask endpoints

@app.route('/api/llm/generate', methods=['POST'])
async def generate_llm_response():
    """Generate LLM response."""
    data = request.get_json()
    prompt = data.get('prompt')
    task_type = data.get('task_type', 'general')
    use_local = data.get('use_local', False)

    llm = get_llm_stack()
    response = await llm.generate_response(
        prompt=prompt,
        task_type=task_type,
        use_local=use_local
    )

    return jsonify(response)

@app.route('/api/llm/metrics', methods=['GET'])
def get_llm_metrics():
    """Get LLM performance metrics."""
    llm = get_llm_stack()
    return jsonify(llm.get_metrics())

```text

---

## Multi-LLM Orchestration

### Intelligent Model Routing

```python

## backend/llm_router.py

from enum import Enum
from typing import Dict, List

class TaskType(Enum):
    CODE_GENERATION = 'code_generation'
    CODE_REVIEW = 'code_review'
    DOCUMENTATION = 'documentation'
    ANALYSIS = 'analysis'
    CREATIVE = 'creative'
    GENERAL = 'general'

class LLMRouter:
    """Intelligent routing of tasks to optimal LLM."""

    ROUTING_MAP = {
        TaskType.CODE_GENERATION: 'copilot_enterprise',
        TaskType.CODE_REVIEW: 'copilot_enterprise',
        TaskType.DOCUMENTATION: 'gpt4_turbo',
        TaskType.ANALYSIS: 'claude_3_5_sonnet',
        TaskType.CREATIVE: 'gpt4_turbo',
        TaskType.GENERAL: 'gpt4_turbo'
    }

    COMPLEXITY_ROUTING = {
        'simple': 'mistral_7b',  # Local, fast
        'medium': 'gpt4_turbo',  # Balanced
        'complex': 'claude_3_5_sonnet'  # Most capable
    }

    @staticmethod
    def select_model(task_type: TaskType, complexity: str = 'medium') -> str:
        """Select optimal model for task."""

        # Task-specific routing takes precedence

        if task_type in LLMRouter.ROUTING_MAP:
            return LLMRouter.ROUTING_MAP[task_type]

        # Fall back to complexity-based routing

        return LLMRouter.COMPLEXITY_ROUTING.get(complexity, 'gpt4_turbo')

    @staticmethod
    def select_backup_models(primary_model: str) -> List[str]:
        """Get backup models if primary fails."""

        backup_chain = {
            'gpt4_turbo': ['claude_3_5_sonnet', 'mistral_7b'],
            'claude_3_5_sonnet': ['gpt4_turbo', 'mistral_7b'],
            'copilot_enterprise': ['gpt4_turbo', 'claude_3_5_sonnet'],
            'mistral_7b': ['gpt4_turbo', 'claude_3_5_sonnet']
        }

        return backup_chain.get(primary_model, [])

class MultiLLMOrchestrator:
    """Orchestrate multiple LLMs for complex tasks."""

    async def decompose_and_solve(self, problem: str) -> Dict:
        """Break complex problem into subtasks, solve with optimal LLMs."""

        # Step 1: Decompose problem

        decomposition = await self._decompose_problem(problem)

        # Step 2: Solve subtasks in parallel

        subtask_results = await asyncio.gather(*[
            self._solve_subtask(subtask)
            for subtask in decomposition['subtasks']
        ])

        # Step 3: Synthesize results

        final_result = await self._synthesize_results(subtask_results)

        return final_result

    async def _decompose_problem(self, problem: str) -> Dict:
        """Break problem into subtasks."""

        # Use Claude for problem analysis

        subtasks = [
            {'id': 1, 'description': 'Subtask 1'},
            {'id': 2, 'description': 'Subtask 2'}
        ]
        return {'subtasks': subtasks}

    async def _solve_subtask(self, subtask: Dict) -> Dict:
        """Solve individual subtask."""
        model = LLMRouter.select_model(TaskType.GENERAL, 'medium')

        # Call appropriate LLM

        return {'subtask_id': subtask['id'], 'result': 'solution'}

    async def _synthesize_results(self, results: List[Dict]) -> Dict:
        """Combine subtask results into final answer."""
        return {
            'final_answer': 'combined result',
            'components': results
        }

```text

---

## Prompt Engineering

### Advanced Prompt Strategies

```python

## backend/prompt_engineering.py

from typing import List, Dict

class PromptEngineer:
    """Advanced prompt engineering strategies."""

    @staticmethod
    def create_system_prompt(role: str, context: str = '') -> str:
        """Create system prompt for role-specific LLM behavior."""

        prompts = {
            'code_expert': """You are an expert software engineer with deep knowledge of:

- Multiple programming languages (Python, JavaScript, Go, Rust, C++)
- System design and architecture
- Performance optimization
- Security best practices

Provide clear, well-structured code with explanations.""",

            'security_analyst': """You are a cybersecurity expert specializing in:

- Vulnerability analysis
- Secure coding practices
- Threat modeling
- Compliance standards (ISO, SOC2, GDPR)

Identify risks and recommend mitigations.""",

            'data_scientist': """You are a data science expert with expertise in:

- Machine learning algorithms
- Statistical analysis
- Data visualization
- Model optimization

Provide data-driven insights and recommendations."""
        }

        return prompts.get(role, f"Act as a {role}. {context}")

    @staticmethod
    def create_few_shot_prompt(examples: List[Dict], task_description: str) -> str:
        """Create few-shot learning prompt with examples."""

        prompt = f"{task_description}\n\nExamples:\n"

        for i, example in enumerate(examples, 1):
            prompt += f"\nExample {i}:\n"
            prompt += f"Input: {example['input']}\n"
            prompt += f"Output: {example['output']}\n"

        return prompt

    @staticmethod
    def create_chain_of_thought_prompt(task: str) -> str:
        """Create prompt that encourages step-by-step reasoning."""

        return f"""Let's solve this step by step.

Task: {task}

Please:

1. Break down the problem into components

2. Think through each component

3. Reason about interactions between components

4. Arrive at a solution

Show your reasoning at each step."""

    @staticmethod
    def create_constrained_output_prompt(
        task: str,
        format_spec: str,
        constraints: List[str]
    ) -> str:
        """Create prompt with output format and constraints."""

        prompt = f"Task: {task}\n\n"
        prompt += f"Output Format:\n{format_spec}\n\n"
        prompt += "Constraints:\n"
        for constraint in constraints:
            prompt += f"- {constraint}\n"

        return prompt

class PromptOptimizer:
    """Optimize prompts for better LLM performance."""

    @staticmethod
    def measure_prompt_quality(prompt: str, response: str) -> float:
        """Measure quality of prompt-response pair."""

        quality_score = 0.0

        # Clarity score (based on prompt length and specificity)

        if len(prompt) > 50 and len(prompt) < 2000:
            quality_score += 0.3

        # Completeness score (response contains expected elements)

        if len(response) > 100:
            quality_score += 0.3

        # Relevance score (rough heuristic)

        if any(word in response.lower() for word in ['task', 'complete', 'done']):
            quality_score += 0.4

        return min(quality_score, 1.0)

    @staticmethod
    def auto_optimize_prompt(original_prompt: str) -> str:
        """Automatically improve prompt quality."""

        optimized = original_prompt

        # Add specificity

        if 'please' not in optimized.lower():
            optimized += "\nPlease be specific and detailed in your response."

        # Add context

        if 'context' not in optimized.lower():
            optimized = "Context: You are helping a software developer.\n" + optimized

        # Add output format guidance

        if 'format' not in optimized.lower():
            optimized += "\nProvide your response in a clear, structured format."

        return optimized

```text

---

## RAG Integration

### Retrieval-Augmented Generation

```python

## backend/rag_integration.py

from typing import List, Tuple
import numpy as np

class RAGSystem:
    """Retrieval-Augmented Generation implementation."""

    def __init__(self, vector_db_type='pinecone'):
        self.vector_db_type = vector_db_type
        self.retriever = self._initialize_retriever()
        self.llm = get_llm_stack()

    def _initialize_retriever(self):
        """Initialize vector database retriever."""
        if self.vector_db_type == 'pinecone':

            # Pinecone integration

            pass
        elif self.vector_db_type == 'weaviate':

            # Weaviate integration

            pass
        return None

    async def retrieve_and_generate(
        self,
        query: str,
        top_k: int = 5
    ) -> Dict:
        """Retrieve relevant documents and generate response."""

        # Step 1: Retrieve relevant documents

        documents = self.retriever.retrieve(query, top_k=top_k)

        # Step 2: Build augmented prompt

        augmented_prompt = self._build_augmented_prompt(query, documents)

        # Step 3: Generate response

        response = await self.llm.generate_response(
            prompt=augmented_prompt,
            task_type='general'
        )

        return {
            'query': query,
            'response': response,
            'sources': [doc['source'] for doc in documents]
        }

    def _build_augmented_prompt(self, query: str, documents: List[Dict]) -> str:
        """Build prompt augmented with retrieved context."""

        context = "\n".join([
            f"Document {i+1}: {doc['content']}"
            for i, doc in enumerate(documents)
        ])

        augmented_prompt = f"""Based on the following context documents, answer the question.

Context:
{context}

Question: {query}

Answer:"""

        return augmented_prompt

    def add_documents(self, documents: List[Dict], metadata: Dict = None):
        """Add documents to knowledge base."""

        for doc in documents:

            # Generate embedding

            embedding = self._generate_embedding(doc['content'])

            # Store in vector database

            self.retriever.add_document(
                id=doc.get('id'),
                embedding=embedding,
                metadata={
                    'source': doc.get('source'),
                    'content': doc.get('content'),

                    **(metadata or {})

                }
            )

    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate text embedding."""

        # Use OpenAI embeddings or local embedding model

        # Returns vector of size 1536 (for OpenAI)

        return np.random.randn(1536)

class KnowledgeGraphManager:
    """Manage knowledge graph for semantic search."""

    def __init__(self, db_url='bolt://localhost:7687'):
        self.db_url = db_url

        # Initialize Neo4j connection

    def add_relationship(self, entity1: str, relationship: str, entity2: str):
        """Add relationship to knowledge graph."""

        # Cypher query to add relationship

        pass

    def query_relationships(self, entity: str) -> List[Tuple]:
        """Query related entities."""

        # Cypher query to retrieve relationships

        return []

```text

---

## LLM Performance Optimization

### Response Caching & Batching

```python

## backend/llm_performance_optimizer.py

from functools import lru_cache
import hashlib
from typing import Dict, List

class LLMPerformanceOptimizer:
    """Optimize LLM performance through caching and batching."""

    def __init__(self):
        self.response_cache = {}
        self.batch_queue = []
        self.cache_hits = 0
        self.cache_misses = 0

    def get_cached_response(self, prompt: str) -> Dict:
        """Retrieve response from cache if available."""

        cache_key = hashlib.md5(prompt.encode()).hexdigest()

        if cache_key in self.response_cache:
            self.cache_hits += 1
            logger.info(f"[LLM-OPT] Cache hit (total: {self.cache_hits})")
            return self.response_cache[cache_key]

        self.cache_misses += 1
        return None

    def cache_response(self, prompt: str, response: Dict, ttl_seconds: int = 3600):
        """Cache LLM response."""

        cache_key = hashlib.md5(prompt.encode()).hexdigest()
        self.response_cache[cache_key] = {
            'response': response,
            'cached_at': datetime.utcnow(),
            'ttl': ttl_seconds
        }

    async def batch_generate(self, prompts: List[str]) -> List[Dict]:
        """Generate responses for multiple prompts in batch."""

        logger.info(f"[LLM-OPT] Batch processing {len(prompts)} prompts")

        responses = []
        for prompt in prompts:

            # Check cache first

            cached = self.get_cached_response(prompt)
            if cached:
                responses.append(cached)
                continue

            # Generate if not cached

            response = await get_llm_stack().generate_response(prompt)
            self.cache_response(prompt, response)
            responses.append(response)

        return responses

    def get_cache_efficiency(self) -> Dict:
        """Get cache efficiency metrics."""
        total_requests = self.cache_hits + self.cache_misses
        hit_rate = self.cache_hits / total_requests if total_requests > 0 else 0

        return {
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'total_requests': total_requests,
            'hit_rate': hit_rate,
            'cache_size': len(self.response_cache)
        }

```text

---

## Enterprise LLM Security

### Content Filtering & Safety

```python

## backend/llm_safety_filter.py

import logging
from typing import Tuple

logger = logging.getLogger(__name__)

class LLMSafetyFilter:
    """Content filtering and safety measures for LLM outputs."""

    FORBIDDEN_PATTERNS = [
        r'(\bprivate\b.*\bkey\b)',
        r'(\bpassword\b)',
        r'(\bsql\s+injection\b)'
    ]

    def __init__(self):
        self.blocked_count = 0

    def filter_prompt(self, prompt: str) -> Tuple[bool, str]:
        """Filter potentially harmful prompts."""

        import re

        for pattern in self.FORBIDDEN_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                self.blocked_count += 1
                logger.warning(f"[SAFETY] Prompt blocked - matches forbidden pattern")
                return False, "Prompt contains forbidden content"

        return True, prompt

    def filter_response(self, response: str) -> Tuple[bool, str]:
        """Filter potentially harmful responses."""

        # Check for sensitive information exposure

        if self._contains_sensitive_info(response):
            logger.warning("[SAFETY] Response contains sensitive information")
            return False, "[Sensitive content removed]"

        return True, response

    def _contains_sensitive_info(self, text: str) -> bool:
        """Check if response contains sensitive information."""

        sensitive_patterns = [
            r'\b(?:\d{1,5}[.-]?){3}\d{1,5}\b',  # IP addresses
            r'\b[A-Z0-9]{40}\b',  # Potential keys/tokens
            r'(?:password|api_key|secret)[\s:=]+[\S]+'  # Credentials
        ]

        import re
        for pattern in sensitive_patterns:
            if re.search(pattern, text):
                return True

        return False

    def get_safety_stats(self) -> Dict:
        """Get safety filter statistics."""
        return {'total_blocked': self.blocked_count}

```text

---

## Cost Optimization

### LLM Cost Management

```python

## backend/llm_cost_optimizer.py

from datetime import datetime

class LLMCostOptimizer:
    """Optimize costs for LLM usage."""

    PRICING = {
        'gpt4_turbo': {
            'input_1k_tokens': 0.01,
            'output_1k_tokens': 0.03
        },
        'claude_3_5_sonnet': {
            'input_1k_tokens': 0.003,
            'output_1k_tokens': 0.015
        },
        'mistral_7b': {
            'input_1k_tokens': 0.0,  # Local, free
            'output_1k_tokens': 0.0
        }
    }

    def __init__(self):
        self.total_cost = 0.0
        self.daily_cost = 0.0
        self.model_costs = {}

    def estimate_cost(
        self,
        model: str,
        input_tokens: int,
        output_tokens: int
    ) -> float:
        """Estimate cost for API call."""

        if model not in self.PRICING:
            return 0.0

        pricing = self.PRICING[model]
        input_cost = (input_tokens / 1000) * pricing['input_1k_tokens']
        output_cost = (output_tokens / 1000) * pricing['output_1k_tokens']

        total = input_cost + output_cost
        self.total_cost += total
        self.daily_cost += total

        if model not in self.model_costs:
            self.model_costs[model] = 0.0
        self.model_costs[model] += total

        return total

    def get_cost_report(self) -> Dict:
        """Get cost summary report."""

        return {
            'total_cost': self.total_cost,
            'daily_cost': self.daily_cost,
            'model_costs': self.model_costs,
            'average_cost_per_request': self.total_cost / 100  # Approximation
        }

    def recommend_cost_optimizations(self) -> List[str]:
        """Recommend cost optimization strategies."""

        recommendations = []

        # Recommend local LLM for simple tasks

        if self.total_cost > 100:
            recommendations.append("Use local Mistral 7B for simple tasks to reduce costs")

        # Recommend caching

        if self.daily_cost > 50:
            recommendations.append("Implement response caching to avoid duplicate API calls")

        # Recommend batch processing

        if self.total_cost > 200:
            recommendations.append("Use batch APIs for non-real-time tasks")

        return recommendations

```text

---

This comprehensive LLM integration guide provides enterprise-grade patterns for leveraging multiple LLMs effectively and cost-efficiently in the ORFEAS platform.
