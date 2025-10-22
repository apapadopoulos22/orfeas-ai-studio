"""
ORFEAS AI 2Dâ†’3D Studio - Multi-LLM Orchestrator
==============================================
ORFEAS AI

Multi-LLM orchestration for complex multi-step tasks.
Coordinates multiple specialized LLMs for optimal task execution and result synthesis.
"""

import asyncio
import json
import logging
import time
from typing import Dict, List, Any, Optional, Tuple
import hashlib
from dataclasses import dataclass
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import uuid

from llm_integration import EnterpriseLLMManager, LLMRequest, LLMResponse

logger = logging.getLogger(__name__)

@dataclass
class SubTask:
    """Structure for decomposed subtasks"""
    id: str
    title: str
    description: str
    prompt: str
    task_type: str
    priority: int
    dependencies: List[str]
    context: Dict[str, Any]
    estimated_complexity: float

@dataclass
class TaskDecomposition:
    """Structure for task decomposition result"""
    original_task: str
    subtasks: List[SubTask]
    execution_order: List[str]
    estimated_total_time: float
    complexity_score: float

@dataclass
class LLMAssignment:
    """Structure for LLM assignment to subtasks"""
    subtask_id: str
    assigned_llm: str
    assignment_reason: str
    confidence: float
    fallback_llms: List[str]

@dataclass
class ExecutionResult:
    """Structure for subtask execution results"""
    subtask_id: str
    result: LLMResponse
    execution_time: float
    success: bool
    error_message: Optional[str]

