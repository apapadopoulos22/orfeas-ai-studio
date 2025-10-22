"""
ORFEAS AI Advanced Agent Communication & Coordination
=====================================================
Enterprise-grade agent communication protocols, message passing,
and distributed coordination systems.

Features:
- Inter-agent communication networks
- Message passing and coordination protocols
- Service discovery and health monitoring
- Load balancing and failover mechanisms
- Real-time agent collaboration
"""

import asyncio
import json
import logging
import time
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Any, Dict, List, Optional, Callable, Set
from datetime import datetime, timedelta
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor
import hashlib

# Message bus and networking
try:
    import aioredis
    import aiohttp
    from aiohttp import web
    NETWORKING_AVAILABLE = True
except ImportError:
    NETWORKING_AVAILABLE = False

logger = logging.getLogger(__name__)

class MessageType(Enum):
    """Types of agent messages"""
    TASK_REQUEST = "task_request"
    TASK_RESPONSE = "task_response"
    COORDINATION_REQUEST = "coordination_request"
    COORDINATION_RESPONSE = "coordination_response"
    STATUS_UPDATE = "status_update"
    HEALTH_CHECK = "health_check"
    DISCOVERY_ANNOUNCEMENT = "discovery_announcement"
    ERROR_NOTIFICATION = "error_notification"
    PERFORMANCE_METRICS = "performance_metrics"

class MessagePriority(Enum):
    """Message priority levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class AgentMessage:
    """Agent communication message"""
    id: str
    type: MessageType
    sender_id: str
    recipient_id: Optional[str]  # None for broadcast
    payload: Dict[str, Any]
    priority: MessagePriority = MessagePriority.MEDIUM
    correlation_id: Optional[str] = None
    timestamp: datetime = None
    expires_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3

    def __post_init__(self):
        if self.id is None:
            self.id = str(uuid.uuid4())
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.expires_at is None:
            self.expires_at = self.timestamp + timedelta(minutes=5)  # Default 5 min expiry

@dataclass
class AgentEndpoint:
    """Agent endpoint information"""
    agent_id: str
    agent_type: str
    capabilities: List[str]
    endpoint_url: str
    status: str = "active"
    last_heartbeat: datetime = None
    performance_metrics: Dict[str, Any] = None

    def __post_init__(self):
        if self.last_heartbeat is None:
            self.last_heartbeat = datetime.utcnow()
        if self.performance_metrics is None:
            self.performance_metrics = {}

class MessageHandler(ABC):
    """Base class for message handlers"""

    @abstractmethod
    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle incoming message and optionally return response"""
        pass

    @abstractmethod
    def can_handle(self, message_type: MessageType) -> bool:
        """Check if handler can process this message type"""
        pass

