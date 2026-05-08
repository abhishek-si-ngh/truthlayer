"""
Ollama Client Utility — handles communication with Ollama Cloud API.
"""

import os
import json
import httpx
from typing import List, Dict, Any, Optional

class OllamaClient:
    def __init__(self):
        self.api_key = os.environ.get("OLLAMA_API_KEY")
        # Default to Ollama Cloud if key starts with specific prefix, otherwise local
        self.base_url = os.environ.get("OLLAMA_BASE_URL", "https://ollama.com/v1")
        # Support multiple model names to increase chances of success
        self.default_model = os.environ.get("OLLAMA_MODEL", "llama-3.1-8b")

    async def generate_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        Send a completion request to Ollama Cloud.
        """
        if not self.api_key:
            raise ValueError("OLLAMA_API_KEY not found in environment.")

        target_model = model or self.default_model
        
        async with httpx.AsyncClient(timeout=60.0) as client:
            payload = {
                "model": target_model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max_tokens
            }
            
            # headers = {
            #     "Authorization": f"Bearer {self.api_key}",
            #     "Content-Type": "application/json"
            # }
            
            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                error_msg = response.text
                if response.status_code == 401:
                    error_msg = "Unauthorized: Your OLLAMA_API_KEY is invalid or expired."
                else:
                    try:
                        error_json = response.json()
                        error_msg = error_json.get("error", {}).get("message", error_msg)
                    except:
                        pass
                raise Exception(f"Ollama API Error ({response.status_code}): {error_msg}")
            
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"Ollama JSON Decode Error: {e}")
                print(f"Raw Response: {response.text}")
                raise Exception(f"Failed to parse Ollama response as JSON: {str(e)}")

            return data["choices"][0]["message"]["content"]

# Global instance
ollama_client = OllamaClient()