class TaskDecomposer:
    """
    Intelligent task decomposition for multi-LLM coordination
    """

    def __init__(self):
        self.decomposition_patterns = self.load_decomposition_patterns()
        self.complexity_analyzer = ComplexityAnalyzer()

    def load_decomposition_patterns(self) -> Dict[str, Any]:
        """Load patterns for task decomposition"""
        return {
            'code_development': {
                'patterns': ['analysis', 'design', 'implementation', 'testing', 'documentation'],
                'complexity_factors': ['language_complexity', 'architecture_complexity', 'integration_points']
            },
            'content_creation': {
                'patterns': ['research', 'outline', 'writing', 'review', 'formatting'],
                'complexity_factors': ['content_length', 'technical_depth', 'audience_specificity']
            },
            'data_analysis': {
                'patterns': ['data_collection', 'preprocessing', 'analysis', 'visualization', 'reporting'],
                'complexity_factors': ['data_volume', 'analysis_complexity', 'visualization_requirements']
            },
            'problem_solving': {
                'patterns': ['problem_definition', 'research', 'solution_design', 'validation', 'implementation'],
                'complexity_factors': ['problem_complexity', 'solution_constraints', 'validation_requirements']
            }
        }

    def decompose_task(self, task_description: str, context: Dict[str, Any]) -> TaskDecomposition:
        """Decompose complex task into manageable subtasks"""

        # Analyze task to determine decomposition strategy
        task_type = self.classify_task_type(task_description)
        complexity_score = self.complexity_analyzer.analyze_task_complexity(task_description, context)

        # Get decomposition pattern
        pattern = self.decomposition_patterns.get(task_type, self.decomposition_patterns['problem_solving'])

        # Generate subtasks based on pattern
        subtasks = self.generate_subtasks(task_description, pattern, complexity_score, context)

        # Determine execution order
        execution_order = self.determine_execution_order(subtasks)

        # Estimate total time
        estimated_time = sum(subtask.estimated_complexity * 30 for subtask in subtasks)  # 30s per complexity unit

        return TaskDecomposition(
            original_task=task_description,
            subtasks=subtasks,
            execution_order=execution_order,
            estimated_total_time=estimated_time,
            complexity_score=complexity_score
        )

    def classify_task_type(self, task_description: str) -> str:
        """Classify task type for appropriate decomposition"""

        task_lower = task_description.lower()

        if any(keyword in task_lower for keyword in ['code', 'program', 'implement', 'develop', 'function', 'class']):
            return 'code_development'
        elif any(keyword in task_lower for keyword in ['write', 'create content', 'article', 'documentation', 'explain']):
            return 'content_creation'
        elif any(keyword in task_lower for keyword in ['analyze', 'data', 'statistics', 'visualize', 'report']):
            return 'data_analysis'
        else:
            return 'problem_solving'

    def generate_subtasks(self, task_description: str, pattern: Dict, complexity_score: float, context: Dict) -> List[SubTask]:
        """Generate specific subtasks based on pattern and task"""

        subtasks = []
        base_patterns = pattern['patterns']

        for i, pattern_step in enumerate(base_patterns):
            subtask_id = str(uuid.uuid4())

            # Generate specific subtask based on pattern step and original task
            subtask = self.create_specific_subtask(
                subtask_id, pattern_step, task_description, i, complexity_score, context
            )

            subtasks.append(subtask)

        return subtasks

    def create_specific_subtask(self, subtask_id: str, pattern_step: str, original_task: str,
                               step_index: int, complexity_score: float, context: Dict) -> SubTask:
        """Create specific subtask for pattern step"""

        # Generate subtask based on pattern step
        if pattern_step == 'analysis':
            title = "Task Analysis and Requirements"
            description = f"Analyze the requirements and constraints for: {original_task}"
            prompt = f"Analyze the following task and break down its requirements, constraints, and success criteria:\n\nTask: {original_task}\n\nProvide a detailed analysis including technical requirements, challenges, and recommended approach."
            task_type = "reasoning_analysis"

        elif pattern_step == 'design':
            title = "Solution Design"
            description = f"Design the solution architecture for: {original_task}"
            prompt = f"Design a comprehensive solution for the following task:\n\nTask: {original_task}\n\nInclude architecture, components, interfaces, and implementation strategy."
            task_type = "reasoning_analysis"

        elif pattern_step == 'implementation':
            title = "Implementation"
            description = f"Implement the solution for: {original_task}"
            prompt = f"Implement the solution for the following task based on previous analysis and design:\n\nTask: {original_task}\n\nProvide complete, working implementation with proper error handling and documentation."
            task_type = "code_generation"

        elif pattern_step == 'testing':
            title = "Testing and Validation"
            description = f"Create tests and validation for: {original_task}"
            prompt = f"Create comprehensive tests and validation procedures for the following task:\n\nTask: {original_task}\n\nInclude unit tests, integration tests, and validation criteria."
            task_type = "code_generation"

        elif pattern_step == 'documentation':
            title = "Documentation"
            description = f"Create documentation for: {original_task}"
            prompt = f"Create comprehensive documentation for the following completed task:\n\nTask: {original_task}\n\nInclude usage instructions, API documentation, and maintenance guidelines."
            task_type = "content_creation"

        elif pattern_step == 'research':
            title = "Research and Information Gathering"
            description = f"Research relevant information for: {original_task}"
            prompt = f"Research and gather relevant information for the following task:\n\nTask: {original_task}\n\nProvide comprehensive background information, best practices, and relevant examples."
            task_type = "reasoning_analysis"

        elif pattern_step == 'outline':
            title = "Content Outline"
            description = f"Create content outline for: {original_task}"
            prompt = f"Create a detailed outline for the following content creation task:\n\nTask: {original_task}\n\nInclude structure, key points, and content flow."
            task_type = "content_creation"

        elif pattern_step == 'writing':
            title = "Content Writing"
            description = f"Write content for: {original_task}"
            prompt = f"Write comprehensive content for the following task based on research and outline:\n\nTask: {original_task}\n\nEnsure clarity, accuracy, and engagement."
            task_type = "content_creation"

        elif pattern_step == 'review':
            title = "Review and Optimization"
            description = f"Review and optimize for: {original_task}"
            prompt = f"Review and optimize the work completed for the following task:\n\nTask: {original_task}\n\nIdentify improvements, errors, and optimization opportunities."
            task_type = "reasoning_analysis"

        else:
            title = f"{pattern_step.title()} Phase"
            description = f"Execute {pattern_step} phase for: {original_task}"
            prompt = f"Execute the {pattern_step} phase for the following task:\n\nTask: {original_task}\n\nProvide detailed output appropriate for this phase."
            task_type = "reasoning_analysis"

        # Set dependencies (each task depends on previous ones)
        dependencies = [f"step_{i}" for i in range(step_index)] if step_index > 0 else []

        # Estimate complexity based on task complexity and step type
        step_complexity_multipliers = {
            'analysis': 0.8,
            'design': 1.0,
            'implementation': 1.5,
            'testing': 1.2,
            'documentation': 0.9,
            'research': 0.7,
            'outline': 0.6,
            'writing': 1.1,
            'review': 0.8
        }

        estimated_complexity = complexity_score * step_complexity_multipliers.get(pattern_step, 1.0)

        return SubTask(
            id=subtask_id,
            title=title,
            description=description,
            prompt=prompt,
            task_type=task_type,
            priority=step_index + 1,
            dependencies=dependencies,
            context=context,
            estimated_complexity=estimated_complexity
        )

    def determine_execution_order(self, subtasks: List[SubTask]) -> List[str]:
        """Determine optimal execution order based on dependencies"""

        # For now, use simple priority-based ordering
        # In future, could implement more sophisticated dependency resolution
        ordered_subtasks = sorted(subtasks, key=lambda x: x.priority)
        return [subtask.id for subtask in ordered_subtasks]

