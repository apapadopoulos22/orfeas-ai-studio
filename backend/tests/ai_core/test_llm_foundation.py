"""
Unit tests for LLM integration foundation
"""

import pytest
import asyncio
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "llm_integration"))

from llm_foundation import (
    LLMProvider, LLMRequest, LLMResponse, 
    OpenAIGPT4Provider, AnthropicClaudeProvider, GoogleGeminiProvider,
    LLMManager, create_llm_manager
)

class TestLLMFoundation:
    """Test LLM foundation classes"""
    
    def test_llm_request_creation(self):
        """Test LLM request creation"""
        request = LLMRequest(
            prompt="Test prompt",
            temperature=0.5,
            max_tokens=1000
        )
        
        assert request.prompt == "Test prompt"
        assert request.temperature == 0.5
        assert request.max_tokens == 1000
        assert request.retry_attempts == 3
        
    def test_llm_response_creation(self):
        """Test LLM response creation"""
        response = LLMResponse(
            content="Test response",
            provider=LLMProvider.OPENAI_GPT4,
            model="gpt-4-turbo",
            success=True
        )
        
        assert response.content == "Test response"
        assert response.provider == LLMProvider.OPENAI_GPT4
        assert response.success is True
        
    @pytest.mark.asyncio
    async def test_openai_provider(self):
        """Test OpenAI provider"""
        provider = OpenAIGPT4Provider("mock_key")
        request = LLMRequest("Test prompt")
        
        response = await provider.generate_response(request)
        
        assert isinstance(response, LLMResponse)
        assert response.provider == LLMProvider.OPENAI_GPT4
        assert "GPT-4 Turbo response" in response.content
        
    @pytest.mark.asyncio 
    async def test_claude_provider(self):
        """Test Claude provider"""
        provider = AnthropicClaudeProvider("mock_key")
        request = LLMRequest("Test prompt")
        
        response = await provider.generate_response(request)
        
        assert isinstance(response, LLMResponse)
        assert response.provider == LLMProvider.ANTHROPIC_CLAUDE
        assert "Claude 3.5 Sonnet response" in response.content
        
    @pytest.mark.asyncio
    async def test_gemini_provider(self):
        """Test Gemini provider"""
        provider = GoogleGeminiProvider("mock_key")
        request = LLMRequest("Test prompt")
        
        response = await provider.generate_response(request)
        
        assert isinstance(response, LLMResponse)
        assert response.provider == LLMProvider.GOOGLE_GEMINI
        assert "Gemini Ultra response" in response.content
        
    def test_llm_manager_creation(self):
        """Test LLM manager creation"""
        manager = create_llm_manager()
        
        assert isinstance(manager, LLMManager)
        assert len(manager.providers) >= 3  # Mock providers
        
    @pytest.mark.asyncio
    async def test_llm_manager_generation(self):
        """Test LLM manager generation with retry"""
        manager = create_llm_manager()
        request = LLMRequest("Test prompt for manager")
        
        response = await manager.generate_with_retry(request)
        
        assert isinstance(response, LLMResponse)
        assert response.success is True
        assert len(response.content) > 0
        
    def test_provider_stats(self):
        """Test provider statistics"""
        provider = OpenAIGPT4Provider("mock_key")
        stats = provider.get_stats()
        
        assert "provider" in stats
        assert "model" in stats
        assert "requests_made" in stats
        assert stats["requests_made"] == 0
        
    def test_manager_stats(self):
        """Test manager statistics"""
        manager = create_llm_manager()
        stats = manager.get_all_stats()
        
        assert "total_providers" in stats
        assert "provider_stats" in stats
        assert stats["total_providers"] >= 3

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
