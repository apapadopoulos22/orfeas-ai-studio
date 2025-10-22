"""
ORFEAS AI 2D→3D Studio - Agent Orchestration Module
===================================================
Implements multi-agent coordination, agent registry, and agent communication protocols.
"""
import threading
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

class AgentMessage:
    """
    Message structure for agent communication.
    """
    def __init__(self, sender_id: str, recipient_id: str, task_type: str, payload: Dict[str, Any]):
        self.message_id = str(uuid.uuid4())
        self.sender_id = sender_id
        self.recipient_id = recipient_id
        self.task_type = task_type
        self.payload = payload
        self.context_hash = self._calculate_context_hash()
        self.timestamp = datetime.utcnow()
        self.version = "1.0"

    def _calculate_context_hash(self) -> str:
        # Simple context hash for demonstration
        return str(hash(f"{self.sender_id}:{self.recipient_id}:{self.task_type}"))

class AgentRegistry:
    """
    Registry for all available agents and their capabilities.
    """
    def __init__(self):
        self._agents: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def register_agent(self, agent_id: str, agent_type: str, capabilities: List[str]):
        with self._lock:
            self._agents[agent_id] = {
                'type': agent_type,
                'capabilities': capabilities,
                'last_seen': datetime.utcnow()
            }

    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        return self._agents.get(agent_id)

    def find_agents(self, capability: str) -> List[str]:
        return [aid for aid, info in self._agents.items() if capability in info['capabilities']]

    def update_last_seen(self, agent_id: str):
        if agent_id in self._agents:
            self._agents[agent_id]['last_seen'] = datetime.utcnow()

class AgentCoordinator:
    """
    Coordinates multi-agent workflows and message passing.
    """
    def __init__(self, registry: AgentRegistry):
        self.registry = registry
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self._lock = threading.Lock()

    def assign_task(self, task_type: str, payload: Dict[str, Any], required_capability: str) -> Optional[str]:
        agent_ids = self.registry.find_agents(required_capability)
        if not agent_ids:
            return None
        agent_id = agent_ids[0]  # Simple round-robin or selection logic
        task_id = str(uuid.uuid4())
        with self._lock:
            self.active_tasks[task_id] = {
                'agent_id': agent_id,
                'task_type': task_type,
                'payload': payload,
                'status': 'assigned',
                'timestamp': datetime.utcnow()
            }
        return task_id

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        return self.active_tasks.get(task_id)

    def update_task_status(self, task_id: str, status: str):
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = status
            self.active_tasks[task_id]['last_update'] = datetime.utcnow()

# Example usage (to be integrated in Flask endpoints or agent runners):
# registry = AgentRegistry()
# registry.register_agent('agent1', 'quality_agent', ['quality_assessment', 'image_analysis'])
# coordinator = AgentCoordinator(registry)
# task_id = coordinator.assign_task('quality_check', {'image': 'img.png'}, 'quality_assessment')
# status = coordinator.get_task_status(task_id)
