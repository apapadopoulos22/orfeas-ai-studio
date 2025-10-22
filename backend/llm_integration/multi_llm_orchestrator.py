"""
ORFEAS AI 2D→3D Studio - Multi-LLM Orchestrator
================================================
Coordinates multiple Large Language Models for complex multi-step tasks.

Features:
- Task decomposition and planning
- Parallel LLM execution coordination
- Result synthesis and validation
- Multi-model ensemble strategies
- Dynamic workflow adaptation
- Error recovery and retry logic
"""

import os
import time
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from .llm_router import get_llm_router, TaskType, RoutingContext
from .error_handler import (
    error_context,
    safe_execute,
    LLMOrchestratorError,
    ErrorAggregator
)
from .tracing import (
    trace_performance,
    trace_block_async,
    PerformanceTracer
)
from .multi_model_ensembler import (
    MultiModelEnsembler,
    EnsembleResponse,
    ModelContribution
)

logger = logging.getLogger(__name__)


class OrchestrationStrategy(Enum):
    """Strategies for multi-LLM orchestration"""
    SEQUENTIAL = "sequential"  # One after another
    PARALLEL = "parallel"  # All at once
    HIERARCHICAL = "hierarchical"  # Main LLM delegates to specialists
    ENSEMBLE = "ensemble"  # Multiple LLMs for same task, combine results
    PIPELINE = "pipeline"  # Output of one feeds into next
    ADAPTIVE = "adaptive"  # Strategy changes based on results


