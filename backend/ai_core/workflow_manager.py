"""
ORFEAS AI 2D→3D Studio - Workflow Manager
=========================================
Intelligent workflow execution engine with error recovery.

Features:
- Workflow definition and execution
- Dynamic workflow adaptation
- Error recovery with automatic retry
- Checkpoint and resume capabilities
- Performance optimization
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)


class WorkflowStatus(Enum):
    """Workflow execution status"""
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(Enum):
    """Workflow step status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class RetryStrategy(Enum):
    """Retry strategy for failed steps"""
    NO_RETRY = "no_retry"
    FIXED_INTERVAL = "fixed_interval"
    EXPONENTIAL_BACKOFF = "exponential_backoff"
    ADAPTIVE = "adaptive"


@dataclass
class WorkflowStep:
    """Single step in workflow"""
    id: str
    name: str
    handler: Callable
    input_mapping: Optional[Dict[str, str]] = None
    output_mapping: Optional[Dict[str, str]] = None
    dependencies: List[str] = field(default_factory=list)
    timeout_seconds: float = 60.0
    retry_strategy: RetryStrategy = RetryStrategy.EXPONENTIAL_BACKOFF
    max_retries: int = 3
    required: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepExecution:
    """Step execution record"""
    step_id: str
    status: StepStatus = StepStatus.PENDING
    attempts: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    result: Optional[Any] = None
    error: Optional[str] = None
    execution_time_ms: float = 0.0