class ComplexityAnalyzer:
    """
    Analyze task complexity for better resource allocation
    """

    def analyze_task_complexity(self, task_description: str, context: Dict[str, Any]) -> float:
        """Analyze and score task complexity (0.0 to 1.0)"""

        complexity_score = 0.3  # Base complexity

        # Length-based complexity
        word_count = len(task_description.split())
        if word_count > 100:
            complexity_score += 0.2
        elif word_count > 50:
            complexity_score += 0.1

        # Technical complexity indicators
        technical_keywords = [
            'algorithm', 'optimization', 'machine learning', 'neural network',
            'distributed', 'scalable', 'enterprise', 'security', 'performance',
            'integration', 'api', 'database', 'concurrent', 'async'
        ]

        technical_count = sum(1 for keyword in technical_keywords if keyword in task_description.lower())
        complexity_score += min(technical_count * 0.1, 0.3)

        # Context-based complexity
        if context.get('user_expertise') == 'beginner':
            complexity_score += 0.1
        elif context.get('user_expertise') == 'expert':
            complexity_score -= 0.1

        if context.get('time_constraint') == 'urgent':
            complexity_score += 0.1

        if context.get('quality_requirements') == 'enterprise':
            complexity_score += 0.15

        return min(1.0, max(0.1, complexity_score))