class AgentMessageBus:
    """Enterprise agent message bus for inter-agent communication"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis_client = None
        self.message_handlers: Dict[MessageType, List[MessageHandler]] = {}
        self.subscription_tasks: Dict[str, asyncio.Task] = {}
        self.agent_id = None
        self.running = False

        # Message routing and delivery
        self.message_queue = asyncio.Queue()
        self.delivery_confirmations: Dict[str, asyncio.Event] = {}
        self.pending_messages: Dict[str, AgentMessage] = {}

        # Performance tracking
        self.message_stats = {
            'sent': 0,
            'received': 0,
            'failed': 0,
            'retries': 0
        }

    async def initialize(self, agent_id: str):
        """Initialize message bus"""
        self.agent_id = agent_id

        if NETWORKING_AVAILABLE:
            try:
                self.redis_client = aioredis.from_url(self.redis_url)
                await self.redis_client.ping()
                logger.info(f"[MESSAGE-BUS] Connected to Redis: {self.redis_url}")
            except Exception as e:
                logger.warning(f"[MESSAGE-BUS] Redis unavailable, using local queue: {e}")
                self.redis_client = None
        else:
            logger.info("[MESSAGE-BUS] Using local message queue (Redis not available)")

        self.running = True

        # Start message processing loop
        asyncio.create_task(self._message_processing_loop())

        logger.info(f"[MESSAGE-BUS] Initialized for agent: {agent_id}")

    async def shutdown(self):
        """Shutdown message bus"""
        self.running = False

        # Cancel subscription tasks
        for task in self.subscription_tasks.values():
            task.cancel()

        # Close Redis connection
        if self.redis_client:
            await self.redis_client.close()

        logger.info("[MESSAGE-BUS] Shutdown complete")

    def register_handler(self, message_type: MessageType, handler: MessageHandler):
        """Register message handler"""
        if message_type not in self.message_handlers:
            self.message_handlers[message_type] = []

        self.message_handlers[message_type].append(handler)
        logger.info(f"[MESSAGE-BUS] Registered handler for: {message_type.value}")

    async def send_message(self, message: AgentMessage) -> bool:
        """Send message to another agent"""
        try:
            # Validate message
            if not self._validate_message(message):
                return False

            # Set sender ID
            message.sender_id = self.agent_id

            # Serialize message
            message_data = self._serialize_message(message)

            if self.redis_client:
                # Send via Redis
                if message.recipient_id:
                    # Direct message
                    channel = f"agent:{message.recipient_id}"
                    await self.redis_client.publish(channel, message_data)
                else:
                    # Broadcast message
                    channel = "agent:broadcast"
                    await self.redis_client.publish(channel, message_data)
            else:
                # Local delivery
                await self.message_queue.put(message)

            self.message_stats['sent'] += 1
            logger.debug(f"[MESSAGE-BUS] Sent message: {message.id}")
            return True

        except Exception as e:
            logger.error(f"[MESSAGE-BUS] Failed to send message: {e}")
            self.message_stats['failed'] += 1
            return False

    async def send_request(self, message: AgentMessage, timeout: float = 30.0) -> Optional[AgentMessage]:
        """Send request and wait for response"""
        # Generate correlation ID
        message.correlation_id = str(uuid.uuid4())

        # Setup response waiter
        response_event = asyncio.Event()
        response_message = None

        def response_handler(response: AgentMessage):
            nonlocal response_message
            if response.correlation_id == message.correlation_id:
                response_message = response
                response_event.set()

        # Register temporary response handler
        self._register_correlation_handler(message.correlation_id, response_handler)

        try:
            # Send request
            success = await self.send_message(message)
            if not success:
                return None

            # Wait for response
            await asyncio.wait_for(response_event.wait(), timeout=timeout)
            return response_message

        except asyncio.TimeoutError:
            logger.warning(f"[MESSAGE-BUS] Request timeout: {message.id}")
            return None
        finally:
            # Cleanup correlation handler
            self._unregister_correlation_handler(message.correlation_id)

    async def subscribe_to_messages(self, agent_id: str):
        """Subscribe to messages for this agent"""
        if not self.redis_client:
            return

        # Subscribe to direct messages
        direct_channel = f"agent:{agent_id}"
        direct_task = asyncio.create_task(
            self._subscribe_to_channel(direct_channel)
        )
        self.subscription_tasks[direct_channel] = direct_task

        # Subscribe to broadcast messages
        broadcast_channel = "agent:broadcast"
        broadcast_task = asyncio.create_task(
            self._subscribe_to_channel(broadcast_channel)
        )
        self.subscription_tasks[broadcast_channel] = broadcast_task

        logger.info(f"[MESSAGE-BUS] Subscribed to channels for agent: {agent_id}")

    async def _subscribe_to_channel(self, channel: str):
        """Subscribe to a specific Redis channel"""
        try:
            pubsub = self.redis_client.pubsub()
            await pubsub.subscribe(channel)

            async for message in pubsub.listen():
                if message['type'] == 'message':
                    try:
                        agent_message = self._deserialize_message(message['data'])
                        if agent_message:
                            await self._process_received_message(agent_message)
                    except Exception as e:
                        logger.error(f"[MESSAGE-BUS] Error processing message: {e}")

        except Exception as e:
            logger.error(f"[MESSAGE-BUS] Subscription error for {channel}: {e}")

    async def _message_processing_loop(self):
        """Main message processing loop"""
        while self.running:
            try:
                # Process local queue (for non-Redis setups)
                if not self.redis_client:
                    try:
                        message = await asyncio.wait_for(
                            self.message_queue.get(), timeout=1.0
                        )
                        await self._process_received_message(message)
                    except asyncio.TimeoutError:
                        continue
                else:
                    await asyncio.sleep(0.1)

            except Exception as e:
                logger.error(f"[MESSAGE-BUS] Processing loop error: {e}")
                await asyncio.sleep(1.0)

    async def _process_received_message(self, message: AgentMessage):
        """Process received message"""
        try:
            # Skip messages from self
            if message.sender_id == self.agent_id:
                return

            # Check message expiry
            if message.expires_at and datetime.utcnow() > message.expires_at:
                logger.warning(f"[MESSAGE-BUS] Expired message: {message.id}")
                return

            self.message_stats['received'] += 1

            # Handle correlation responses
            if message.correlation_id and message.type == MessageType.TASK_RESPONSE:
                self._handle_correlation_response(message)
                return

            # Find handlers
            handlers = self.message_handlers.get(message.type, [])

            for handler in handlers:
                if handler.can_handle(message.type):
                    try:
                        response = await handler.handle_message(message)

                        # Send response if generated
                        if response:
                            response.recipient_id = message.sender_id
                            response.correlation_id = message.correlation_id
                            await self.send_message(response)

                    except Exception as e:
                        logger.error(f"[MESSAGE-BUS] Handler error: {e}")

            logger.debug(f"[MESSAGE-BUS] Processed message: {message.id}")

        except Exception as e:
            logger.error(f"[MESSAGE-BUS] Message processing error: {e}")

    def _validate_message(self, message: AgentMessage) -> bool:
        """Validate message before sending"""
        if not message.id:
            logger.error("[MESSAGE-BUS] Message missing ID")
            return False

        if not message.type:
            logger.error("[MESSAGE-BUS] Message missing type")
            return False

        if not message.payload:
            logger.error("[MESSAGE-BUS] Message missing payload")
            return False

        return True

    def _serialize_message(self, message: AgentMessage) -> str:
        """Serialize message to JSON"""
        message_dict = asdict(message)

        # Convert datetime objects to ISO strings
        if message_dict['timestamp']:
            message_dict['timestamp'] = message.timestamp.isoformat()
        if message_dict['expires_at']:
            message_dict['expires_at'] = message.expires_at.isoformat()

        # Convert enums to strings
        message_dict['type'] = message.type.value
        message_dict['priority'] = message.priority.value

        return json.dumps(message_dict)

    def _deserialize_message(self, message_data: str) -> Optional[AgentMessage]:
        """Deserialize message from JSON"""
        try:
            message_dict = json.loads(message_data)

            # Convert ISO strings back to datetime objects
            if message_dict.get('timestamp'):
                message_dict['timestamp'] = datetime.fromisoformat(message_dict['timestamp'])
            if message_dict.get('expires_at'):
                message_dict['expires_at'] = datetime.fromisoformat(message_dict['expires_at'])

            # Convert strings back to enums
            message_dict['type'] = MessageType(message_dict['type'])
            message_dict['priority'] = MessagePriority(message_dict['priority'])

            return AgentMessage(**message_dict)

        except Exception as e:
            logger.error(f"[MESSAGE-BUS] Deserialization error: {e}")
            return None

    def _register_correlation_handler(self, correlation_id: str, handler: Callable):
        """Register temporary correlation handler"""
        # Implementation for request-response correlation
        pass

    def _unregister_correlation_handler(self, correlation_id: str):
        """Unregister correlation handler"""
        # Implementation for cleanup
        pass

    def _handle_correlation_response(self, message: AgentMessage):
        """Handle correlated response message"""
        # Implementation for response handling
        pass

    def get_message_stats(self) -> Dict[str, Any]:
        """Get message bus statistics"""
        return {
            'stats': self.message_stats,
            'active_subscriptions': len(self.subscription_tasks),
            'pending_messages': len(self.pending_messages),
            'agent_id': self.agent_id,
            'redis_connected': self.redis_client is not None
        }

class AgentServiceDiscovery:
    """Service discovery for agents"""

    def __init__(self, message_bus: AgentMessageBus):
        self.message_bus = message_bus
        self.registered_agents: Dict[str, AgentEndpoint] = {}
        self.discovery_interval = 30.0  # seconds
        self.heartbeat_timeout = 60.0  # seconds
        self.running = False

        # Health monitoring
        self.health_check_interval = 10.0
        self.unhealthy_agents: Set[str] = set()

    async def start(self):
        """Start service discovery"""
        self.running = True

        # Start discovery and health monitoring tasks
        asyncio.create_task(self._discovery_loop())
        asyncio.create_task(self._health_monitoring_loop())

        logger.info("[SERVICE-DISCOVERY] Started")

    async def stop(self):
        """Stop service discovery"""
        self.running = False
        logger.info("[SERVICE-DISCOVERY] Stopped")

    async def register_agent(self, endpoint: AgentEndpoint):
        """Register agent endpoint"""
        self.registered_agents[endpoint.agent_id] = endpoint

        # Announce to other agents
        announcement = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.DISCOVERY_ANNOUNCEMENT,
            sender_id=endpoint.agent_id,
            recipient_id=None,  # Broadcast
            payload={
                'action': 'register',
                'agent_endpoint': asdict(endpoint)
            }
        )

        await self.message_bus.send_message(announcement)
        logger.info(f"[SERVICE-DISCOVERY] Registered agent: {endpoint.agent_id}")

    async def unregister_agent(self, agent_id: str):
        """Unregister agent endpoint"""
        if agent_id in self.registered_agents:
            del self.registered_agents[agent_id]

            # Announce to other agents
            announcement = AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.DISCOVERY_ANNOUNCEMENT,
                sender_id=agent_id,
                recipient_id=None,  # Broadcast
                payload={
                    'action': 'unregister',
                    'agent_id': agent_id
                }
            )

            await self.message_bus.send_message(announcement)
            logger.info(f"[SERVICE-DISCOVERY] Unregistered agent: {agent_id}")

    def find_agents_by_capability(self, capability: str) -> List[AgentEndpoint]:
        """Find agents with specific capability"""
        matching_agents = []

        for endpoint in self.registered_agents.values():
            if capability in endpoint.capabilities and endpoint.agent_id not in self.unhealthy_agents:
                matching_agents.append(endpoint)

        # Sort by performance metrics (if available)
        matching_agents.sort(
            key=lambda x: x.performance_metrics.get('success_rate', 0.0),
            reverse=True
        )

        return matching_agents

    def find_agent_by_type(self, agent_type: str) -> Optional[AgentEndpoint]:
        """Find agent by type"""
        for endpoint in self.registered_agents.values():
            if endpoint.agent_type == agent_type and endpoint.agent_id not in self.unhealthy_agents:
                return endpoint
        return None

    def get_all_agents(self) -> List[AgentEndpoint]:
        """Get all registered agents"""
        return [
            endpoint for endpoint in self.registered_agents.values()
            if endpoint.agent_id not in self.unhealthy_agents
        ]

    async def _discovery_loop(self):
        """Discovery heartbeat loop"""
        while self.running:
            try:
                # Send discovery heartbeat
                heartbeat = AgentMessage(
                    id=str(uuid.uuid4()),
                    type=MessageType.DISCOVERY_ANNOUNCEMENT,
                    sender_id=self.message_bus.agent_id,
                    recipient_id=None,  # Broadcast
                    payload={
                        'action': 'heartbeat',
                        'timestamp': datetime.utcnow().isoformat()
                    }
                )

                await self.message_bus.send_message(heartbeat)
                await asyncio.sleep(self.discovery_interval)

            except Exception as e:
                logger.error(f"[SERVICE-DISCOVERY] Discovery loop error: {e}")
                await asyncio.sleep(5.0)

    async def _health_monitoring_loop(self):
        """Health monitoring loop"""
        while self.running:
            try:
                current_time = datetime.utcnow()

                # Check for stale agents
                stale_agents = []
                for agent_id, endpoint in self.registered_agents.items():
                    time_since_heartbeat = current_time - endpoint.last_heartbeat
                    if time_since_heartbeat.total_seconds() > self.heartbeat_timeout:
                        stale_agents.append(agent_id)
                        self.unhealthy_agents.add(agent_id)

                # Remove stale agents
                for agent_id in stale_agents:
                    logger.warning(f"[SERVICE-DISCOVERY] Agent stale: {agent_id}")
                    del self.registered_agents[agent_id]

                await asyncio.sleep(self.health_check_interval)

            except Exception as e:
                logger.error(f"[SERVICE-DISCOVERY] Health monitoring error: {e}")
                await asyncio.sleep(5.0)

    def update_agent_heartbeat(self, agent_id: str):
        """Update agent heartbeat timestamp"""
        if agent_id in self.registered_agents:
            self.registered_agents[agent_id].last_heartbeat = datetime.utcnow()
            self.unhealthy_agents.discard(agent_id)

    def update_agent_performance(self, agent_id: str, metrics: Dict[str, Any]):
        """Update agent performance metrics"""
        if agent_id in self.registered_agents:
            self.registered_agents[agent_id].performance_metrics.update(metrics)

    def get_discovery_status(self) -> Dict[str, Any]:
        """Get service discovery status"""
        agent_summary = {}
        for agent_type in set(endpoint.agent_type for endpoint in self.registered_agents.values()):
            agents_of_type = [
                endpoint for endpoint in self.registered_agents.values()
                if endpoint.agent_type == agent_type
            ]
            agent_summary[agent_type] = {
                'count': len(agents_of_type),
                'healthy': len([a for a in agents_of_type if a.agent_id not in self.unhealthy_agents]),
                'agents': [
                    {
                        'id': a.agent_id,
                        'status': a.status,
                        'last_seen': a.last_heartbeat.isoformat(),
                        'healthy': a.agent_id not in self.unhealthy_agents
                    } for a in agents_of_type
                ]
            }

        return {
            'total_agents': len(self.registered_agents),
            'healthy_agents': len(self.registered_agents) - len(self.unhealthy_agents),
            'unhealthy_agents': len(self.unhealthy_agents),
            'agent_summary': agent_summary
        }

class AgentLoadBalancer:
    """Load balancer for agent requests"""

    def __init__(self, service_discovery: AgentServiceDiscovery):
        self.service_discovery = service_discovery
        self.request_counts: Dict[str, int] = {}
        self.response_times: Dict[str, List[float]] = {}
        self.selection_strategies = {
            'round_robin': self._round_robin_selection,
            'least_connections': self._least_connections_selection,
            'performance_based': self._performance_based_selection,
            'capability_based': self._capability_based_selection
        }
        self.default_strategy = 'performance_based'

    def select_agent(self, capability: str, strategy: str = None) -> Optional[AgentEndpoint]:
        """Select optimal agent for request"""
        strategy = strategy or self.default_strategy

        # Get available agents with capability
        available_agents = self.service_discovery.find_agents_by_capability(capability)

        if not available_agents:
            return None

        # Apply selection strategy
        selection_func = self.selection_strategies.get(strategy, self._performance_based_selection)
        return selection_func(available_agents)

    def record_request(self, agent_id: str, response_time: float, success: bool):
        """Record request metrics for load balancing"""
        # Update request count
        self.request_counts[agent_id] = self.request_counts.get(agent_id, 0) + 1

        # Update response times
        if agent_id not in self.response_times:
            self.response_times[agent_id] = []

        self.response_times[agent_id].append(response_time)

        # Keep only recent response times (last 100)
        if len(self.response_times[agent_id]) > 100:
            self.response_times[agent_id] = self.response_times[agent_id][-100:]

    def _round_robin_selection(self, agents: List[AgentEndpoint]) -> AgentEndpoint:
        """Round-robin agent selection"""
        if not agents:
            return None

        # Simple round-robin based on request counts
        min_requests = min(self.request_counts.get(agent.agent_id, 0) for agent in agents)
        candidates = [agent for agent in agents if self.request_counts.get(agent.agent_id, 0) == min_requests]

        return candidates[0] if candidates else agents[0]

    def _least_connections_selection(self, agents: List[AgentEndpoint]) -> AgentEndpoint:
        """Least connections agent selection"""
        if not agents:
            return None

        # Select agent with fewest active connections (approximated by recent requests)
        min_connections = min(self.request_counts.get(agent.agent_id, 0) for agent in agents)
        candidates = [agent for agent in agents if self.request_counts.get(agent.agent_id, 0) == min_connections]

        return candidates[0] if candidates else agents[0]

    def _performance_based_selection(self, agents: List[AgentEndpoint]) -> AgentEndpoint:
        """Performance-based agent selection"""
        if not agents:
            return None

        best_agent = None
        best_score = -1

        for agent in agents:
            score = self._calculate_performance_score(agent)
            if score > best_score:
                best_score = score
                best_agent = agent

        return best_agent or agents[0]

    def _capability_based_selection(self, agents: List[AgentEndpoint]) -> AgentEndpoint:
        """Capability-based agent selection"""
        if not agents:
            return None

        # Select agent with most capabilities (most versatile)
        max_capabilities = max(len(agent.capabilities) for agent in agents)
        candidates = [agent for agent in agents if len(agent.capabilities) == max_capabilities]

        # Among equally capable agents, select by performance
        return self._performance_based_selection(candidates)

    def _calculate_performance_score(self, agent: AgentEndpoint) -> float:
        """Calculate performance score for agent"""
        score = 0.0

        # Performance metrics from agent
        metrics = agent.performance_metrics
        if metrics:
            score += metrics.get('success_rate', 0.0) * 0.4
            score += (1.0 - min(metrics.get('average_execution_time', 1.0), 1.0)) * 0.3
            score += metrics.get('quality_score', 0.0) * 0.3

        # Response time performance
        response_times = self.response_times.get(agent.agent_id, [])
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            # Normalize response time (lower is better)
            response_score = max(0.0, 1.0 - (avg_response_time / 10.0))  # 10s as baseline
            score += response_score * 0.2

        # Request count penalty (avoid overloading)
        request_count = self.request_counts.get(agent.agent_id, 0)
        if request_count > 0:
            load_penalty = min(request_count / 100.0, 0.5)  # Max 50% penalty
            score -= load_penalty

        return max(0.0, score)

    def get_load_balancer_stats(self) -> Dict[str, Any]:
        """Get load balancer statistics"""
        return {
            'request_counts': self.request_counts,
            'avg_response_times': {
                agent_id: sum(times) / len(times) if times else 0.0
                for agent_id, times in self.response_times.items()
            },
            'available_agents': len(self.service_discovery.get_all_agents()),
            'strategies': list(self.selection_strategies.keys()),
            'default_strategy': self.default_strategy
        }

class AgentCoordinationProtocol:
    """Protocol for coordinating complex multi-agent tasks"""

    def __init__(self, message_bus: AgentMessageBus, service_discovery: AgentServiceDiscovery, load_balancer: AgentLoadBalancer):
        self.message_bus = message_bus
        self.service_discovery = service_discovery
        self.load_balancer = load_balancer
        self.active_coordinations: Dict[str, Dict[str, Any]] = {}
        self.coordination_timeout = 300.0  # 5 minutes

    async def coordinate_task(self, task_definition: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate complex multi-agent task"""
        coordination_id = str(uuid.uuid4())

        # Parse task definition
        required_capabilities = task_definition.get('required_capabilities', [])
        task_steps = task_definition.get('steps', [])
        dependencies = task_definition.get('dependencies', {})

        # Create coordination context
        coordination_context = {
            'id': coordination_id,
            'task_definition': task_definition,
            'required_capabilities': required_capabilities,
            'steps': task_steps,
            'dependencies': dependencies,
            'started_at': datetime.utcnow(),
            'status': 'initializing',
            'agent_assignments': {},
            'step_results': {},
            'completed_steps': set(),
            'failed_steps': set()
        }

        self.active_coordinations[coordination_id] = coordination_context

        try:
            # Phase 1: Agent selection and assignment
            await self._assign_agents_to_capabilities(coordination_context)

            # Phase 2: Execute coordination workflow
            coordination_context['status'] = 'executing'
            result = await self._execute_coordination_workflow(coordination_context)

            # Phase 3: Aggregate results
            coordination_context['status'] = 'completed'
            final_result = self._aggregate_coordination_results(coordination_context, result)

            return final_result

        except Exception as e:
            coordination_context['status'] = 'failed'
            logger.error(f"[COORDINATION] Task {coordination_id} failed: {e}")
            return {
                'success': False,
                'coordination_id': coordination_id,
                'error': str(e),
                'partial_results': coordination_context.get('step_results', {})
            }
        finally:
            # Cleanup
            if coordination_id in self.active_coordinations:
                del self.active_coordinations[coordination_id]

    async def _assign_agents_to_capabilities(self, context: Dict[str, Any]):
        """Assign agents to required capabilities"""
        required_capabilities = context['required_capabilities']
        agent_assignments = {}

        for capability in required_capabilities:
            # Find best agent for capability
            selected_agent = self.load_balancer.select_agent(capability)

            if not selected_agent:
                raise RuntimeError(f"No agent available for capability: {capability}")

            agent_assignments[capability] = selected_agent.agent_id
            logger.info(f"[COORDINATION] Assigned {selected_agent.agent_id} to {capability}")

        context['agent_assignments'] = agent_assignments

    async def _execute_coordination_workflow(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute coordinated workflow"""
        steps = context['steps']
        dependencies = context['dependencies']
        step_results = {}

        # Execute steps in dependency order
        while len(context['completed_steps']) < len(steps):
            # Find executable steps (dependencies satisfied)
            executable_steps = []

            for step in steps:
                step_name = step['name']

                if step_name in context['completed_steps'] or step_name in context['failed_steps']:
                    continue

                # Check dependencies
                step_deps = dependencies.get(step_name, [])
                if all(dep in context['completed_steps'] for dep in step_deps):
                    executable_steps.append(step)

            if not executable_steps:
                # Check for circular dependencies or failures
                remaining_steps = [s for s in steps if s['name'] not in context['completed_steps'] and s['name'] not in context['failed_steps']]
                if remaining_steps:
                    raise RuntimeError("Circular dependencies or all remaining steps blocked")
                break

            # Execute steps in parallel
            step_tasks = []
            for step in executable_steps:
                task = asyncio.create_task(self._execute_coordination_step(step, context))
                step_tasks.append((step['name'], task))

            # Wait for step completion
            for step_name, task in step_tasks:
                try:
                    result = await task
                    step_results[step_name] = result
                    context['completed_steps'].add(step_name)
                    logger.info(f"[COORDINATION] Completed step: {step_name}")
                except Exception as e:
                    logger.error(f"[COORDINATION] Step {step_name} failed: {e}")
                    context['failed_steps'].add(step_name)
                    step_results[step_name] = {'success': False, 'error': str(e)}

        context['step_results'] = step_results
        return step_results

    async def _execute_coordination_step(self, step: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single coordination step"""
        step_name = step['name']
        required_capability = step['required_capability']
        step_payload = step.get('payload', {})

        # Get assigned agent
        agent_id = context['agent_assignments'].get(required_capability)
        if not agent_id:
            raise RuntimeError(f"No agent assigned for capability: {required_capability}")

        # Create coordination message
        coord_message = AgentMessage(
            id=str(uuid.uuid4()),
            type=MessageType.COORDINATION_REQUEST,
            sender_id=self.message_bus.agent_id,
            recipient_id=agent_id,
            payload={
                'coordination_id': context['id'],
                'step_name': step_name,
                'step_definition': step,
                'context': {
                    'previous_results': context.get('step_results', {}),
                    'global_context': step_payload
                }
            },
            priority=MessagePriority.HIGH
        )

        # Send request and wait for response
        response = await self.message_bus.send_request(coord_message, timeout=60.0)

        if not response:
            raise RuntimeError(f"No response from agent {agent_id} for step {step_name}")

        return response.payload

    def _aggregate_coordination_results(self, context: Dict[str, Any], step_results: Dict[str, Any]) -> Dict[str, Any]:
        """Aggregate coordination results"""
        successful_steps = [step for step, result in step_results.items() if result.get('success', False)]
        failed_steps = [step for step, result in step_results.items() if not result.get('success', False)]

        # Calculate overall success
        total_steps = len(context['steps'])
        success_rate = len(successful_steps) / total_steps if total_steps > 0 else 0.0
        overall_success = success_rate >= 0.8  # 80% success threshold

        # Calculate quality score
        quality_scores = [
            result.get('quality_score', 0.0)
            for result in step_results.values()
            if result.get('success', False)
        ]
        overall_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0

        return {
            'success': overall_success,
            'coordination_id': context['id'],
            'total_steps': total_steps,
            'successful_steps': len(successful_steps),
            'failed_steps': len(failed_steps),
            'success_rate': success_rate,
            'overall_quality_score': overall_quality,
            'step_results': step_results,
            'execution_time': (datetime.utcnow() - context['started_at']).total_seconds(),
            'agent_assignments': context['agent_assignments']
        }

    def get_coordination_status(self, coordination_id: str) -> Optional[Dict[str, Any]]:
        """Get status of active coordination"""
        context = self.active_coordinations.get(coordination_id)
        if not context:
            return None

        return {
            'coordination_id': coordination_id,
            'status': context['status'],
            'progress': {
                'total_steps': len(context['steps']),
                'completed_steps': len(context['completed_steps']),
                'failed_steps': len(context['failed_steps']),
                'completion_percentage': len(context['completed_steps']) / len(context['steps']) * 100 if context['steps'] else 0
            },
            'agent_assignments': context['agent_assignments'],
            'elapsed_time': (datetime.utcnow() - context['started_at']).total_seconds()
        }

    def get_all_coordinations(self) -> Dict[str, Any]:
        """Get status of all active coordinations"""
        return {
            coord_id: self.get_coordination_status(coord_id)
            for coord_id in self.active_coordinations.keys()
        }

# Global communication system instance
_communication_system = None

class AgentCommunicationSystem:
    """Unified agent communication system"""

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.message_bus = AgentMessageBus(redis_url)
        self.service_discovery = AgentServiceDiscovery(self.message_bus)
        self.load_balancer = AgentLoadBalancer(self.service_discovery)
        self.coordination_protocol = AgentCoordinationProtocol(
            self.message_bus, self.service_discovery, self.load_balancer
        )
        self.initialized = False

    async def initialize(self, agent_id: str):
        """Initialize communication system"""
        await self.message_bus.initialize(agent_id)
        await self.service_discovery.start()
        await self.message_bus.subscribe_to_messages(agent_id)

        self.initialized = True
        logger.info(f"[COMMUNICATION-SYSTEM] Initialized for agent: {agent_id}")

    async def shutdown(self):
        """Shutdown communication system"""
        await self.service_discovery.stop()
        await self.message_bus.shutdown()

        self.initialized = False
        logger.info("[COMMUNICATION-SYSTEM] Shutdown complete")

    def get_system_status(self) -> Dict[str, Any]:
        """Get overall system status"""
        return {
            'initialized': self.initialized,
            'message_bus': self.message_bus.get_message_stats(),
            'service_discovery': self.service_discovery.get_discovery_status(),
            'load_balancer': self.load_balancer.get_load_balancer_stats(),
            'active_coordinations': len(self.coordination_protocol.active_coordinations)
        }

def get_agent_communication_system() -> AgentCommunicationSystem:
    """Get global agent communication system"""
    global _communication_system
    if _communication_system is None:
        _communication_system = AgentCommunicationSystem()
    return _communication_system

# Example message handlers
class TaskRequestHandler(MessageHandler):
    """Handler for task request messages"""

    def __init__(self, agent_executor):
        self.agent_executor = agent_executor

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle task request message"""
        try:
            task_data = message.payload
            result = await self.agent_executor.execute_task(task_data)

            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.TASK_RESPONSE,
                sender_id=message.recipient_id,
                recipient_id=message.sender_id,
                payload=result,
                correlation_id=message.correlation_id
            )

        except Exception as e:
            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.TASK_RESPONSE,
                sender_id=message.recipient_id,
                recipient_id=message.sender_id,
                payload={'success': False, 'error': str(e)},
                correlation_id=message.correlation_id
            )

    def can_handle(self, message_type: MessageType) -> bool:
        """Check if can handle message type"""
        return message_type == MessageType.TASK_REQUEST

class CoordinationRequestHandler(MessageHandler):
    """Handler for coordination request messages"""

    def __init__(self, agent_executor):
        self.agent_executor = agent_executor

    async def handle_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Handle coordination request message"""
        try:
            coord_data = message.payload
            step_definition = coord_data['step_definition']
            context = coord_data.get('context', {})

            # Execute coordination step
            result = await self.agent_executor.execute_coordination_step(step_definition, context)

            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.COORDINATION_RESPONSE,
                sender_id=message.recipient_id,
                recipient_id=message.sender_id,
                payload=result,
                correlation_id=message.correlation_id
            )

        except Exception as e:
            return AgentMessage(
                id=str(uuid.uuid4()),
                type=MessageType.COORDINATION_RESPONSE,
                sender_id=message.recipient_id,
                recipient_id=message.sender_id,
                payload={'success': False, 'error': str(e)},
                correlation_id=message.correlation_id
            )

    def can_handle(self, message_type: MessageType) -> bool:
        """Check if can handle message type"""
        return message_type == MessageType.COORDINATION_REQUEST

if __name__ == "__main__":
    async def test_communication_system():
        """Test the agent communication system"""
        print("Testing Agent Communication System...")

        # Initialize communication system
        comm_system = get_agent_communication_system()
        await comm_system.initialize("test_agent_001")

        # Test message bus
        print("\n=== Message Bus Test ===")
        stats = comm_system.message_bus.get_message_stats()
        print(f"Message Bus Stats: {stats}")

        # Test service discovery
        print("\n=== Service Discovery Test ===")
        discovery_status = comm_system.service_discovery.get_discovery_status()
        print(f"Discovery Status: {discovery_status}")

        # Test load balancer
        print("\n=== Load Balancer Test ===")
        lb_stats = comm_system.load_balancer.get_load_balancer_stats()
        print(f"Load Balancer Stats: {lb_stats}")

        # Test system status
        print("\n=== System Status ===")
        system_status = comm_system.get_system_status()
        print(f"System Status: {system_status}")

        # Cleanup
        await comm_system.shutdown()
        print("\nCommunication System Test Complete")

    # Run the test
    asyncio.run(test_communication_system())
