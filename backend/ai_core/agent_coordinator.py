"""
ORFEAS AI 2D→3D Studio - Agent Coordinator
===========================================
Multi-agent orchestration and coordination system.

Features:
- Agent capability discovery and registry
- Dynamic task delegation
- Multi-agent collaboration patterns
- Agent performance monitoring
- Load balancing across agents
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Set, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid

logger = logging.getLogger(__name__)


class AgentStatus(Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class CollaborationPattern(Enum):
    """Agent collaboration pattern"""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    HIERARCHICAL = "hierarchical"
    CONSENSUS = "consensus"


@dataclass
class AgentCapability:
    """Agent capability definition"""
    name: str
    description: str
    input_types: List[str]
    output_types: List[str]
    estimated_time_ms: int = 1000
    resource_requirements: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Agent:
    """Agent definition"""
    id: str
    name: str
    capabilities: List[AgentCapability]
    status: AgentStatus = AgentStatus.IDLE
    current_task_id: Optional[str] = None
    performance_score: float = 1.0
    total_tasks: int = 0
    successful_tasks: int = 0
    failed_tasks: int = 0
    avg_response_time_ms: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_active: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Task:
    """Task definition for agent execution"""
    id: str
    type: str
    input_data: Dict[str, Any]
    required_capabilities: List[str]
    priority: int = 5  # 1=highest, 10=lowest
    timeout_ms: int = 30000
    created_at: datetime = field(default_factory=datetime.utcnow)
    assigned_agent_id: Optional[str] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class CollaborationSession:
    """Multi-agent collaboration session"""
    id: str
    pattern: CollaborationPattern
    participating_agents: List[str]
    coordinator_agent_id: Optional[str] = None
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentCoordinator:
    """
    Multi-agent orchestration and coordination
    """

    def __init__(self):
        # Agent registry
        self.agents: Dict[str, Agent] = {}
        self.capability_index: Dict[str, List[str]] = {}  # capability -> agent_ids

        # Task management
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[Task] = []

        # Collaboration
        self.collaboration_sessions: Dict[str, CollaborationSession] = {}

        # Performance tracking
        self.total_tasks_delegated = 0
        self.successful_delegations = 0
        self.failed_delegations = 0

        # Agent communication (will be injected)
        self.communication = None

        logger.info("[ORFEAS-COORDINATOR] AgentCoordinator initialized")

    def register_agent(
        self,
        agent_id: str,
        name: str,
        capabilities: List[AgentCapability],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Agent:
        """
        Register a new agent

        Args:
            agent_id: Unique agent identifier
            name: Human-readable agent name
            capabilities: List of agent capabilities
            metadata: Additional metadata

        Returns:
            Registered Agent object
        """
        agent = Agent(
            id=agent_id,
            name=name,
            capabilities=capabilities,
            metadata=metadata or {}
        )

        self.agents[agent_id] = agent

        # Update capability index
        for capability in capabilities:
            if capability.name not in self.capability_index:
                self.capability_index[capability.name] = []
            self.capability_index[capability.name].append(agent_id)

        logger.info(
            f"[ORFEAS-COORDINATOR] Registered agent: {name} "
            f"(id={agent_id}, capabilities={len(capabilities)})"
        )

        return agent

    def unregister_agent(self, agent_id: str):
        """Unregister an agent"""
        if agent_id not in self.agents:
            logger.warning(f"[ORFEAS-COORDINATOR] Agent not found: {agent_id}")
            return

        agent = self.agents[agent_id]

        # Remove from capability index
        for capability in agent.capabilities:
            if capability.name in self.capability_index:
                self.capability_index[capability.name].remove(agent_id)
                if not self.capability_index[capability.name]:
                    del self.capability_index[capability.name]

        # Remove agent
        del self.agents[agent_id]

        logger.info(f"[ORFEAS-COORDINATOR] Unregistered agent: {agent.name} (id={agent_id})")

    def find_agents_by_capability(
        self,
        capability: str,
        status_filter: Optional[List[AgentStatus]] = None
    ) -> List[Agent]:
        """
        Find agents with specific capability

        Args:
            capability: Required capability name
            status_filter: Optional status filter

        Returns:
            List of matching agents
        """
        agent_ids = self.capability_index.get(capability, [])
        agents = [self.agents[aid] for aid in agent_ids if aid in self.agents]

        # Apply status filter
        if status_filter:
            agents = [a for a in agents if a.status in status_filter]

        return agents

    def select_best_agent(
        self,
        required_capabilities: List[str],
        task_type: Optional[str] = None
    ) -> Optional[Agent]:
        """
        Select best agent for task

        Selection criteria:
        1. Has all required capabilities
        2. Currently idle
        3. Highest performance score
        4. Lowest current workload

        Args:
            required_capabilities: List of required capabilities
            task_type: Optional task type for specialization

        Returns:
            Selected Agent or None if no suitable agent found
        """
        # Find agents with all required capabilities
        candidate_agents: Set[str] = None

        for capability in required_capabilities:
            capable_agents = set(self.capability_index.get(capability, []))

            if candidate_agents is None:
                candidate_agents = capable_agents
            else:
                candidate_agents = candidate_agents.intersection(capable_agents)

        if not candidate_agents:
            logger.warning(
                f"[ORFEAS-COORDINATOR] No agents found with capabilities: "
                f"{required_capabilities}"
            )
            return None

        # Filter to agents in registry and score them
        scored_agents = []

        for agent_id in candidate_agents:
            if agent_id not in self.agents:
                continue

            agent = self.agents[agent_id]

            # Skip busy or offline agents
            if agent.status not in [AgentStatus.IDLE]:
                continue

            # Calculate selection score
            score = self._calculate_agent_score(agent, required_capabilities)
            scored_agents.append((agent, score))

        if not scored_agents:
            logger.warning("[ORFEAS-COORDINATOR] No available agents found")
            return None

        # Select agent with highest score
        scored_agents.sort(key=lambda x: x[1], reverse=True)
        selected_agent = scored_agents[0][0]

        logger.info(
            f"[ORFEAS-COORDINATOR] Selected agent: {selected_agent.name} "
            f"(score={scored_agents[0][1]:.2f})"
        )

        return selected_agent

    def _calculate_agent_score(
        self,
        agent: Agent,
        required_capabilities: List[str]
    ) -> float:
        """Calculate agent selection score"""

        score = 0.0

        # Performance score (weight: 40%)
        score += agent.performance_score * 0.4

        # Success rate (weight: 30%)
        if agent.total_tasks > 0:
            success_rate = agent.successful_tasks / agent.total_tasks
            score += success_rate * 0.3
        else:
            score += 0.15  # Neutral score for new agents

        # Response time (weight: 20%)
        if agent.avg_response_time_ms > 0:
            # Lower response time is better
            time_score = max(0, 1.0 - (agent.avg_response_time_ms / 10000))
            score += time_score * 0.2
        else:
            score += 0.1

        # Idle bonus (weight: 10%)
        if agent.status == AgentStatus.IDLE:
            score += 0.1

        return score

    async def delegate_task(
        self,
        task: Task,
        agent: Optional[Agent] = None
    ) -> Dict[str, Any]:
        """
        Delegate task to agent

        Args:
            task: Task to delegate
            agent: Optional specific agent to use

        Returns:
            Task execution result
        """
        self.total_tasks_delegated += 1

        try:
            # Select agent if not provided
            if agent is None:
                agent = self.select_best_agent(task.required_capabilities, task.type)

                if agent is None:
                    raise ValueError("No suitable agent available")

            # Update task
            task.assigned_agent_id = agent.id
            task.status = "assigned"
            self.tasks[task.id] = task

            # Update agent status
            agent.status = AgentStatus.BUSY
            agent.current_task_id = task.id
            agent.last_active = datetime.utcnow()

            logger.info(
                f"[ORFEAS-COORDINATOR] Delegated task {task.id} "
                f"to agent {agent.name}"
            )

            # Execute task (would call actual agent)
            result = await self._execute_task_on_agent(task, agent)

            # Update statistics
            agent.total_tasks += 1
            if result.get('success', False):
                agent.successful_tasks += 1
                self.successful_delegations += 1
            else:
                agent.failed_tasks += 1
                self.failed_delegations += 1

            # Update response time
            execution_time = result.get('execution_time_ms', 0)
            if agent.avg_response_time_ms == 0:
                agent.avg_response_time_ms = execution_time
            else:
                # Exponential moving average
                agent.avg_response_time_ms = (
                    0.7 * agent.avg_response_time_ms + 0.3 * execution_time
                )

            # Update performance score
            self._update_agent_performance(agent, result)

            # Update task
            task.status = "completed" if result.get('success') else "failed"
            task.result = result.get('result')
            task.error = result.get('error')

            # Reset agent status
            agent.status = AgentStatus.IDLE
            agent.current_task_id = None

            return result

        except Exception as e:
            self.failed_delegations += 1
            logger.error(f"[ORFEAS-COORDINATOR] Task delegation failed: {e}")

            if agent:
                agent.status = AgentStatus.ERROR
                agent.current_task_id = None

            raise

    async def _execute_task_on_agent(
        self,
        task: Task,
        agent: Agent
    ) -> Dict[str, Any]:
        """Execute task on agent (placeholder)"""

        import time
        start_time = time.time()

        # Placeholder - would call actual agent
        await asyncio.sleep(0.1)

        execution_time = (time.time() - start_time) * 1000

        return {
            'success': True,
            'result': {'status': 'completed', 'output': 'placeholder'},
            'execution_time_ms': execution_time
        }

    def _update_agent_performance(self, agent: Agent, result: Dict[str, Any]):
        """Update agent performance score"""

        success = result.get('success', False)
        execution_time = result.get('execution_time_ms', 0)

        # Calculate performance delta
        delta = 0.0

        if success:
            delta += 0.05  # Bonus for success

            # Bonus for fast execution
            if execution_time < 1000:
                delta += 0.02
        else:
            delta -= 0.1  # Penalty for failure

        # Update score with decay
        agent.performance_score = max(0.0, min(1.0, agent.performance_score + delta * 0.1))

    async def coordinate_multi_agent_task(
        self,
        task: Task,
        pattern: CollaborationPattern = CollaborationPattern.SEQUENTIAL
    ) -> Dict[str, Any]:
        """
        Coordinate multi-agent task execution

        Args:
            task: Complex task requiring multiple agents
            pattern: Collaboration pattern to use

        Returns:
            Combined result from all agents
        """
        session_id = str(uuid.uuid4())

        # Decompose task (simplified)
        subtasks = self._decompose_task(task)

        # Create collaboration session
        session = CollaborationSession(
            id=session_id,
            pattern=pattern,
            participating_agents=[],
            metadata={'original_task_id': task.id}
        )

        self.collaboration_sessions[session_id] = session

        try:
            if pattern == CollaborationPattern.SEQUENTIAL:
                result = await self._sequential_execution(subtasks, session)
            elif pattern == CollaborationPattern.PARALLEL:
                result = await self._parallel_execution(subtasks, session)
            elif pattern == CollaborationPattern.HIERARCHICAL:
                result = await self._hierarchical_execution(subtasks, session)
            elif pattern == CollaborationPattern.CONSENSUS:
                result = await self._consensus_execution(subtasks, session)
            else:
                result = await self._sequential_execution(subtasks, session)

            session.status = "completed"

            return result

        except Exception as e:
            session.status = "failed"
            logger.error(f"[ORFEAS-COORDINATOR] Multi-agent coordination failed: {e}")
            raise

    def _decompose_task(self, task: Task) -> List[Task]:
        """Decompose complex task into subtasks"""

        # Simplified decomposition
        subtasks = [
            Task(
                id=f"{task.id}_sub_{i}",
                type=task.type,
                input_data=task.input_data,
                required_capabilities=task.required_capabilities[:1],
                priority=task.priority
            )
            for i in range(min(3, len(task.required_capabilities)))
        ]

        return subtasks

    async def _sequential_execution(
        self,
        subtasks: List[Task],
        session: CollaborationSession
    ) -> Dict[str, Any]:
        """Execute subtasks sequentially"""

        results = []

        for subtask in subtasks:
            result = await self.delegate_task(subtask)
            results.append(result)

            # Add agent to session
            if subtask.assigned_agent_id:
                if subtask.assigned_agent_id not in session.participating_agents:
                    session.participating_agents.append(subtask.assigned_agent_id)

        return {
            'success': all(r.get('success', False) for r in results),
            'results': results
        }

    async def _parallel_execution(
        self,
        subtasks: List[Task],
        session: CollaborationSession
    ) -> Dict[str, Any]:
        """Execute subtasks in parallel"""

        # Create coroutines for all subtasks
        coroutines = [self.delegate_task(subtask) for subtask in subtasks]

        # Execute in parallel
        results = await asyncio.gather(*coroutines, return_exceptions=True)

        # Update session
        for subtask in subtasks:
            if subtask.assigned_agent_id:
                if subtask.assigned_agent_id not in session.participating_agents:
                    session.participating_agents.append(subtask.assigned_agent_id)

        # Handle exceptions
        valid_results = []
        for result in results:
            if isinstance(result, Exception):
                valid_results.append({'success': False, 'error': str(result)})
            else:
                valid_results.append(result)

        return {
            'success': all(r.get('success', False) for r in valid_results),
            'results': valid_results
        }

    async def _hierarchical_execution(
        self,
        subtasks: List[Task],
        session: CollaborationSession
    ) -> Dict[str, Any]:
        """Execute subtasks hierarchically with coordinator"""

        # Select coordinator agent
        if subtasks:
            coordinator = self.select_best_agent(subtasks[0].required_capabilities)
            if coordinator:
                session.coordinator_agent_id = coordinator.id

        # Execute subtasks under coordinator
        results = []
        for subtask in subtasks:
            result = await self.delegate_task(subtask)
            results.append(result)

            if subtask.assigned_agent_id:
                if subtask.assigned_agent_id not in session.participating_agents:
                    session.participating_agents.append(subtask.assigned_agent_id)

        return {
            'success': all(r.get('success', False) for r in results),
            'results': results,
            'coordinator': session.coordinator_agent_id
        }

    async def _consensus_execution(
        self,
        subtasks: List[Task],
        session: CollaborationSession
    ) -> Dict[str, Any]:
        """Execute subtasks and reach consensus"""

        # Execute all subtasks
        results = await self._parallel_execution(subtasks, session)

        # Voting mechanism (simplified)
        if results['success']:
            # All agents succeeded - use majority vote
            return {
                'success': True,
                'results': results['results'],
                'consensus': 'unanimous'
            }
        else:
            # Some failures - use best result
            valid_results = [r for r in results['results'] if r.get('success')]

            if valid_results:
                return {
                    'success': True,
                    'results': valid_results,
                    'consensus': 'majority'
                }
            else:
                return {
                    'success': False,
                    'results': results['results'],
                    'consensus': 'failed'
                }

    def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get agent status"""
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]

        return {
            'id': agent.id,
            'name': agent.name,
            'status': agent.status.value,
            'current_task_id': agent.current_task_id,
            'performance_score': agent.performance_score,
            'total_tasks': agent.total_tasks,
            'success_rate': agent.successful_tasks / agent.total_tasks if agent.total_tasks > 0 else 0,
            'avg_response_time_ms': agent.avg_response_time_ms,
            'capabilities': [c.name for c in agent.capabilities]
        }

    def get_statistics(self) -> Dict[str, Any]:
        """Get coordinator statistics"""

        total_agents = len(self.agents)
        idle_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.IDLE)
        busy_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.BUSY)
        error_agents = sum(1 for a in self.agents.values() if a.status == AgentStatus.ERROR)

        success_rate = (
            self.successful_delegations / self.total_tasks_delegated * 100
            if self.total_tasks_delegated > 0 else 0
        )

        return {
            'total_agents': total_agents,
            'idle_agents': idle_agents,
            'busy_agents': busy_agents,
            'error_agents': error_agents,
            'total_tasks_delegated': self.total_tasks_delegated,
            'successful_delegations': self.successful_delegations,
            'failed_delegations': self.failed_delegations,
            'success_rate': f"{success_rate:.1f}%",
            'active_collaboration_sessions': len([
                s for s in self.collaboration_sessions.values()
                if s.status == 'active'
            ])
        }


# Global agent coordinator instance
_agent_coordinator: Optional[AgentCoordinator] = None


def get_agent_coordinator() -> AgentCoordinator:
    """Get global agent coordinator instance"""
    global _agent_coordinator
    if _agent_coordinator is None:
        _agent_coordinator = AgentCoordinator()
    return _agent_coordinator
