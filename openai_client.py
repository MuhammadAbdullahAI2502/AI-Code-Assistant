import openai
import asyncio
import time
from typing import List, Dict, Optional

class OpenAIClient:
    def __init__(self, api_key: str, max_retries: int = 3, retry_delay: float = 1.0):
        openai.api_key = api_key
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = False
    ) -> str:
        """Get completion from OpenAI with retry logic."""
        
        for attempt in range(self.max_retries):
            try:
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model=model,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature
                )
                return response.choices[0].message.content or ""
            
            except Exception as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    await asyncio.sleep(wait_time)
                    continue
                return f"Error: {str(e)}"
    