@dataclass
class Checkpoint:
    """Workflow checkpoint"""
    checkpoint_id: str
    workflow_id: str
    completed_steps: List[str]
    step_results: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Workflow:
    """Workflow definition"""
    id: str
    name: str
    steps: List[WorkflowStep]
    status: WorkflowStatus = WorkflowStatus.PENDING
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    step_executions: Dict[str, StepExecution] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    checkpoint_ids: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class WorkflowManager:
    """
    Intelligent workflow execution engine
    """

    def __init__(self):
        # Workflow registry
        self.workflows: Dict[str, Workflow] = {}

        # Checkpoint storage
        self.checkpoints: Dict[str, Checkpoint] = {}

        # Workflow templates
        self.templates: Dict[str, List[WorkflowStep]] = {}

        # Statistics
        self.total_workflows_executed = 0
        self.successful_workflows = 0
        self.failed_workflows = 0

        # Configuration
        self.enable_checkpointing = True
        self.checkpoint_interval_steps = 5

        logger.info("[ORFEAS-WORKFLOW] WorkflowManager initialized")

    def create_workflow(
        self,
        name: str,
        steps: List[WorkflowStep],
        context: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """
        Create new workflow

        Args:
            name: Workflow name
            steps: Workflow steps
            context: Initial context
            metadata: Additional metadata

        Returns:
            Created Workflow object
        """
        workflow_id = str(uuid.uuid4())

        workflow = Workflow(
            id=workflow_id,
            name=name,
            steps=steps,
            context=context or {},
            metadata=metadata or {}
        )

        # Initialize step executions
        for step in steps:
            workflow.step_executions[step.id] = StepExecution(step_id=step.id)

        self.workflows[workflow_id] = workflow

        logger.info(
            f"[ORFEAS-WORKFLOW] Created workflow: {name} "
            f"(id={workflow_id}, steps={len(steps)})"
        )

        return workflow

    def register_template(self, template_name: str, steps: List[WorkflowStep]):
        """Register workflow template"""
        self.templates[template_name] = steps
        logger.info(f"[ORFEAS-WORKFLOW] Registered template: {template_name}")

    def create_from_template(
        self,
        template_name: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Workflow:
        """Create workflow from template"""
        if template_name not in self.templates:
            raise ValueError(f"Template not found: {template_name}")

        steps = self.templates[template_name]
        return self.create_workflow(
            name=f"workflow_from_{template_name}",
            steps=steps,
            context=context
        )

    async def execute_workflow(
        self,
        workflow: Workflow,
        resume_from_checkpoint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute workflow

        Args:
            workflow: Workflow to execute
            resume_from_checkpoint: Optional checkpoint to resume from

        Returns:
            Workflow execution result
        """
        self.total_workflows_executed += 1

        workflow.status = WorkflowStatus.RUNNING
        workflow.started_at = datetime.utcnow()

        logger.info(f"[ORFEAS-WORKFLOW] Starting workflow: {workflow.name} (id={workflow.id})")

        try:
            # Resume from checkpoint if provided
            if resume_from_checkpoint:
                await self._resume_from_checkpoint(workflow, resume_from_checkpoint)

            # Execute steps
            await self._execute_steps(workflow)

            # Mark as completed
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.utcnow()

            self.successful_workflows += 1

            logger.info(f"[ORFEAS-WORKFLOW] Completed workflow: {workflow.name}")

            return {
                'success': True,
                'workflow_id': workflow.id,
                'status': workflow.status.value,
                'results': self._collect_results(workflow),
                'execution_time_ms': self._calculate_execution_time(workflow)
            }

        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            self.failed_workflows += 1

            logger.error(f"[ORFEAS-WORKFLOW] Workflow failed: {workflow.name} - {e}")

            return {
                'success': False,
                'workflow_id': workflow.id,
                'status': workflow.status.value,
                'error': str(e),
                'completed_steps': self._get_completed_steps(workflow)
            }

    async def _execute_steps(self, workflow: Workflow):
        """Execute workflow steps with dependency resolution"""

        pending_steps = {step.id: step for step in workflow.steps}
        completed_steps = set()

        while pending_steps:
            # Find executable steps (dependencies satisfied)
            executable_steps = []

            for step_id, step in pending_steps.items():
                if all(dep in completed_steps for dep in step.dependencies):
                    executable_steps.append(step)

            if not executable_steps:
                # No executable steps - check for circular dependencies
                if pending_steps:
                    raise RuntimeError(
                        f"Circular dependency detected or unsatisfied dependencies: "
                        f"{list(pending_steps.keys())}"
                    )
                break

            # Execute steps (parallel execution for independent steps)
            execution_tasks = [
                self._execute_step(workflow, step)
                for step in executable_steps
            ]

            results = await asyncio.gather(*execution_tasks, return_exceptions=True)

            # Process results
            for step, result in zip(executable_steps, results):
                if isinstance(result, Exception):
                    if step.required:
                        raise result
                    else:
                        # Non-required step failed - mark as skipped
                        execution = workflow.step_executions[step.id]
                        execution.status = StepStatus.SKIPPED
                        execution.error = str(result)

                completed_steps.add(step.id)
                del pending_steps[step.id]

            # Create checkpoint if enabled
            if self.enable_checkpointing:
                if len(completed_steps) % self.checkpoint_interval_steps == 0:
                    await self._create_checkpoint(workflow, list(completed_steps))

    async def _execute_step(self, workflow: Workflow, step: WorkflowStep):
        """Execute single workflow step with retry logic"""

        execution = workflow.step_executions[step.id]
        execution.status = StepStatus.RUNNING
        execution.start_time = datetime.utcnow()

        logger.debug(f"[ORFEAS-WORKFLOW] Executing step: {step.name} (id={step.id})")

        attempt = 0
        last_error = None

        while attempt <= step.max_retries:
            try:
                execution.attempts = attempt + 1

                # Prepare input
                step_input = self._prepare_step_input(workflow, step)

                # Execute with timeout
                result = await asyncio.wait_for(
                    step.handler(step_input, workflow.context),
                    timeout=step.timeout_seconds
                )

                # Process output
                self._process_step_output(workflow, step, result)

                # Mark as completed
                execution.status = StepStatus.COMPLETED
                execution.end_time = datetime.utcnow()
                execution.result = result
                execution.execution_time_ms = (
                    (execution.end_time - execution.start_time).total_seconds() * 1000
                )

                logger.debug(
                    f"[ORFEAS-WORKFLOW] Step completed: {step.name} "
                    f"(attempts={attempt + 1}, time={execution.execution_time_ms:.1f}ms)"
                )

                return result

            except asyncio.TimeoutError as e:
                last_error = f"Step timeout after {step.timeout_seconds}s"
                logger.warning(f"[ORFEAS-WORKFLOW] {last_error}")

            except Exception as e:
                last_error = str(e)
                logger.warning(f"[ORFEAS-WORKFLOW] Step error: {e}")

            # Retry logic
            attempt += 1
            if attempt <= step.max_retries:
                retry_delay = self._calculate_retry_delay(step.retry_strategy, attempt)
                logger.info(
                    f"[ORFEAS-WORKFLOW] Retrying step {step.name} "
                    f"in {retry_delay:.1f}s (attempt {attempt + 1}/{step.max_retries + 1})"
                )
                await asyncio.sleep(retry_delay)

        # All retries exhausted
        execution.status = StepStatus.FAILED
        execution.end_time = datetime.utcnow()
        execution.error = last_error

        raise RuntimeError(f"Step failed after {step.max_retries + 1} attempts: {last_error}")

    def _prepare_step_input(self, workflow: Workflow, step: WorkflowStep) -> Dict[str, Any]:
        """Prepare input for step execution"""

        step_input = {}

        if step.input_mapping:
            for step_key, context_key in step.input_mapping.items():
                if context_key in workflow.context:
                    step_input[step_key] = workflow.context[context_key]
        else:
            # No mapping - use entire context
            step_input = workflow.context.copy()

        return step_input

    def _process_step_output(self, workflow: Workflow, step: WorkflowStep, result: Any):
        """Process step output and update context"""

        if step.output_mapping:
            if isinstance(result, dict):
                for result_key, context_key in step.output_mapping.items():
                    if result_key in result:
                        workflow.context[context_key] = result[result_key]
        else:
            # No mapping - store result with step id
            workflow.context[f"step_{step.id}_result"] = result

    def _calculate_retry_delay(self, strategy: RetryStrategy, attempt: int) -> float:
        """Calculate retry delay based on strategy"""

        if strategy == RetryStrategy.NO_RETRY:
            return 0.0
        elif strategy == RetryStrategy.FIXED_INTERVAL:
            return 1.0
        elif strategy == RetryStrategy.EXPONENTIAL_BACKOFF:
            return min(2 ** attempt, 60.0)  # Max 60 seconds
        elif strategy == RetryStrategy.ADAPTIVE:
            # Adaptive based on attempt
            return min(attempt * 2.0, 30.0)
        else:
            return 1.0

    async def _create_checkpoint(self, workflow: Workflow, completed_steps: List[str]):
        """Create workflow checkpoint"""

        checkpoint_id = str(uuid.uuid4())

        # Collect step results
        step_results = {}
        for step_id in completed_steps:
            execution = workflow.step_executions[step_id]
            if execution.result is not None:
                step_results[step_id] = execution.result

        checkpoint = Checkpoint(
            checkpoint_id=checkpoint_id,
            workflow_id=workflow.id,
            completed_steps=completed_steps,
            step_results=step_results
        )

        self.checkpoints[checkpoint_id] = checkpoint
        workflow.checkpoint_ids.append(checkpoint_id)

        logger.debug(
            f"[ORFEAS-WORKFLOW] Created checkpoint: {checkpoint_id} "
            f"(steps={len(completed_steps)})"
        )

    async def _resume_from_checkpoint(self, workflow: Workflow, checkpoint_id: str):
        """Resume workflow from checkpoint"""

        if checkpoint_id not in self.checkpoints:
            raise ValueError(f"Checkpoint not found: {checkpoint_id}")

        checkpoint = self.checkpoints[checkpoint_id]

        # Restore completed steps
        for step_id in checkpoint.completed_steps:
            if step_id in workflow.step_executions:
                execution = workflow.step_executions[step_id]
                execution.status = StepStatus.COMPLETED
                execution.result = checkpoint.step_results.get(step_id)

        # Restore context
        workflow.context.update(checkpoint.step_results)

        logger.info(
            f"[ORFEAS-WORKFLOW] Resumed from checkpoint: {checkpoint_id} "
            f"(steps={len(checkpoint.completed_steps)})"
        )

    def _collect_results(self, workflow: Workflow) -> Dict[str, Any]:
        """Collect results from all completed steps"""

        results = {}

        for step_id, execution in workflow.step_executions.items():
            if execution.status == StepStatus.COMPLETED and execution.result is not None:
                results[step_id] = execution.result

        return results

    def _get_completed_steps(self, workflow: Workflow) -> List[str]:
        """Get list of completed step IDs"""

        return [
            step_id
            for step_id, execution in workflow.step_executions.items()
            if execution.status == StepStatus.COMPLETED
        ]

    def _calculate_execution_time(self, workflow: Workflow) -> float:
        """Calculate total workflow execution time"""

        if workflow.started_at and workflow.completed_at:
            return (workflow.completed_at - workflow.started_at).total_seconds() * 1000
        return 0.0

    async def pause_workflow(self, workflow_id: str):
        """Pause workflow execution"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.PAUSED

        logger.info(f"[ORFEAS-WORKFLOW] Paused workflow: {workflow_id}")

    async def cancel_workflow(self, workflow_id: str):
        """Cancel workflow execution"""
        if workflow_id not in self.workflows:
            raise ValueError(f"Workflow not found: {workflow_id}")

        workflow = self.workflows[workflow_id]
        workflow.status = WorkflowStatus.CANCELLED
        workflow.completed_at = datetime.utcnow()

        logger.info(f"[ORFEAS-WORKFLOW] Cancelled workflow: {workflow_id}")

    def get_workflow_status(self, workflow_id: str) -> Optional[Dict[str, Any]]:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            return None

        workflow = self.workflows[workflow_id]

        completed_steps = len([
            e for e in workflow.step_executions.values()
            if e.status == StepStatus.COMPLETED
        ])

        return {
            'workflow_id': workflow.id,
            'name': workflow.name,
            'status': workflow.status.value,
            'total_steps': len(workflow.steps),
            'completed_steps': completed_steps,
            'progress': completed_steps / len(workflow.steps) * 100 if workflow.steps else 0,
            'started_at': workflow.started_at.isoformat() if workflow.started_at else None,
            'execution_time_ms': self._calculate_execution_time(workflow)
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get workflow manager statistics"""

        success_rate = (
            self.successful_workflows / self.total_workflows_executed * 100
            if self.total_workflows_executed > 0 else 0
        )

        return {
            'total_workflows_executed': self.total_workflows_executed,
            'successful_workflows': self.successful_workflows,
            'failed_workflows': self.failed_workflows,
            'success_rate': f"{success_rate:.1f}%",
            'active_workflows': len([
                w for w in self.workflows.values()
                if w.status == WorkflowStatus.RUNNING
            ]),
            'total_checkpoints': len(self.checkpoints),
            'registered_templates': len(self.templates)
        }


# Global workflow manager instance
_workflow_manager: Optional[WorkflowManager] = None


def get_workflow_manager() -> WorkflowManager:
    """Get global workflow manager instance"""
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager()
    return _workflow_manager
