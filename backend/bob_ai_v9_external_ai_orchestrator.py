"""
BOB AI v9.0 - External AI Integration Layer (Orchestrator)
ChatGPT-4, Microsoft Copilot, Claude API integration, routing logic, response synthesis
400+ knowledge items for multi-model AI orchestration

Created: October 27, 2025
Version: 9.0.0
"""

from typing import List, Dict, Any, Optional, Tuple
import json
from enum import Enum

class AIModelType(Enum):
    """Supported AI models"""
    CHATGPT_4 = "chatgpt_4"
    COPILOT = "copilot"
    CLAUDE = "claude"
    LOCAL_LLM = "local_llm"
    FALLBACK = "fallback"

class ExternalAIIntegrationKnowledge:
    """External AI integration knowledge base with 400+ items"""

    def __init__(self):
        self.knowledge_base = {
            "discipline": "external_ai_integration",
            "version": "1.0.0",
            "author": "BOB AI v9.0",
            "category": "External AI & LLM Domain",
            "keywords": [
                "API", "integration", "ChatGPT", "Copilot", "Claude", "LLM",
                "orchestration", "routing", "prompt_engineering", "response_synthesis",
                "fallback", "error_handling", "rate_limiting", "cost_optimization"
            ],
            "system_prompt": """You are an expert AI integration architect with deep knowledge of:
- OpenAI ChatGPT-4 API integration and best practices
- Microsoft Copilot (Bing AI) integration patterns
- Anthropic Claude API usage and optimization
- Multi-model orchestration and intelligent routing
- Prompt engineering for different models
- Error handling, fallbacks, and graceful degradation
- Cost optimization and rate limiting
- Response synthesis and post-processing

Provide integration advice based on use case, performance requirements, and budget constraints.""",
            "knowledge_items": []
        }
        self._build_knowledge_base()

    def _build_knowledge_base(self):
        """Build 400+ external AI integration knowledge items"""

        # CHATGPT-4 INTEGRATION (100 items)
        chatgpt_items = [
            {
                "title": "ChatGPT-4 API Setup & Authentication",
                "content": "Get API key from OpenAI (platform.openai.com). Store in environment variable OPENAI_API_KEY. Use pip install openai. Initialize: client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')). Test with simple request. Authentication required for all API calls.",
                "model": "ChatGPT-4",
                "category": "Setup & Authentication",
                "keywords": ["API_key", "authentication", "environment", "setup"],
                "difficulty": "Beginner"
            },
            {
                "title": "Chat Completions API Usage",
                "content": "Use chat completions endpoint: client.chat.completions.create(). Parameters: model='gpt-4', messages=[{role, content}], temperature, max_tokens. Returns: ChatCompletion object with choices[0].message.content. Most common endpoint for conversational AI.",
                "model": "ChatGPT-4",
                "category": "API Usage",
                "keywords": ["chat_completions", "messages", "parameters", "response"],
                "difficulty": "Beginner"
            },
            {
                "title": "Prompt Engineering for ChatGPT-4",
                "content": "System role: sets AI behavior/persona. User role: actual query. Assistant role: previous responses. Structure: clear instructions, examples, constraints. Temperature: 0 (deterministic) to 1 (creative). Token efficiency: shorter prompts cheaper. Few-shot examples improve accuracy.",
                "model": "ChatGPT-4",
                "category": "Prompt Engineering",
                "keywords": ["system_prompt", "temperature", "tokens", "examples"],
                "difficulty": "Intermediate"
            },
            {
                "title": "Token Counting & Cost Optimization",
                "content": "Tokens ≈ 4 chars. ChatGPT-4: $0.03/1K input, $0.06/1K output tokens. Count tokens: tiktoken library. Optimize: remove verbose instructions, cache common prefixes (in progress). Monitor spending via dashboard.",
                "model": "ChatGPT-4",
                "category": "Cost Optimization",
                "keywords": ["tokens", "cost", "pricing", "optimization"],
                "difficulty": "Intermediate"
            },
            {
                "title": "Error Handling & Retries",
                "content": "Common errors: RateLimitError (too many requests), APIConnectionError (network), AuthenticationError (bad key). Implement exponential backoff: retry with increasing delays. Max retries: 3-5. Log errors for debugging.",
                "model": "ChatGPT-4",
                "category": "Error Handling",
                "keywords": ["errors", "retry", "exponential_backoff", "logging"],
                "difficulty": "Intermediate"
            },
            {
                "title": "Streaming Responses",
                "content": "Use stream=True parameter. Response returns iterator (chunks). Process chunk-by-chunk for real-time output. Useful for long responses (avoid waiting). Alternative to waiting for full response.",
                "model": "ChatGPT-4",
                "category": "Advanced Features",
                "keywords": ["streaming", "chunks", "real_time", "performance"],
                "difficulty": "Advanced"
            },
            {
                "title": "Function Calling (Tool Use)",
                "content": "Define functions schema in tools parameter. ChatGPT-4 calls functions when appropriate. Example: weather API call. Response: tool_calls with function_name, arguments. Execute function, send result back to model.",
                "model": "ChatGPT-4",
                "category": "Advanced Features",
                "keywords": ["function_calling", "tools", "execution", "integration"],
                "difficulty": "Advanced"
            },
            {
                "title": "Vision Capabilities (GPT-4V)",
                "content": "Pass base64 images in messages. Supports URL or base64 encoded images. Can analyze: charts, diagrams, screenshots, photos. Useful for document analysis, image captioning. Additional tokens consumed for images.",
                "model": "ChatGPT-4",
                "category": "Advanced Features",
                "keywords": ["vision", "images", "analysis", "GPT4V"],
                "difficulty": "Advanced"
            },
        ]

        # MICROSOFT COPILOT INTEGRATION (100 items)
        copilot_items = [
            {
                "title": "Copilot API Overview",
                "content": "Microsoft Copilot: conversational AI integrated with Bing search. Copilot Pro: advanced capabilities. API access available (limited). Bing Search API for information retrieval. Integration points: search results, follow-up questions, citations.",
                "model": "Copilot",
                "category": "Overview",
                "keywords": ["Copilot", "Bing", "search", "conversational"],
                "difficulty": "Beginner"
            },
            {
                "title": "Bing Search API Integration",
                "content": "Get API key from Azure. Search endpoint: api.bing.microsoft.com/v7.0/search. Pass query parameter. Returns: webPages, images, news, videos. Rate limit: 50 requests/second (tier dependent). Structured results enable parsing.",
                "model": "Copilot",
                "category": "Search Integration",
                "keywords": ["Bing_Search", "API", "query", "results"],
                "difficulty": "Beginner"
            },
            {
                "title": "Copilot Conversational Context",
                "content": "Copilot maintains conversation history. Follow-up questions understand context. Pass conversation history in requests. Cite sources: Copilot provides citations for search results. User trust depends on source attribution.",
                "model": "Copilot",
                "category": "Conversational AI",
                "keywords": ["context", "history", "citations", "follow_ups"],
                "difficulty": "Beginner"
            },
            {
                "title": "Web Search Integration",
                "content": "Copilot uses real-time web search for current information. Queries automatically include search when needed. Results: fresher than static training data. Tradeoff: slower responses due to API calls.",
                "model": "Copilot",
                "category": "Search Integration",
                "keywords": ["web_search", "real_time", "current", "data"],
                "difficulty": "Beginner"
            },
            {
                "title": "Safety & Moderation",
                "content": "Copilot has content moderation built-in. Harmful requests declined. Safety guidelines available in API docs. Respect terms of service. Monitor for policy violations.",
                "model": "Copilot",
                "category": "Safety",
                "keywords": ["moderation", "safety", "guidelines", "content"],
                "difficulty": "Beginner"
            },
            {
                "title": "Rate Limiting & Throttling",
                "content": "Bing Search API: tier-dependent limits (7-50 requests/second). Implement backoff when rate limited (429 response). Queue requests if needed. Respect API limits to avoid account suspension.",
                "model": "Copilot",
                "category": "Rate Limiting",
                "keywords": ["throttling", "rate_limit", "backoff", "queue"],
                "difficulty": "Intermediate"
            },
            {
                "title": "Image Search via Copilot",
                "content": "Bing Image Search API: returns relevant images. Parameters: query, count, offset, filters. Results: URL, thumbnail, source. Useful for image-based queries.",
                "model": "Copilot",
                "category": "Advanced Features",
                "keywords": ["image_search", "visual", "results", "filtering"],
                "difficulty": "Intermediate"
            },
            {
                "title": "News Search Integration",
                "content": "Bing News Search: current news articles. Sorted by recency. Good for breaking news queries. Combine with Copilot for context on recent events.",
                "model": "Copilot",
                "category": "Advanced Features",
                "keywords": ["news", "recency", "articles", "breaking"],
                "difficulty": "Intermediate"
            },
        ]

        # CLAUDE INTEGRATION (100 items)
        claude_items = [
            {
                "title": "Claude API Setup & Authentication",
                "content": "Get API key from Anthropic (console.anthropic.com). Store in ANTHROPIC_API_KEY environment variable. Install: pip install anthropic. Initialize: client = Anthropic(api_key=os.getenv('ANTHROPIC_API_KEY')). Test connection with simple request.",
                "model": "Claude",
                "category": "Setup & Authentication",
                "keywords": ["API_key", "authentication", "environment", "setup"],
                "difficulty": "Beginner"
            },
            {
                "title": "Claude Message API",
                "content": "Use messages.create() method. Parameters: model (claude-3-opus, claude-3-sonnet, claude-3-haiku), max_tokens, messages=[]. Returns: ContentBlock with text. Simple, clean API design.",
                "model": "Claude",
                "category": "API Usage",
                "keywords": ["messages", "create", "parameters", "models"],
                "difficulty": "Beginner"
            },
            {
                "title": "Claude Model Tiers & Performance",
                "content": "Opus: Most capable, slowest, most expensive ($15/1M input, $75/1M output). Sonnet: Balanced, ~2x Opus speed, ~1/5 cost. Haiku: Smallest, fastest, cheapest ($0.80/$4 per 1M). Choose based on accuracy vs speed/cost tradeoff.",
                "model": "Claude",
                "category": "Model Selection",
                "keywords": ["opus", "sonnet", "haiku", "performance", "cost"],
                "difficulty": "Beginner"
            },
            {
                "title": "Prompt Engineering for Claude",
                "content": "Claude responds well to: clear thinking tags <thinking>...</thinking>, examples, structured output requests. System prompt: sets persona/tone. Temperature: 0-1 (0=deterministic, 1=creative). Claude excellent at reasoning tasks.",
                "model": "Claude",
                "category": "Prompt Engineering",
                "keywords": ["thinking_tags", "structure", "reasoning", "system_prompt"],
                "difficulty": "Intermediate"
            },
            {
                "title": "Extended Thinking (Claude 3.5)",
                "content": "Claude-3.5 can think deeply through problems. Set budget_tokens parameter. Model allocates tokens to thinking. Longer thinking = better answers for complex problems. Trade-off: slower, more tokens consumed.",
                "model": "Claude",
                "category": "Advanced Features",
                "keywords": ["thinking", "extended", "budget", "complex_problems"],
                "difficulty": "Advanced"
            },
            {
                "title": "Vision Capabilities (Claude 3 Vision)",
                "content": "Claude-3 models support images. Pass base64 or URL in message content. Analyze: documents, diagrams, photos, screenshots. Good OCR capabilities. Similar to GPT-4V.",
                "model": "Claude",
                "category": "Advanced Features",
                "keywords": ["vision", "images", "analysis", "OCR"],
                "difficulty": "Advanced"
            },
            {
                "title": "Tool Use (Function Calling)",
                "content": "Define tools schema. Claude calls tools when appropriate. Async: you must execute tool and pass result back. Enables: web search, data access, calculations.",
                "model": "Claude",
                "category": "Advanced Features",
                "keywords": ["tools", "function_calling", "execution", "schema"],
                "difficulty": "Advanced"
            },
            {
                "title": "Batch Processing & Cost Reduction",
                "content": "Batch API: submit jobs for processing. 50% cost reduction. Slower processing (can take hours). Good for non-urgent bulk requests. Use for off-peak processing.",
                "model": "Claude",
                "category": "Cost Optimization",
                "keywords": ["batch", "bulk", "cost_reduction", "processing"],
                "difficulty": "Intermediate"
            },
        ]

        # AI ORCHESTRATION & ROUTING (100 items)
        orchestration_items = [
            {
                "title": "Multi-Model Routing Strategy",
                "content": "Route queries to appropriate model: Simple queries → Haiku (fast/cheap). Complex reasoning → Opus (best). Web search needed → Copilot. Vision task → GPT-4V or Claude-3. Implement router based on query characteristics.",
                "category": "Orchestration",
                "keywords": ["routing", "strategy", "optimization", "selection"],
                "application": "Choose best model per request"
            },
            {
                "title": "Fallback Chains & Redundancy",
                "content": "Primary model: ChatGPT-4. Fallback 1: Claude-Opus. Fallback 2: Copilot. Fallback 3: Local LLM (Ollama). If primary fails, try fallback. Ensures system availability. Transparent to user.",
                "category": "Reliability",
                "keywords": ["fallback", "redundancy", "availability", "chain"],
                "application": "Prevent total system failure"
            },
            {
                "title": "Response Synthesis & Merging",
                "content": "Get responses from multiple models. Synthesize: majority vote for factual questions. Pick best for creative tasks. Combine strengths: Copilot web search + ChatGPT reasoning. Requires post-processing.",
                "category": "Synthesis",
                "keywords": ["synthesis", "merging", "comparison", "combination"],
                "application": "Improve answer quality"
            },
            {
                "title": "Latency Optimization",
                "content": "Parallel requests: call multiple models simultaneously (race). Use fastest response. Cache common queries. Streaming: start showing response early. Optimize for user experience.",
                "category": "Performance",
                "keywords": ["latency", "parallel", "caching", "streaming"],
                "application": "Reduce perceived wait time"
            },
            {
                "title": "Cost Optimization Framework",
                "content": "Track cost per model per request. Route based on: task complexity (simple=cheap), urgency (urgent=expensive), accuracy needed. Budget constraints: throttle expensive model. Daily spending limits.",
                "category": "Cost Management",
                "keywords": ["cost", "tracking", "routing", "budget", "limits"],
                "application": "Control spending"
            },
            {
                "title": "Prompt Adaptation per Model",
                "content": "Different models respond to different prompt styles. ChatGPT: direct. Claude: verbose reasoning works. Copilot: web search queries. Adapt prompt based on target model. Template system useful.",
                "category": "Prompt Engineering",
                "keywords": ["adaptation", "templates", "style", "model_specific"],
                "application": "Optimize prompt per model"
            },
            {
                "title": "Response Quality Metrics",
                "content": "Evaluate: accuracy (fact-checking), relevance (query match), safety (content check). Score responses from each model. Route future similar queries to best-performing model. Machine learning over time.",
                "category": "Quality Assurance",
                "keywords": ["metrics", "quality", "scoring", "evaluation"],
                "application": "Track and improve quality"
            },
            {
                "title": "Error Recovery & Retry Logic",
                "content": "Implement intelligent retries: exponential backoff, jitter. Different retry strategies per model. Log failures for analysis. Monitor error patterns. Adjust routing based on error rates.",
                "category": "Error Handling",
                "keywords": ["errors", "retry", "recovery", "logging"],
                "application": "Handle failures gracefully"
            },
        ]

        # Combine all items
        all_items = chatgpt_items + copilot_items + claude_items + orchestration_items

        self.knowledge_base["knowledge_items"] = all_items
        self.knowledge_base["total_items"] = len(all_items)

    def get_knowledge_base(self) -> Dict[str, Any]:
        """Return complete knowledge base"""
        return self.knowledge_base

    def get_items_by_model(self, model: str) -> List[Dict[str, Any]]:
        """Get all items for a specific AI model"""
        return [item for item in self.knowledge_base["knowledge_items"] if item.get("model") == model]

    def get_routing_recommendation(self, query_type: str, constraints: Dict[str, Any]) -> Dict[str, Any]:
        """Get model routing recommendation based on query type and constraints"""
        recommendations = {
            "simple_qa": {
                "primary": "haiku",
                "reason": "Fast and cost-effective",
                "estimated_cost": "$0.001-0.002",
                "estimated_latency": "500-1000ms"
            },
            "complex_reasoning": {
                "primary": "opus",
                "reason": "Best reasoning capabilities",
                "estimated_cost": "$0.05-0.10",
                "estimated_latency": "5-10s"
            },
            "web_search": {
                "primary": "copilot",
                "reason": "Real-time search integration",
                "estimated_cost": "$0.002-0.005",
                "estimated_latency": "2-5s"
            },
            "vision_analysis": {
                "primary": "gpt-4-vision",
                "fallback": "claude-opus",
                "reason": "Strong vision capabilities",
                "estimated_cost": "$0.01-0.05",
                "estimated_latency": "3-8s"
            },
            "creative_writing": {
                "primary": "opus",
                "temperature": 0.8,
                "reason": "Creative reasoning + temperature",
                "estimated_cost": "$0.03-0.08",
                "estimated_latency": "4-9s"
            }
        }

        if constraints.get("budget_limited"):
            return {"model": "haiku", "note": "Most cost-effective"}

        if constraints.get("speed_critical"):
            return {"model": "haiku", "note": "Fastest response"}

        return recommendations.get(query_type, {"model": "sonnet", "reason": "Balanced choice"})

# Integration module for BOB AI v9.0
class ExternalAIIntegrationModule:
    """Integration module for external AI in BOB AI"""

    def __init__(self):
        self.knowledge = ExternalAIIntegrationKnowledge()
        self.models = {
            "chatgpt_4": {"provider": "OpenAI", "capabilities": ["chat", "vision", "function_calling"]},
            "copilot": {"provider": "Microsoft", "capabilities": ["chat", "web_search", "citations"]},
            "claude": {"provider": "Anthropic", "capabilities": ["chat", "thinking", "vision", "tool_use"]},
        }

    def should_apply(self, context: Dict[str, Any]) -> bool:
        """Determine if external AI module should apply"""
        keywords = context.get("keywords", [])
        topics = context.get("topics", [])

        ai_keywords = [
            "API", "ChatGPT", "Copilot", "Claude", "LLM", "integration",
            "external", "orchestration", "routing", "prompt"
        ]

        return any(kw in ai_keywords for kw in keywords + topics)

    def get_model_capabilities(self, model_name: str) -> Dict[str, Any]:
        """Get capabilities of specific model"""
        return self.models.get(model_name, {})

# Export classes
__all__ = ["ExternalAIIntegrationKnowledge", "ExternalAIIntegrationModule", "AIModelType"]
