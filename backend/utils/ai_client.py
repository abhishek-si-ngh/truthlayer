import os
import asyncio
from .ollama_client import ollama_client
from .gemini_client import gemini_rotator
from .groq_client import groq_client

class AIClient:
    async def generate_completion(self, prompt: str, temperature: float = 0.1, max_tokens: int = 4096) -> str:
        # Check for Demo/Mock mode
        if os.environ.get("DEMO_MODE", "").lower() == "true":
            if "extract" in prompt.lower():
                return '[{"id": 1, "claim": "Demo Claim: The AI is running in mock mode because no valid keys were found.", "context": "System", "category": "demo"}]'
            return '{"verdict": "Verified", "confidence": 1.0, "explanation": "Demo mode: This is a mock verification.", "correction": null, "sources": ["https://example.com"]}'

        # Prioritize Groq (fastest), then Gemini, then Ollama
        errors = []

        # 1. Try Groq
        if groq_client.api_key:
            try:
                return await groq_client.generate_completion(prompt, temperature=temperature, max_tokens=max_tokens)
            except Exception as e:
                err_msg = f"Groq error: {str(e)}"
                print(err_msg)
                errors.append(err_msg)

        # 2. Try Gemini
        if gemini_rotator.keys:
            try:
                model = gemini_rotator.get_model()
                response = await asyncio.to_thread(model.generate_content, prompt)
                return response.text
            except Exception as e:
                err_msg = f"Gemini error: {str(e)}"
                print(err_msg)
                errors.append(err_msg)
        
        # 3. Try Ollama
        if ollama_client.api_key or os.environ.get("OLLAMA_BASE_URL"):
            try:
                return await ollama_client.generate_completion(prompt, temperature=temperature, max_tokens=max_tokens)
            except Exception as e:
                err_msg = f"Ollama error: {str(e)}"
                print(err_msg)
                errors.append(err_msg)

        # If we get here, everything failed or no keys provided
        error_details = "\n".join(errors)
        raise Exception(
            f"AI completion failed. Please check your API keys in backend/.env.\n"
            f"Details:\n{error_details if errors else 'No Gemini or Ollama keys found.'}\n\n"
            f"TIP: You can set DEMO_MODE=true in .env to test the UI with mock data."
        )

ai_client = AIClient()
