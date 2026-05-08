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

        async def attempt_with_retry(func, name, retries=2):
            for i in range(retries + 1):
                try:
                    return await func()
                except Exception as e:
                    err_str = str(e)
                    # If it's a rate limit error (429), wait a bit and retry
                    if "429" in err_str and i < retries:
                        wait_time = (i + 1) * 2 # 2s, 4s
                        print(f"--- {name} rate limited. Retrying in {wait_time}s... ---")
                        await asyncio.sleep(wait_time)
                        continue
                    return e # Return the exception to be handled
            return Exception(f"{name} failed after {retries} retries")

        # 1. Try Groq
        if groq_client.api_key:
            res = await attempt_with_retry(
                lambda: groq_client.generate_completion(prompt, temperature=temperature, max_tokens=max_tokens),
                "Groq"
            )
            if isinstance(res, str): return res
            errors.append(f"Groq error: {str(res)}")

        # 2. Try Gemini
        if gemini_rotator.keys:
            async def gemini_call():
                model = gemini_rotator.get_model()
                response = await asyncio.to_thread(model.generate_content, prompt)
                return response.text

            res = await attempt_with_retry(gemini_call, "Gemini")
            if isinstance(res, str): return res
            errors.append(f"Gemini error: {str(res)}")
        
        # 3. Try Ollama
        if ollama_client.api_key or os.environ.get("OLLAMA_BASE_URL"):
            res = await attempt_with_retry(
                lambda: ollama_client.generate_completion(prompt, temperature=temperature, max_tokens=max_tokens),
                "Ollama"
            )
            if isinstance(res, str): return res
            errors.append(f"Ollama error: {str(res)}")

        # If we get here, everything failed or no keys provided
        error_details = "\n".join(errors)
        raise Exception(
            f"AI completion failed. Please check your API keys in backend/.env.\n"
            f"Details:\n{error_details if errors else 'No Gemini or Ollama keys found.'}\n\n"
            f"TIP: You can set DEMO_MODE=true in .env to test the UI with mock data."
        )

ai_client = AIClient()
