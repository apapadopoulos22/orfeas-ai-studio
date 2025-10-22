#!/usr/bin/env python3
"""
Local LLM Router - Routes requests to local Ollama server
"""

import os
import requests
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class LocalLLMRouter:
    """Routes LLM requests to local Ollama server"""

    def __init__(self):
        self.server_url = os.getenv("LOCAL_LLM_SERVER", "http://localhost:11434")
        self.model = os.getenv("LOCAL_LLM_MODEL", "mistral")  # Internal model name for Ollama
        self.display_name = "Bob AI"  # User-friendly display name
        self.enabled = os.getenv("ENABLE_LOCAL_LLMS", "false").lower() == "true"

        if self.enabled:
            logger.info(f"Local LLM router initialized")
            logger.info(f"  Server: {self.server_url}")
            logger.info(f"  Model: {self.model} (Display name: {self.display_name})")

    def is_available(self) -> bool:
        """Check if local LLM server is available"""
        if not self.enabled:
            return False

        try:
            response = requests.get(
                f"{self.server_url}/api/tags",
                timeout=2
            )
            return response.status_code == 200
        except:
            return False

    def generate(self, prompt: str, max_tokens: int = 2048) -> Dict:
        """Generate response from local Mistral"""

        if not self.is_available():
            return {"error": "Local LLM not available"}

        try:
            response = requests.post(
                f"{self.server_url}/api/generate",
                json={
                    "model": self.model,
                    "prompt": prompt,
                    "stream": False,
                    "num_predict": max_tokens,
                    "temperature": float(os.getenv("LOCAL_LLM_TEMPERATURE", "0.3"))
                },
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                return {
                    "response": data.get("response", ""),
                    "model": self.display_name,  # Return "Bob AI" to frontend
                    "source": "local",
                    "latency_ms": int(data.get("eval_duration", 0) / 1000000)
                }
            else:
                return {"error": f"Server error: {response.status_code}"}

        except Exception as e:
            logger.error(f"Local LLM generation failed: {e}")
            return {"error": str(e)}

# Initialize global router
local_llm = LocalLLMRouter()

def use_local_llm(prompt: str) -> Optional[Dict]:
    """Use local LLM if enabled and available"""
    if local_llm.is_available():
        return local_llm.generate(prompt)
    return None
