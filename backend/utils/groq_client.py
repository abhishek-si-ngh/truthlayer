"""
Groq Client Utility — handles communication with Groq Cloud API.
"""

import os
import httpx
from typing import Optional

class GroqClient:
    def __init__(self):
        self.api_key = os.environ.get("GROQ_API_KEY")
        self.base_url = "https://api.groq.com/openai/v1"
        self.default_model = "llama-3.3-70b-versatile"

    async def generate_completion(
        self, 
        prompt: str, 
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> str:
        """
        Send a completion request to Groq Cloud.
        """
        if not self.api_key:
            raise ValueError("GROQ_API_KEY not found in environment.")

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
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await client.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Groq API Error ({response.status_code}): {response.text}")
            
            data = response.json()
            return data["choices"][0]["message"]["content"]

# Global instance
groq_client = GroqClient()