class ResultSynthesizer:
    """
    Synthesize results from multiple LLM executions
    """

    def synthesize_results(self, execution_results: Dict[str, ExecutionResult],
                          original_task: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Synthesize results from multiple subtask executions"""

        # Filter successful results
        successful_results = {k: v for k, v in execution_results.items() if v.success}

        if not successful_results:
            return {
                'success': False,
                'error': 'All subtasks failed',
                'details': execution_results
            }

        # Combine results based on task type
        task_type = self.classify_synthesis_type(original_task)

        if task_type == 'code_development':
            return self.synthesize_code_development(successful_results, original_task)
        elif task_type == 'content_creation':
            return self.synthesize_content_creation(successful_results, original_task)
        elif task_type == 'data_analysis':
            return self.synthesize_data_analysis(successful_results, original_task)
        else:
            return self.synthesize_general_task(successful_results, original_task)

    def classify_synthesis_type(self, task_description: str) -> str:
        """Classify task for appropriate synthesis strategy"""

        task_lower = task_description.lower()

        if any(keyword in task_lower for keyword in ['code', 'program', 'implement', 'develop']):
            return 'code_development'
        elif any(keyword in task_lower for keyword in ['write', 'create content', 'article', 'documentation']):
            return 'content_creation'
        elif any(keyword in task_lower for keyword in ['analyze', 'data', 'statistics', 'report']):
            return 'data_analysis'
        else:
            return 'general_task'

    def synthesize_code_development(self, results: Dict[str, ExecutionResult], original_task: str) -> Dict[str, Any]:
        """Synthesize code development results"""

        synthesis = {
            'task': original_task,
            'synthesis_type': 'code_development',
            'components': {}
        }

        # Extract different components
        for subtask_id, result in results.items():
            content = result.result.content

            if 'analysis' in result.result.metadata.get('task_type', ''):
                synthesis['components']['analysis'] = content
            elif 'implementation' in content.lower() or 'def ' in content or 'class ' in content:
                synthesis['components']['code'] = content
            elif 'test' in content.lower() or 'assert' in content:
                synthesis['components']['tests'] = content
            elif 'documentation' in content.lower() or '# ' in content:
                synthesis['components']['documentation'] = content

        # Create final synthesis
        final_result = self.create_code_synthesis(synthesis['components'])

        return {
            'success': True,
            'result': final_result,
            'components': synthesis['components'],
            'metadata': {
                'synthesis_type': 'code_development',
                'component_count': len(synthesis['components']),
                'quality_score': self.calculate_synthesis_quality(results)
            }
        }

    def synthesize_content_creation(self, results: Dict[str, ExecutionResult], original_task: str) -> Dict[str, Any]:
        """Synthesize content creation results"""

        content_parts = []
        metadata = {'synthesis_type': 'content_creation'}

        # Order results by subtask priority/order
        ordered_results = sorted(results.items(), key=lambda x: x[1].result.metadata.get('priority', 0))

        for subtask_id, result in ordered_results:
            content_parts.append(result.result.content)

        # Combine content parts
        final_content = self.combine_content_parts(content_parts)

        return {
            'success': True,
            'result': final_content,
            'metadata': {
                **metadata,
                'section_count': len(content_parts),
                'total_length': len(final_content),
                'quality_score': self.calculate_synthesis_quality(results)
            }
        }

    def synthesize_data_analysis(self, results: Dict[str, ExecutionResult], original_task: str) -> Dict[str, Any]:
        """Synthesize data analysis results"""

        analysis_components = {
            'data_collection': None,
            'preprocessing': None,
            'analysis': None,
            'visualization': None,
            'reporting': None
        }

        # Categorize results
        for subtask_id, result in results.items():
            content = result.result.content.lower()

            if 'data collection' in content or 'collect' in content:
                analysis_components['data_collection'] = result.result.content
            elif 'preprocess' in content or 'clean' in content:
                analysis_components['preprocessing'] = result.result.content
            elif 'analysis' in content or 'analyze' in content:
                analysis_components['analysis'] = result.result.content
            elif 'visualiz' in content or 'plot' in content or 'chart' in content:
                analysis_components['visualization'] = result.result.content
            elif 'report' in content or 'summary' in content:
                analysis_components['reporting'] = result.result.content

        # Create comprehensive analysis report
        final_report = self.create_analysis_report(analysis_components)

        return {
            'success': True,
            'result': final_report,
            'components': analysis_components,
            'metadata': {
                'synthesis_type': 'data_analysis',
                'component_count': sum(1 for v in analysis_components.values() if v),
                'quality_score': self.calculate_synthesis_quality(results)
            }
        }

    def synthesize_general_task(self, results: Dict[str, ExecutionResult], original_task: str) -> Dict[str, Any]:
        """Synthesize general task results"""

        # Simple concatenation with separators for general tasks
        content_parts = []

        for subtask_id, result in results.items():
            content_parts.append(f"## {result.result.metadata.get('subtask_title', 'Result')}\n\n{result.result.content}")

        final_result = "\n\n---\n\n".join(content_parts)

        return {
            'success': True,
            'result': final_result,
            'metadata': {
                'synthesis_type': 'general_task',
                'section_count': len(content_parts),
                'quality_score': self.calculate_synthesis_quality(results)
            }
        }

    def create_code_synthesis(self, components: Dict[str, str]) -> str:
        """Create synthesized code development result"""

        synthesis_parts = []

        if 'analysis' in components:
            synthesis_parts.append(f"# Analysis\n\n{components['analysis']}")

        if 'code' in components:
            synthesis_parts.append(f"# Implementation\n\n```python\n{components['code']}\n```")

        if 'tests' in components:
            synthesis_parts.append(f"# Tests\n\n```python\n{components['tests']}\n```")

        if 'documentation' in components:
            synthesis_parts.append(f"# Documentation\n\n{components['documentation']}")

        return "\n\n".join(synthesis_parts)

    def combine_content_parts(self, content_parts: List[str]) -> str:
        """Combine content parts into coherent document"""

        # Remove excessive whitespace and combine
        cleaned_parts = []
        for part in content_parts:
            cleaned = part.strip()
            if cleaned:
                cleaned_parts.append(cleaned)

        return "\n\n".join(cleaned_parts)

    def create_analysis_report(self, components: Dict[str, str]) -> str:
        """Create comprehensive analysis report"""

        report_parts = []

        component_order = ['data_collection', 'preprocessing', 'analysis', 'visualization', 'reporting']

        for component in component_order:
            if components.get(component):
                title = component.replace('_', ' ').title()
                report_parts.append(f"## {title}\n\n{components[component]}")

        return "\n\n".join(report_parts)

    def calculate_synthesis_quality(self, results: Dict[str, ExecutionResult]) -> float:
        """Calculate overall quality score for synthesis"""

        if not results:
            return 0.0

        # Average confidence scores from all results
        total_confidence = sum(result.result.confidence_score for result in results.values())
        avg_confidence = total_confidence / len(results)

        # Factor in success rate
        success_rate = sum(1 for result in results.values() if result.success) / len(results)

        # Combined quality score
        quality_score = (avg_confidence * 0.7) + (success_rate * 0.3)

        return quality_score

class MultiLLMOrchestrator:
    """
    Orchestrate multiple LLMs for complex multi-step tasks
    """

    def __init__(self):
        self.llm_manager = None  # Will be injected
        self.task_decomposer = TaskDecomposer()
        self.result_synthesizer = ResultSynthesizer()
        self.execution_metrics = {}

    def set_llm_manager(self, llm_manager: EnterpriseLLMManager):
        """Inject LLM manager dependency"""
        self.llm_manager = llm_manager

    async def execute_complex_task(self, task_description: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute complex task using multiple specialized LLMs"""

        if not self.llm_manager:
            raise RuntimeError("LLM Manager not initialized. Call set_llm_manager() first.")

        start_time = time.time()
        context = context or {}

        try:
            # 1. Decompose complex task into subtasks
            logger.info(f"[ORFEAS-ORCHESTRATOR] Decomposing task: {task_description[:100]}...")
            decomposition = self.task_decomposer.decompose_task(task_description, context)

            # 2. Assign optimal LLM for each subtask
            logger.info(f"[ORFEAS-ORCHESTRATOR] Assigning LLMs to {len(decomposition.subtasks)} subtasks")
            llm_assignments = self.assign_llms_to_subtasks(decomposition.subtasks)

            # 3. Execute subtasks in optimal order
            logger.info("[ORFEAS-ORCHESTRATOR] Executing subtasks with assigned LLMs")
            execution_results = await self.execute_subtasks_with_assignments(
                decomposition, llm_assignments, context
            )

            # 4. Synthesize results from multiple LLMs
            logger.info("[ORFEAS-ORCHESTRATOR] Synthesizing results from multiple LLM executions")
            final_result = self.result_synthesizer.synthesize_results(
                execution_results, task_description, context
            )

            total_time = time.time() - start_time

            # 5. Compile comprehensive response
            response = {
                'task_description': task_description,
                'final_result': final_result,
                'execution_breakdown': self.compile_execution_breakdown(execution_results, llm_assignments),
                'task_decomposition': {
                    'subtask_count': len(decomposition.subtasks),
                    'estimated_time': decomposition.estimated_total_time,
                    'actual_time': total_time,
                    'complexity_score': decomposition.complexity_score
                },
                'llm_usage': self.compile_llm_usage_stats(execution_results, llm_assignments),
                'performance_metrics': {
                    'total_execution_time': total_time,
                    'successful_subtasks': sum(1 for r in execution_results.values() if r.success),
                    'total_subtasks': len(execution_results),
                    'overall_success_rate': sum(1 for r in execution_results.values() if r.success) / len(execution_results),
                    'average_confidence': sum(r.result.confidence_score for r in execution_results.values() if r.success) /
                                        max(sum(1 for r in execution_results.values() if r.success), 1)
                }
            }

            # Update metrics
            self.update_orchestration_metrics(task_description, response)

            logger.info(f"[ORFEAS-ORCHESTRATOR] Task completed in {total_time:.2f}s with {response['performance_metrics']['overall_success_rate']:.1%} success rate")

            return response

        except Exception as e:
            logger.error(f"[ORFEAS-ORCHESTRATOR] Task execution failed: {e}")
            return {
                'task_description': task_description,
                'success': False,
                'error': str(e),
                'execution_time': time.time() - start_time
            }

    def assign_llms_to_subtasks(self, subtasks: List[SubTask]) -> Dict[str, LLMAssignment]:
        """Assign optimal LLMs to each subtask"""

        assignments = {}

        for subtask in subtasks:
            # Create LLM request for assignment analysis
            assignment_request = LLMRequest(
                prompt=subtask.prompt,
                context=subtask.context,
                task_type=subtask.task_type,
                priority="normal"
            )

            # Select optimal LLM
            optimal_llm = self.llm_manager.select_optimal_llm(assignment_request)

            # Determine fallback LLMs
            fallback_llms = self.get_fallback_llms(optimal_llm, subtask.task_type)

            # Create assignment
            assignments[subtask.id] = LLMAssignment(
                subtask_id=subtask.id,
                assigned_llm=optimal_llm,
                assignment_reason=f"Optimal for {subtask.task_type}",
                confidence=0.8,  # Base confidence
                fallback_llms=fallback_llms
            )

        return assignments

    def get_fallback_llms(self, primary_llm: str, task_type: str) -> List[str]:
        """Get fallback LLMs for task type"""

        fallback_chains = {
            'code_generation': ['claude_3_5_sonnet', 'gpt4_turbo', 'deepseek_coder'],
            'reasoning_analysis': ['gpt4_turbo', 'claude_3_5_sonnet', 'gemini_ultra'],
            'content_creation': ['claude_3_5_sonnet', 'gpt4_turbo', 'mistral_8x22b'],
            'multimodal_understanding': ['gemini_ultra', 'gpt4_turbo', 'claude_3_5_sonnet']
        }

        fallbacks = fallback_chains.get(task_type, ['claude_3_5_sonnet', 'gpt4_turbo'])

        # Remove primary LLM from fallbacks
        return [llm for llm in fallbacks if llm != primary_llm]

    async def execute_subtasks_with_assignments(self, decomposition: TaskDecomposition,
                                              assignments: Dict[str, LLMAssignment],
                                              context: Dict[str, Any]) -> Dict[str, ExecutionResult]:
        """Execute subtasks with assigned LLMs"""

        results = {}

        # Execute subtasks in dependency order
        for subtask_id in decomposition.execution_order:
            subtask = next(st for st in decomposition.subtasks if st.id == subtask_id)
            assignment = assignments[subtask_id]

            try:
                # Create LLM request
                llm_request = LLMRequest(
                    prompt=subtask.prompt,
                    context=subtask.context,
                    task_type=subtask.task_type,
                    priority="normal",
                    model_override=assignment.assigned_llm
                )

                # Execute with assigned LLM
                start_time = time.time()
                llm_response = await self.llm_manager.process_with_llm(llm_request)
                execution_time = time.time() - start_time

                # Create execution result
                results[subtask_id] = ExecutionResult(
                    subtask_id=subtask_id,
                    result=llm_response,
                    execution_time=execution_time,
                    success=True,
                    error_message=None
                )

                logger.info(f"[ORFEAS-ORCHESTRATOR] Subtask {subtask.title} completed successfully with {assignment.assigned_llm}")

            except Exception as e:
                logger.error(f"[ORFEAS-ORCHESTRATOR] Subtask {subtask.title} failed with {assignment.assigned_llm}: {e}")

                # Try fallback LLMs
                success = False
                for fallback_llm in assignment.fallback_llms:
                    try:
                        logger.info(f"[ORFEAS-ORCHESTRATOR] Attempting fallback to {fallback_llm}")

                        fallback_request = LLMRequest(
                            prompt=subtask.prompt,
                            context=subtask.context,
                            task_type=subtask.task_type,
                            priority="normal",
                            model_override=fallback_llm
                        )

                        start_time = time.time()
                        llm_response = await self.llm_manager.process_with_llm(fallback_request)
                        execution_time = time.time() - start_time

                        results[subtask_id] = ExecutionResult(
                            subtask_id=subtask_id,
                            result=llm_response,
                            execution_time=execution_time,
                            success=True,
                            error_message=None
                        )

                        success = True
                        logger.info(f"[ORFEAS-ORCHESTRATOR] Subtask {subtask.title} completed with fallback {fallback_llm}")
                        break

                    except Exception as fallback_error:
                        logger.warning(f"[ORFEAS-ORCHESTRATOR] Fallback {fallback_llm} also failed: {fallback_error}")
                        continue

                if not success:
                    # All LLMs failed for this subtask
                    results[subtask_id] = ExecutionResult(
                        subtask_id=subtask_id,
                        result=None,
                        execution_time=0,
                        success=False,
                        error_message=str(e)
                    )

        return results

    def compile_execution_breakdown(self, execution_results: Dict[str, ExecutionResult],
                                  assignments: Dict[str, LLMAssignment]) -> Dict[str, Any]:
        """Compile detailed execution breakdown"""

        breakdown = {
            'subtask_results': {},
            'llm_performance': {},
            'execution_summary': {
                'total_subtasks': len(execution_results),
                'successful_subtasks': sum(1 for r in execution_results.values() if r.success),
                'failed_subtasks': sum(1 for r in execution_results.values() if not r.success),
                'total_execution_time': sum(r.execution_time for r in execution_results.values())
            }
        }

        # Detailed subtask results
        for subtask_id, result in execution_results.items():
            assignment = assignments[subtask_id]

            breakdown['subtask_results'][subtask_id] = {
                'assigned_llm': assignment.assigned_llm,
                'success': result.success,
                'execution_time': result.execution_time,
                'confidence_score': result.result.confidence_score if result.result else 0,
                'token_count': result.result.token_count if result.result else 0,
                'error': result.error_message
            }

        # LLM performance summary
        llm_usage = {}
        for subtask_id, result in execution_results.items():
            if result.success and result.result:
                llm_used = result.result.model_used
                if llm_used not in llm_usage:
                    llm_usage[llm_used] = {
                        'subtasks_completed': 0,
                        'total_time': 0,
                        'avg_confidence': 0,
                        'total_tokens': 0
                    }

                llm_usage[llm_used]['subtasks_completed'] += 1
                llm_usage[llm_used]['total_time'] += result.execution_time
                llm_usage[llm_used]['total_tokens'] += result.result.token_count

                # Update average confidence
                current_avg = llm_usage[llm_used]['avg_confidence']
                count = llm_usage[llm_used]['subtasks_completed']
                llm_usage[llm_used]['avg_confidence'] = (current_avg * (count - 1) + result.result.confidence_score) / count

        breakdown['llm_performance'] = llm_usage

        return breakdown

    def compile_llm_usage_stats(self, execution_results: Dict[str, ExecutionResult],
                               assignments: Dict[str, LLMAssignment]) -> Dict[str, Any]:
        """Compile LLM usage statistics"""

        stats = {
            'llm_distribution': {},
            'fallback_usage': 0,
            'assignment_accuracy': 0
        }

        # Count LLM usage
        for subtask_id, result in execution_results.items():
            if result.success and result.result:
                llm_used = result.result.model_used
                if llm_used in stats['llm_distribution']:
                    stats['llm_distribution'][llm_used] += 1
                else:
                    stats['llm_distribution'][llm_used] = 1

                # Check if fallback was used
                assigned_llm = assignments[subtask_id].assigned_llm
                if llm_used != assigned_llm:
                    stats['fallback_usage'] += 1

        # Calculate assignment accuracy
        total_successful = sum(1 for r in execution_results.values() if r.success)
        if total_successful > 0:
            correct_assignments = total_successful - stats['fallback_usage']
            stats['assignment_accuracy'] = correct_assignments / total_successful

        return stats

    def update_orchestration_metrics(self, task_description: str, response: Dict[str, Any]):
        """Update orchestration performance metrics"""

        task_hash = hashlib.md5(task_description.encode()).hexdigest()[:8]

        self.execution_metrics[task_hash] = {
            'timestamp': datetime.utcnow().isoformat(),
            'task_description': task_description[:100],
            'execution_time': response['performance_metrics']['total_execution_time'],
            'success_rate': response['performance_metrics']['overall_success_rate'],
            'subtask_count': response['task_decomposition']['subtask_count'],
            'complexity_score': response['task_decomposition']['complexity_score'],
            'llm_usage': response['llm_usage']['llm_distribution']
        }

    def get_orchestration_metrics(self) -> Dict[str, Any]:
        """Get orchestration performance metrics"""

        if not self.execution_metrics:
            return {'message': 'No orchestration metrics available'}

        # Calculate summary statistics
        total_executions = len(self.execution_metrics)
        avg_execution_time = sum(m['execution_time'] for m in self.execution_metrics.values()) / total_executions
        avg_success_rate = sum(m['success_rate'] for m in self.execution_metrics.values()) / total_executions
        avg_complexity = sum(m['complexity_score'] for m in self.execution_metrics.values()) / total_executions

        # Most used LLMs
        llm_usage_count = {}
        for metrics in self.execution_metrics.values():
            for llm, count in metrics['llm_usage'].items():
                llm_usage_count[llm] = llm_usage_count.get(llm, 0) + count

        return {
            'summary': {
                'total_orchestrations': total_executions,
                'avg_execution_time': avg_execution_time,
                'avg_success_rate': avg_success_rate,
                'avg_complexity_score': avg_complexity,
                'most_used_llm': max(llm_usage_count, key=llm_usage_count.get) if llm_usage_count else None
            },
            'recent_executions': list(self.execution_metrics.values())[-10:],  # Last 10
            'llm_usage_distribution': llm_usage_count
        }

# Global orchestrator instance
_multi_llm_orchestrator = None

def get_multi_llm_orchestrator() -> MultiLLMOrchestrator:
    """Get singleton Multi-LLM Orchestrator instance"""
    global _multi_llm_orchestrator
    if _multi_llm_orchestrator is None:
        _multi_llm_orchestrator = MultiLLMOrchestrator()
    return _multi_llm_orchestrator

def initialize_orchestrator_system(llm_manager: EnterpriseLLMManager):
    """Initialize Multi-LLM Orchestrator system"""
    orchestrator = get_multi_llm_orchestrator()
    orchestrator.set_llm_manager(llm_manager)
    logger.info("[ORFEAS-ORCHESTRATOR] Multi-LLM Orchestrator system initialized")
    return orchestrator
