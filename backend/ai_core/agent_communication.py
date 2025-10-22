"""
ORFEAS AI 2D→3D Studio - Agent Communication
============================================
Inter-agent messaging and event coordination system.

Features:
- Inter-agent message passing
- Event-driven coordination with pub/sub
- Message queue management
- Agent state synchronization
- Communication logging and debugging
"""

import os
import logging
import asyncio
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import uuid
import json

logger = logging.getLogger(__name__)


class MessageType(Enum):
    """Message type enumeration"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    BROADCAST = "broadcast"
    STATE_SYNC = "state_sync"


class MessagePriority(Enum):
    """Message priority levels"""
    LOW = 1
    NORMAL = 5
    HIGH = 8
    CRITICAL = 10


@dataclass
class Message:
    """Inter-agent message"""
    id: str
    type: MessageType
    sender_id: str
    recipient_id: Optional[str] = None  # None for broadcast
    topic: Optional[str] = None
    payload: Dict[str, Any] = field(default_factory=dict)
    priority: MessagePriority = MessagePriority.NORMAL
    correlation_id: Optional[str] = None  # For request-response
    timestamp: datetime = field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MessageRoute:
    """Message routing rule"""
    topic: str
    handler: Callable
    agent_id: str
    filter_func: Optional[Callable] = None


class AgentCommunication:
    """
    Inter-agent messaging and event coordination
    """

    def __init__(self):
        # Message queues per agent
        self.message_queues: Dict[str, asyncio.Queue] = {}

        # Topic subscriptions
        self.subscriptions: Dict[str, List[MessageRoute]] = {}

        # Message history for debugging
        self.message_history: List[Message] = []
        self.max_history_size = 1000

        # Request-response tracking
        self.pending_requests: Dict[str, asyncio.Future] = {}

        # Statistics
        self.total_messages_sent = 0
        self.total_messages_delivered = 0
        self.total_broadcasts = 0
        self.total_events = 0

        # Active connections
        self.active_agents: Set[str] = set()

        logger.info("[ORFEAS-COMM] AgentCommunication initialized")

    def register_agent(self, agent_id: str):
        """Register agent for communication"""
        if agent_id not in self.message_queues:
            self.message_queues[agent_id] = asyncio.Queue()
            self.active_agents.add(agent_id)

            logger.info(f"[ORFEAS-COMM] Registered agent: {agent_id}")

    def unregister_agent(self, agent_id: str):
        """Unregister agent"""
        if agent_id in self.message_queues:
            del self.message_queues[agent_id]
            self.active_agents.discard(agent_id)

            # Remove subscriptions
            for topic in list(self.subscriptions.keys()):
                self.subscriptions[topic] = [
                    route for route in self.subscriptions[topic]
                    if route.agent_id != agent_id
                ]
                if not self.subscriptions[topic]:
                    del self.subscriptions[topic]

            logger.info(f"[ORFEAS-COMM] Unregistered agent: {agent_id}")

    async def send_message(
        self,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        message_type: MessageType = MessageType.REQUEST,
        priority: MessagePriority = MessagePriority.NORMAL,
        correlation_id: Optional[str] = None
    ) -> Message:
        """
        Send message to specific agent

        Args:
            sender_id: Sender agent ID
            recipient_id: Recipient agent ID
            payload: Message payload
            message_type: Type of message
            priority: Message priority
            correlation_id: For request-response tracking

        Returns:
            Sent Message object
        """
        message = Message(
            id=str(uuid.uuid4()),
            type=message_type,
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            priority=priority,
            correlation_id=correlation_id
        )

        await self._deliver_message(message)

        self.total_messages_sent += 1

        logger.debug(
            f"[ORFEAS-COMM] Message sent: {sender_id} -> {recipient_id} "
            f"(type={message_type.value}, priority={priority.value})"
        )

        return message

    async def _deliver_message(self, message: Message):
        """Deliver message to recipient"""

        recipient_id = message.recipient_id

        if recipient_id is None:
            logger.warning("[ORFEAS-COMM] Cannot deliver message without recipient")
            return

        if recipient_id not in self.message_queues:
            logger.warning(f"[ORFEAS-COMM] Recipient not registered: {recipient_id}")
            return

        # Add to queue
        await self.message_queues[recipient_id].put(message)

        # Track delivery
        self.total_messages_delivered += 1

        # Add to history
        self._add_to_history(message)

    async def broadcast_message(
        self,
        sender_id: str,
        payload: Dict[str, Any],
        exclude_agents: Optional[List[str]] = None
    ) -> List[Message]:
        """
        Broadcast message to all agents

        Args:
            sender_id: Sender agent ID
            payload: Message payload
            exclude_agents: Agents to exclude from broadcast

        Returns:
            List of sent messages
        """
        exclude_agents = exclude_agents or []
        messages = []

        for agent_id in self.active_agents:
            if agent_id == sender_id or agent_id in exclude_agents:
                continue

            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.BROADCAST,
                sender_id=sender_id,
                recipient_id=agent_id,
                payload=payload,
                priority=MessagePriority.NORMAL
            )

            await self._deliver_message(message)
            messages.append(message)

        self.total_broadcasts += 1

        logger.info(
            f"[ORFEAS-COMM] Broadcast from {sender_id} "
            f"to {len(messages)} agents"
        )

        return messages

    async def publish_event(
        self,
        sender_id: str,
        topic: str,
        payload: Dict[str, Any],
        priority: MessagePriority = MessagePriority.NORMAL
    ) -> int:
        """
        Publish event to topic subscribers

        Args:
            sender_id: Event publisher
            topic: Event topic
            payload: Event data
            priority: Event priority

        Returns:
            Number of subscribers notified
        """
        if topic not in self.subscriptions:
            logger.debug(f"[ORFEAS-COMM] No subscribers for topic: {topic}")
            return 0

        routes = self.subscriptions[topic]
        delivered = 0

        for route in routes:
            # Apply filter if present
            if route.filter_func and not route.filter_func(payload):
                continue

            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.EVENT,
                sender_id=sender_id,
                recipient_id=route.agent_id,
                topic=topic,
                payload=payload,
                priority=priority
            )

            await self._deliver_message(message)
            delivered += 1

        self.total_events += 1

        logger.debug(
            f"[ORFEAS-COMM] Published event to topic '{topic}': "
            f"{delivered} subscribers notified"
        )

        return delivered

    def subscribe(
        self,
        agent_id: str,
        topic: str,
        handler: Callable,
        filter_func: Optional[Callable] = None
    ):
        """
        Subscribe agent to topic

        Args:
            agent_id: Subscribing agent ID
            topic: Topic to subscribe to
            handler: Message handler function
            filter_func: Optional filter function
        """
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []

        route = MessageRoute(
            topic=topic,
            handler=handler,
            agent_id=agent_id,
            filter_func=filter_func
        )

        self.subscriptions[topic].append(route)

        logger.info(f"[ORFEAS-COMM] Agent {agent_id} subscribed to topic: {topic}")

    def unsubscribe(self, agent_id: str, topic: str):
        """Unsubscribe agent from topic"""
        if topic not in self.subscriptions:
            return

        self.subscriptions[topic] = [
            route for route in self.subscriptions[topic]
            if route.agent_id != agent_id
        ]

        if not self.subscriptions[topic]:
            del self.subscriptions[topic]

        logger.info(f"[ORFEAS-COMM] Agent {agent_id} unsubscribed from topic: {topic}")

    async def request_response(
        self,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        timeout_seconds: float = 30.0
    ) -> Optional[Dict[str, Any]]:
        """
        Send request and wait for response

        Args:
            sender_id: Requester agent ID
            recipient_id: Responder agent ID
            payload: Request payload
            timeout_seconds: Timeout for response

        Returns:
            Response payload or None on timeout
        """
        correlation_id = str(uuid.uuid4())

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[correlation_id] = future

        # Send request
        await self.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            message_type=MessageType.REQUEST,
            correlation_id=correlation_id
        )

        try:
            # Wait for response with timeout
            response = await asyncio.wait_for(future, timeout=timeout_seconds)
            return response

        except asyncio.TimeoutError:
            logger.warning(
                f"[ORFEAS-COMM] Request timeout: {sender_id} -> {recipient_id} "
                f"(correlation_id={correlation_id})"
            )
            return None

        finally:
            # Clean up
            if correlation_id in self.pending_requests:
                del self.pending_requests[correlation_id]

    async def send_response(
        self,
        sender_id: str,
        recipient_id: str,
        payload: Dict[str, Any],
        correlation_id: str
    ):
        """
        Send response to request

        Args:
            sender_id: Responder agent ID
            recipient_id: Original requester ID
            payload: Response payload
            correlation_id: Original request correlation ID
        """
        # Send response message
        await self.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            payload=payload,
            message_type=MessageType.RESPONSE,
            correlation_id=correlation_id
        )

        # Complete pending request if exists
        if correlation_id in self.pending_requests:
            future = self.pending_requests[correlation_id]
            if not future.done():
                future.set_result(payload)

    async def receive_message(
        self,
        agent_id: str,
        timeout_seconds: Optional[float] = None
    ) -> Optional[Message]:
        """
        Receive message from agent's queue

        Args:
            agent_id: Agent ID
            timeout_seconds: Optional timeout

        Returns:
            Message or None on timeout
        """
        if agent_id not in self.message_queues:
            logger.warning(f"[ORFEAS-COMM] Agent not registered: {agent_id}")
            return None

        queue = self.message_queues[agent_id]

        try:
            if timeout_seconds:
                message = await asyncio.wait_for(
                    queue.get(),
                    timeout=timeout_seconds
                )
            else:
                message = await queue.get()

            return message

        except asyncio.TimeoutError:
            return None

    async def sync_state(
        self,
        agent_id: str,
        state_data: Dict[str, Any],
        target_agents: Optional[List[str]] = None
    ):
        """
        Synchronize state with other agents

        Args:
            agent_id: Agent sharing state
            state_data: State to synchronize
            target_agents: Specific agents to sync with (None for all)
        """
        if target_agents is None:
            target_agents = list(self.active_agents)
            target_agents.remove(agent_id)

        for target_id in target_agents:
            if target_id == agent_id:
                continue

            message = Message(
                id=str(uuid.uuid4()),
                type=MessageType.STATE_SYNC,
                sender_id=agent_id,
                recipient_id=target_id,
                payload=state_data,
                priority=MessagePriority.HIGH
            )

            await self._deliver_message(message)

        logger.debug(
            f"[ORFEAS-COMM] State synced from {agent_id} "
            f"to {len(target_agents)} agents"
        )

    def _add_to_history(self, message: Message):
        """Add message to history with size limit"""
        self.message_history.append(message)

        # Limit history size
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]

    def get_message_history(
        self,
        agent_id: Optional[str] = None,
        topic: Optional[str] = None,
        limit: int = 100
    ) -> List[Message]:
        """Get message history with optional filters"""

        history = self.message_history[-limit:]

        if agent_id:
            history = [
                m for m in history
                if m.sender_id == agent_id or m.recipient_id == agent_id
            ]

        if topic:
            history = [m for m in history if m.topic == topic]

        return history

    def get_statistics(self) -> Dict[str, Any]:
        """Get communication statistics"""

        return {
            'total_messages_sent': self.total_messages_sent,
            'total_messages_delivered': self.total_messages_delivered,
            'total_broadcasts': self.total_broadcasts,
            'total_events': self.total_events,
            'active_agents': len(self.active_agents),
            'active_subscriptions': sum(len(routes) for routes in self.subscriptions.values()),
            'pending_requests': len(self.pending_requests),
            'message_history_size': len(self.message_history),
            'topics': list(self.subscriptions.keys())
        }

    def get_agent_connections(self) -> Dict[str, Any]:
        """Get agent connection information"""

        return {
            'active_agents': list(self.active_agents),
            'queue_sizes': {
                agent_id: queue.qsize()
                for agent_id, queue in self.message_queues.items()
            },
            'subscriptions_by_agent': {
                agent_id: [
                    route.topic
                    for routes in self.subscriptions.values()
                    for route in routes
                    if route.agent_id == agent_id
                ]
                for agent_id in self.active_agents
            }
        }


# Global agent communication instance
_agent_communication: Optional[AgentCommunication] = None


def get_agent_communication() -> AgentCommunication:
    """Get global agent communication instance"""
    global _agent_communication
    if _agent_communication is None:
        _agent_communication = AgentCommunication()
    return _agent_communication