class SubtaskStatus(Enum):
    """Status of orchestrated subtasks"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"


@dataclass
class Subtask:
    """A subtask in orchestrated workflow"""
    subtask_id: str
    description: str
    task_type: TaskType
    prompt: str
    assigned_model: Optional[str] = None
    status: SubtaskStatus = SubtaskStatus.PENDING
    result: Optional[str] = None
    error: Optional[str] = None
    dependencies: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attempts: int = 0
    max_attempts: int = 3
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


@dataclass
class OrchestrationContext:
    """Context for orchestration workflow"""
    workflow_id: str
    main_task: str
    strategy: OrchestrationStrategy
    subtasks: List[Subtask]
    enable_ensemble: bool = False
    enable_retry: bool = True
    max_parallel_tasks: int = 5
    timeout_seconds: int = 300
    quality_threshold: float = 0.7
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class OrchestrationResult:
    """Result from orchestrated workflow"""
    workflow_id: str
    success: bool
    final_result: str
    subtask_results: Dict[str, str]
    execution_time: float
    total_cost: float
    models_used: List[str]
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class MultiLLMOrchestrator:
    """
    Orchestrates multiple LLMs for complex multi-step tasks
    """

    def __init__(self):
        self.router = get_llm_router()
        self.active_workflows: Dict[str, OrchestrationContext] = {}
        self.workflow_history: List[OrchestrationResult] = []
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.error_agg = ErrorAggregator()
        self.perf_tracer = PerformanceTracer()

        # Initialize multi-model ensembler for ensemble orchestration strategy
        self.ensembler = MultiModelEnsembler()
        self.ensemble_confidence_threshold = 0.7
        self.ensemble_enabled = True

        logger.info("[ORFEAS-ORCHESTRATOR] Multi-LLM Orchestrator initialized")

    @trace_performance(operation='orchestrate', component='multi_llm_orchestrator')
    @error_context(component='multi_llm_orchestrator', operation='orchestrate')
    async def orchestrate(
        self,
        task: str,
        strategy: OrchestrationStrategy = OrchestrationStrategy.ADAPTIVE,
        context: Optional[Dict[str, Any]] = None
    ) -> OrchestrationResult:
        """
        Orchestrate complex task across multiple LLMs

        Args:
            task: Main task description
            strategy: Orchestration strategy to use
            context: Additional context and parameters

        Returns:
            OrchestrationResult with final output
        """
        workflow_id = self._generate_workflow_id(task)
        start_time = time.time()

        try:
            logger.info(
                f"[ORFEAS-ORCHESTRATOR] Starting orchestration for workflow {workflow_id}"
            )

            # Decompose task into subtasks
            subtasks = await self._decompose_task(task, context or {})

            # Create orchestration context
            orch_context = OrchestrationContext(
                workflow_id=workflow_id,
                main_task=task,
                strategy=strategy,
                subtasks=subtasks,
                enable_ensemble=context.get('enable_ensemble', False) if context else False,
                metadata=context or {}
            )

            self.active_workflows[workflow_id] = orch_context

            # Execute based on strategy
            if strategy == OrchestrationStrategy.SEQUENTIAL:
                result = await self._execute_sequential(orch_context)
            elif strategy == OrchestrationStrategy.PARALLEL:
                result = await self._execute_parallel(orch_context)
            elif strategy == OrchestrationStrategy.HIERARCHICAL:
                result = await self._execute_hierarchical(orch_context)
            elif strategy == OrchestrationStrategy.ENSEMBLE:
                result = await self._execute_ensemble(orch_context)
            elif strategy == OrchestrationStrategy.PIPELINE:
                result = await self._execute_pipeline(orch_context)
            elif strategy == OrchestrationStrategy.ADAPTIVE:
                result = await self._execute_adaptive(orch_context)
            else:
                raise ValueError(f"Unknown strategy: {strategy}")

            # Synthesize final result
            final_result = await self._synthesize_results(orch_context, result)

            execution_time = time.time() - start_time

            # Calculate total cost
            total_cost = self._calculate_workflow_cost(orch_context)

            # Get models used
            models_used = list(set(
                st.assigned_model for st in orch_context.subtasks
                if st.assigned_model
            ))

            orchestration_result = OrchestrationResult(
                workflow_id=workflow_id,
                success=True,
                final_result=final_result,
                subtask_results={st.subtask_id: st.result for st in orch_context.subtasks},
                execution_time=execution_time,
                total_cost=total_cost,
                models_used=models_used
            )

            self.workflow_history.append(orchestration_result)

            logger.info(
                f"[ORFEAS-ORCHESTRATOR] Workflow {workflow_id} completed in {execution_time:.2f}s"
            )

            return orchestration_result

        except Exception as e:
            logger.error(f"[ORFEAS-ORCHESTRATOR] Workflow {workflow_id} failed: {e}")

            execution_time = time.time() - start_time

            return OrchestrationResult(
                workflow_id=workflow_id,
                success=False,
                final_result="",
                subtask_results={},
                execution_time=execution_time,
                total_cost=0.0,
                models_used=[],
                error=str(e)
            )

        finally:
            if workflow_id in self.active_workflows:
                del self.active_workflows[workflow_id]

    @trace_performance(operation='decompose_task', component='multi_llm_orchestrator')
    @error_context(component='multi_llm_orchestrator', operation='decompose_task')
    async def _decompose_task(
        self,
        task: str,
        context: Dict[str, Any]
    ) -> List[Subtask]:
        """Decompose complex task into subtasks"""

        # Use LLM to decompose task (GPT-4 for planning)
        decomposition_prompt = f"""
        Decompose this complex task into smaller, manageable subtasks:

        Task: {task}

        Context: {json.dumps(context, indent=2)}

        Provide subtasks in JSON format:
        [
          {{"id": "subtask_1", "description": "...", "type": "code_generation"}},
          {{"id": "subtask_2", "description": "...", "type": "text_analysis"}},
          ...
        ]

        Task types: code_generation, text_analysis, reasoning, creative_writing,
                   translation, summarization, qa, chat, multimodal, general
        """

        routing_context = RoutingContext(
            task_type=TaskType.REASONING,
            prompt_length=len(decomposition_prompt),
            max_tokens=2000,
            priority="high"
        )

        model_id, model_config = await self.router.route_request(
            decomposition_prompt,
            routing_context
        )

        # Execute decomposition (mock for now - would call actual LLM API)
        decomposition_result = await self._execute_llm_request(
            model_id,
            decomposition_prompt,
            model_config
        )

        # Parse subtasks from LLM response
        subtasks = self._parse_subtasks(decomposition_result, task)

        logger.info(f"[ORFEAS-ORCHESTRATOR] Decomposed into {len(subtasks)} subtasks")

        return subtasks

    def _parse_subtasks(self, llm_response: str, main_task: str) -> List[Subtask]:
        """Parse subtasks from LLM decomposition response"""

        try:
            # Try to parse JSON from response
            import re
            json_match = re.search(r'\[.*\]', llm_response, re.DOTALL)
            if json_match:
                subtasks_data = json.loads(json_match.group())

                subtasks = []
                for i, st_data in enumerate(subtasks_data):
                    task_type_str = st_data.get('type', 'general')
                    try:
                        task_type = TaskType(task_type_str)
                    except ValueError:
                        task_type = TaskType.GENERAL

                    subtask = Subtask(
                        subtask_id=st_data.get('id', f'subtask_{i+1}'),
                        description=st_data.get('description', ''),
                        task_type=task_type,
                        prompt=st_data.get('prompt', st_data.get('description', ''))
                    )
                    subtasks.append(subtask)

                return subtasks
        except Exception as e:
            logger.warning(f"[ORFEAS-ORCHESTRATOR] Failed to parse subtasks: {e}")

        # Fallback: create simple subtask
        return [
            Subtask(
                subtask_id='subtask_1',
                description=main_task,
                task_type=TaskType.GENERAL,
                prompt=main_task
            )
        ]

    async def _execute_sequential(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute subtasks sequentially"""

        results = {}

        for subtask in context.subtasks:
            # Check dependencies
            if not self._check_dependencies_met(subtask, results):
                logger.warning(
                    f"[ORFEAS-ORCHESTRATOR] Dependencies not met for {subtask.subtask_id}"
                )
                continue

            # Execute subtask
            result = await self._execute_subtask(subtask, context)
            results[subtask.subtask_id] = result

        return results

    async def _execute_parallel(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute subtasks in parallel"""

        # Group subtasks by dependency level
        dependency_levels = self._compute_dependency_levels(context.subtasks)

        results = {}

        for level, subtasks_at_level in sorted(dependency_levels.items()):
            # Execute all subtasks at this level in parallel
            tasks = []
            for subtask in subtasks_at_level:
                if self._check_dependencies_met(subtask, results):
                    tasks.append(self._execute_subtask(subtask, context))

            if tasks:
                level_results = await asyncio.gather(*tasks, return_exceptions=True)

                for subtask, result in zip(subtasks_at_level, level_results):
                    if isinstance(result, Exception):
                        logger.error(
                            f"[ORFEAS-ORCHESTRATOR] Subtask {subtask.subtask_id} failed: {result}"
                        )
                        subtask.status = SubtaskStatus.FAILED
                        subtask.error = str(result)
                    else:
                        results[subtask.subtask_id] = result

        return results

    async def _execute_hierarchical(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute with main LLM delegating to specialists"""

        # Main LLM coordinates
        main_subtask = context.subtasks[0] if context.subtasks else None

        if not main_subtask:
            return {}

        # Execute main task
        main_result = await self._execute_subtask(main_subtask, context)

        results = {main_subtask.subtask_id: main_result}

        # Execute remaining subtasks as delegated tasks
        specialist_tasks = context.subtasks[1:]

        if specialist_tasks:
            parallel_results = await asyncio.gather(*[
                self._execute_subtask(st, context)
                for st in specialist_tasks
            ], return_exceptions=True)

            for subtask, result in zip(specialist_tasks, parallel_results):
                if not isinstance(result, Exception):
                    results[subtask.subtask_id] = result

        return results

    async def _execute_ensemble(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute same task with multiple models and combine results with confidence filtering"""

        results = {}

        for subtask in context.subtasks:
            # Build model executors for ensembler
            model_executors: Dict[str, Callable] = {}

            # Get available models
            router = self.router
            candidates = []
            for model_id, config in router.models.items():
                if config.enabled and config.supports_task_type(subtask.task_type):
                    candidates.append((model_id, config))

            # Take top 3 by priority
            top_models = sorted(candidates, key=lambda x: x[1].priority)[:3]

            # Create executor for each model
            for model_id, config in top_models:
                async def make_model_executor(mid: str, cfg) -> Callable:
                    """Create executor function for a specific model"""
                    async def model_executor() -> ModelContribution:
                        try:
                            response = await self._execute_llm_request(
                                subtask.description,
                                model=mid,
                                context=context
                            )
                            # Return ModelContribution
                            return ModelContribution(
                                model_name=mid,
                                content=response,
                                quality_score=0.85,
                                confidence=0.8
                            )
                        except Exception as e:
                            logger.warning(
                                f"[ORFEAS-ORCHESTRATOR] Model {mid} failed: {e}"
                            )
                            raise
                    return model_executor

                model_executors[model_id] = await make_model_executor(model_id, config)

            # Use ensembler to combine responses
            if self.ensemble_enabled and len(model_executors) >= 2:
                try:
                    ensemble_result = await self.ensembler.get_ensemble_response(
                        prompt=subtask.description,
                        model_executors=model_executors,
                        merge_strategy='weighted_consensus',
                        use_quality_filtering=True,
                        quality_threshold=0.6
                    )

                    # Apply confidence filtering
                    if ensemble_result.confidence >= self.ensemble_confidence_threshold:
                        results[subtask.subtask_id] = {
                            'response': ensemble_result.consensus,
                            'confidence': ensemble_result.confidence,
                            'strategy': 'ensemble',
                            'individual_scores': ensemble_result.individual_scores,
                            'merge_strategy_used': ensemble_result.merge_strategy
                        }
                        logger.info(
                            f"[ORFEAS-ORCHESTRATOR] Ensemble result: "
                            f"confidence={ensemble_result.confidence:.2f}, "
                            f"strategy={ensemble_result.merge_strategy}"
                        )
                    else:
                        # Fall back to best response if confidence too low
                        best_model = max(ensemble_result.individual_scores.items(),
                                       key=lambda x: x[1])
                        results[subtask.subtask_id] = {
                            'response': ensemble_result.responses.get(best_model[0], ensemble_result.consensus),
                            'confidence': ensemble_result.confidence,
                            'strategy': 'fallback',
                            'reason': 'confidence_below_threshold',
                            'best_model': best_model[0]
                        }
                except Exception as e:
                    logger.error(f"[ORFEAS-ORCHESTRATOR] Ensemble failed: {e}")
                    # Fallback: execute first model directly
                    try:
                        first_executor = list(model_executors.values())[0]
                        first_contribution = await first_executor()
                        results[subtask.subtask_id] = {
                            'response': first_contribution.content,
                            'confidence': 0.5,
                            'strategy': 'fallback_single'
                        }
                    except Exception as e2:
                        logger.error(f"[ORFEAS-ORCHESTRATOR] Fallback executor failed: {e2}")
                        results[subtask.subtask_id] = {
                            'response': '',
                            'confidence': 0.0,
                            'strategy': 'failed',
                            'error': str(e2)
                        }
            elif model_executors:
                # If ensemble disabled or <2 models, use first model
                try:
                    first_executor = list(model_executors.values())[0]
                    first_contribution = await first_executor()
                    results[subtask.subtask_id] = {
                        'response': first_contribution.content,
                        'confidence': 0.6,
                        'strategy': 'single' if not self.ensemble_enabled else 'insufficient_models'
                    }
                except Exception as e:
                    logger.error(f"[ORFEAS-ORCHESTRATOR] Single model execution failed: {e}")
                    results[subtask.subtask_id] = {
                        'response': '',
                        'confidence': 0.0,
                        'strategy': 'failed',
                        'error': str(e)
                    }

        return results

    async def _execute_pipeline(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Execute as pipeline where output feeds into next"""

        results = {}
        previous_output = None

        for subtask in context.subtasks:
            # Augment prompt with previous output
            if previous_output:
                subtask.prompt = f"{subtask.prompt}\n\nPrevious step output:\n{previous_output}"

            # Execute subtask
            result = await self._execute_subtask(subtask, context)
            results[subtask.subtask_id] = result
            previous_output = result

        return results

    async def _execute_adaptive(
        self,
        context: OrchestrationContext
    ) -> Dict[str, Any]:
        """Adaptively choose strategy based on task characteristics"""

        # Analyze task characteristics
        num_subtasks = len(context.subtasks)
        has_dependencies = any(st.dependencies for st in context.subtasks)

        # Choose strategy
        if context.enable_ensemble:
            strategy = OrchestrationStrategy.ENSEMBLE
        elif num_subtasks == 1:
            strategy = OrchestrationStrategy.SEQUENTIAL
        elif has_dependencies:
            strategy = OrchestrationStrategy.PARALLEL  # Respects dependencies
        elif num_subtasks <= 3:
            strategy = OrchestrationStrategy.PIPELINE
        else:
            strategy = OrchestrationStrategy.HIERARCHICAL

        logger.info(
            f"[ORFEAS-ORCHESTRATOR] Adaptive strategy selected: {strategy.value}"
        )

        # Update context and execute
        context.strategy = strategy

        if strategy == OrchestrationStrategy.SEQUENTIAL:
            return await self._execute_sequential(context)
        elif strategy == OrchestrationStrategy.PARALLEL:
            return await self._execute_parallel(context)
        elif strategy == OrchestrationStrategy.HIERARCHICAL:
            return await self._execute_hierarchical(context)
        elif strategy == OrchestrationStrategy.ENSEMBLE:
            return await self._execute_ensemble(context)
        elif strategy == OrchestrationStrategy.PIPELINE:
            return await self._execute_pipeline(context)
        else:
            return await self._execute_sequential(context)

    async def _execute_subtask(
        self,
        subtask: Subtask,
        context: OrchestrationContext
    ) -> str:
        """Execute a single subtask"""

        subtask.status = SubtaskStatus.RUNNING
        subtask.start_time = datetime.utcnow()
        subtask.attempts += 1

        try:
            # Route to appropriate model
            routing_context = RoutingContext(
                task_type=subtask.task_type,
                prompt_length=len(subtask.prompt),
                max_tokens=2000,
                priority="normal"
            )

            model_id, model_config = await self.router.route_request(
                subtask.prompt,
                routing_context
            )

            subtask.assigned_model = model_id

            # Execute LLM request
            result = await self._execute_llm_request(
                model_id,
                subtask.prompt,
                model_config
            )

            subtask.result = result
            subtask.status = SubtaskStatus.COMPLETED
            subtask.end_time = datetime.utcnow()

            logger.info(
                f"[ORFEAS-ORCHESTRATOR] Completed subtask {subtask.subtask_id} "
                f"with {model_id}"
            )

            return result

        except Exception as e:
            logger.error(
                f"[ORFEAS-ORCHESTRATOR] Subtask {subtask.subtask_id} failed: {e}"
            )

            subtask.error = str(e)

            # Retry logic
            if context.enable_retry and subtask.attempts < subtask.max_attempts:
                subtask.status = SubtaskStatus.RETRYING
                logger.info(
                    f"[ORFEAS-ORCHESTRATOR] Retrying subtask {subtask.subtask_id} "
                    f"(attempt {subtask.attempts + 1}/{subtask.max_attempts})"
                )
                return await self._execute_subtask(subtask, context)

            subtask.status = SubtaskStatus.FAILED
            raise

    async def _execute_llm_request(
        self,
        model_id: str,
        prompt: str,
        model_config: Any
    ) -> str:
        """Execute actual LLM API request (mock for now)"""

        # This would make actual API calls to OpenAI, Anthropic, etc.
        # For now, return mock response

        await asyncio.sleep(0.1)  # Simulate API latency

        return f"[Response from {model_id}] Processing: {prompt[:100]}..."

    def _check_dependencies_met(
        self,
        subtask: Subtask,
        results: Dict[str, Any]
    ) -> bool:
        """Check if subtask dependencies are met"""

        if not subtask.dependencies:
            return True

        return all(dep_id in results for dep_id in subtask.dependencies)

    def _compute_dependency_levels(
        self,
        subtasks: List[Subtask]
    ) -> Dict[int, List[Subtask]]:
        """Compute dependency levels for parallel execution"""

        levels: Dict[int, List[Subtask]] = {}
        subtask_levels: Dict[str, int] = {}

        # Compute level for each subtask
        def compute_level(subtask: Subtask) -> int:
            if subtask.subtask_id in subtask_levels:
                return subtask_levels[subtask.subtask_id]

            if not subtask.dependencies:
                level = 0
            else:
                # Find max level of dependencies
                dep_levels = []
                for dep_id in subtask.dependencies:
                    dep_subtask = next((st for st in subtasks if st.subtask_id == dep_id), None)
                    if dep_subtask:
                        dep_levels.append(compute_level(dep_subtask))
                level = max(dep_levels, default=0) + 1

            subtask_levels[subtask.subtask_id] = level
            return level

        # Group by level
        for subtask in subtasks:
            level = compute_level(subtask)
            if level not in levels:
                levels[level] = []
            levels[level].append(subtask)

        return levels

    async def _combine_ensemble_results(
        self,
        results: List[str]
    ) -> str:
        """Combine results from ensemble execution"""

        if not results:
            return ""

        if len(results) == 1:
            return results[0]

        # Use LLM to synthesize ensemble results
        synthesis_prompt = f"""
        Synthesize these {len(results)} results into a single, coherent response:

        {chr(10).join(f"Result {i+1}: {r}" for i, r in enumerate(results))}

        Provide a synthesized result that combines the best aspects of each.
        """

        routing_context = RoutingContext(
            task_type=TaskType.REASONING,
            prompt_length=len(synthesis_prompt),
            max_tokens=2000
        )

        model_id, model_config = await self.router.route_request(
            synthesis_prompt,
            routing_context
        )

        synthesized = await self._execute_llm_request(
            model_id,
            synthesis_prompt,
            model_config
        )

        return synthesized

    @trace_performance(operation='synthesize_results', component='multi_llm_orchestrator')
    @error_context(component='multi_llm_orchestrator', operation='synthesize_results')
    async def _synthesize_results(
        self,
        context: OrchestrationContext,
        subtask_results: Dict[str, Any]
    ) -> str:
        """Synthesize final result from all subtask results"""

        if not subtask_results:
            return "No results to synthesize"

        # Create synthesis prompt
        results_summary = "\n".join([
            f"{subtask_id}: {result}"
            for subtask_id, result in subtask_results.items()
        ])

        synthesis_prompt = f"""
        Original task: {context.main_task}

        Subtask results:
        {results_summary}

        Provide a final, comprehensive answer to the original task by synthesizing
        the subtask results.
        """

        routing_context = RoutingContext(
            task_type=TaskType.REASONING,
            prompt_length=len(synthesis_prompt),
            max_tokens=3000,
            priority="high"
        )

        model_id, model_config = await self.router.route_request(
            synthesis_prompt,
            routing_context
        )

        final_result = await self._execute_llm_request(
            model_id,
            synthesis_prompt,
            model_config
        )

        return final_result

    def _calculate_workflow_cost(self, context: OrchestrationContext) -> float:
        """Calculate total cost of workflow"""

        total_cost = 0.0

        for subtask in context.subtasks:
            if subtask.assigned_model and subtask.result:
                # Get model config
                model_config = self.router.models.get(subtask.assigned_model)
                if model_config:
                    # Estimate tokens
                    input_tokens = len(subtask.prompt) / 4
                    output_tokens = len(subtask.result) / 4

                    # Calculate cost
                    input_cost = (input_tokens / 1000) * model_config.cost_per_1k_tokens_input
                    output_cost = (output_tokens / 1000) * model_config.cost_per_1k_tokens_output

                    total_cost += input_cost + output_cost

        return total_cost

    def _generate_workflow_id(self, task: str) -> str:
        """Generate unique workflow ID"""
        timestamp = datetime.utcnow().isoformat()
        content = f"{task}{timestamp}"
        return hashlib.md5(content.encode()).hexdigest()[:16]

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get current status of active workflow"""

        if workflow_id not in self.active_workflows:
            return None

        context = self.active_workflows[workflow_id]

        return {
            'workflow_id': workflow_id,
            'strategy': context.strategy.value,
            'total_subtasks': len(context.subtasks),
            'completed_subtasks': len([st for st in context.subtasks if st.status == SubtaskStatus.COMPLETED]),
            'failed_subtasks': len([st for st in context.subtasks if st.status == SubtaskStatus.FAILED]),
            'running_subtasks': len([st for st in context.subtasks if st.status == SubtaskStatus.RUNNING]),
            'subtasks': [
                {
                    'id': st.subtask_id,
                    'status': st.status.value,
                    'model': st.assigned_model
                }
                for st in context.subtasks
            ]
        }

    def configure_ensemble(
        self,
        enabled: bool = True,
        confidence_threshold: float = 0.7,
        merge_strategy: str = 'weighted_consensus'
    ) -> None:
        """Configure ensemble execution parameters"""
        self.ensemble_enabled = enabled
        self.ensemble_confidence_threshold = confidence_threshold
        self.ensembler.merge_strategy = merge_strategy
        logger.info(
            f"[ORFEAS-ORCHESTRATOR] Ensemble configured: "
            f"enabled={enabled}, threshold={confidence_threshold}, strategy={merge_strategy}"
        )

    def get_ensemble_status(self) -> Dict[str, Any]:
        """Get current ensemble configuration and metrics"""
        return {
            'enabled': self.ensemble_enabled,
            'confidence_threshold': self.ensemble_confidence_threshold,
            'merge_strategy': getattr(self.ensembler, 'merge_strategy', 'weighted_consensus'),
            'available_models': len(self.router.models),
            'active_workflows': len(self.active_workflows)
        }


# Global orchestrator instance
_orchestrator_instance: Optional[MultiLLMOrchestrator] = None


def get_multi_llm_orchestrator() -> MultiLLMOrchestrator:
    """Get global multi-LLM orchestrator instance"""
    global _orchestrator_instance
    if _orchestrator_instance is None:
        _orchestrator_instance = MultiLLMOrchestrator()
    return _orchestrator_instance
