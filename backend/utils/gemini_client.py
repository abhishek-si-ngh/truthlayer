"""
Gemini Client Utility — implements API key rotation to bypass free-tier quota limits.
"""

import os
import random
import google.generativeai as genai
from typing import Optional

class GeminiRotator:
    def __init__(self):
        # Load keys from environment
        keys_str = os.environ.get("GEMINI_API_KEYS", "")
        if not keys_str:
            # Fallback to single key variants
            keys_str = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY", "")
        
        self.keys = [k.strip() for k in keys_str.split(",") if k.strip()]
        self.current_index = 0
        
        if not self.keys:
            print("WARNING: No Gemini API keys found in environment!")
        else:
            print(f"Initialized GeminiRotator with {len(self.keys)} keys.")

    def get_model(self, model_name: str = "gemini-flash-latest", generation_config: Optional[dict] = None):
        """
        Configure genai with a key and return a model instance.
        """
        if not self.keys:
            raise ValueError("No API keys available.")
            
        key = self.keys[self.current_index]
        genai.configure(api_key=key)
        
        return genai.GenerativeModel(
            model_name=model_name,
            generation_config=generation_config
        )

    def rotate(self):
        """
        Move to the next available API key.
        """
        if len(self.keys) > 1:
            self.current_index = (self.current_index + 1) % len(self.keys)
            print(f"Rotated to Gemini API key index {self.current_index}")
        return self.keys[self.current_index]

# Global instance
gemini_rotator = GeminiRotator()
