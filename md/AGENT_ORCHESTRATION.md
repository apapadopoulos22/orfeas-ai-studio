# ORFEAS AI Agent Orchestration Patterns

This document describes the core patterns for multi-agent coordination, agent registry, and agent communication protocols in the ORFEAS platform.

## Agent Registry

The `AgentRegistry` class manages all available agents and their capabilities.

```python
from backend.agent_orchestration import AgentRegistry

registry = AgentRegistry()
registry.register_agent('agent1', 'quality_agent', ['quality_assessment', 'image_analysis'])
registry.register_agent('agent2', 'workflow_agent', ['pipeline_selection', 'resource_optimization'])

```text

## Agent Coordinator

The `AgentCoordinator` assigns tasks to agents based on required capabilities and tracks task status.

```python
from backend.agent_orchestration import AgentCoordinator

coordinator = AgentCoordinator(registry)
task_id = coordinator.assign_task('quality_check', {'image': 'img.png'}, 'quality_assessment')
status = coordinator.get_task_status(task_id)

```text

## Agent Message Structure

The `AgentMessage` class defines the message format for agent-to-agent or system-to-agent communication.

```python
from backend.agent_orchestration import AgentMessage

msg = AgentMessage(
    sender_id='system',
    recipient_id='agent1',
    task_type='quality_check',
    payload={'image': 'img.png'}
)

```text

## Integration Points

- Register agents at startup or dynamically as they become available.
- Use `AgentCoordinator` to assign tasks and monitor progress.
- Extend with message passing or distributed coordination as needed.

## Example Workflow

```python

## Register agents

registry = AgentRegistry()
registry.register_agent('agent1', 'quality_agent', ['quality_assessment'])
registry.register_agent('agent2', 'workflow_agent', ['pipeline_selection'])

## Assign a task

coordinator = AgentCoordinator(registry)
task_id = coordinator.assign_task('quality_check', {'image': 'img.png'}, 'quality_assessment')

## Check status

status = coordinator.get_task_status(task_id)
print(f"Task {task_id} status: {status['status']}")

```text

---

For advanced orchestration, see the full reference in `.github/copilot-instructions.md` and extend with distributed agent communication as needed.
