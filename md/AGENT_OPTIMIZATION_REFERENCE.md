# ORFEAS AI 2D→3D Studio - Agent Optimization Reference

This document summarizes the implementation and reference patterns for all major recommendations from the optimization audit and copilot-instructions. Use this as a guide for code, architecture, and documentation.

## 1. Batch Inference Implementation

- Implement true batch inference in `hunyuan_integration.py` and `batch_processor.py`.
- Use PyTorch tensor batching and mixed precision for GPU efficiency.
- Add batch size auto-tuning based on VRAM.
- Reference: See code pattern in audit section 2.1.

## 2. AI Agent API Endpoints

- Add `/api/agent/generate-3d` and `/api/agent/status/<job_id>` endpoints.
- Require API key authentication for agents.
- Support batch requests, priority queue, and structured JSON responses.
- Reference: See audit section 2.2 for endpoint and decorator patterns.

## 3. Dynamic GPU Resource Scaling

- Refactor `gpu_manager.py` to dynamically allocate jobs based on VRAM and job type.
- Implement `allocate_optimal_batch_size` and `can_allocate_job` methods.
- Reference: See audit section 2.3 for class and method patterns.

## 4. Asynchronous WebSocket Progress

- Implement a `ProgressTracker` class for automatic progress updates via WebSocket.
- Use context managers for stage tracking and ETA calculation.
- Reference: See audit section 2.4 for usage example.

## 5. Horizontal Scaling Preparation

- Implement a Redis-backed distributed job queue (`distributed_queue.py`).
- Update Docker Compose to support multiple backend workers and Redis.
- Reference: See audit section 2.5 for code and docker-compose patterns.

## 6. Security for AI Agents

- Add agent authentication in `agent_auth.py` using API keys and HMAC.
- Enforce per-agent rate limits and allowed operations.
- Reference: See audit section 3.2 for decorator and config patterns.

## 7. Documentation and Reference

- All new features and patterns must be documented in the `md/` directory.
- Use this file as a quick reference for implementation and onboarding.

---

For detailed code examples, see the full audit and copilot-instructions. For each new feature, update this document with implementation notes and usage patterns.
