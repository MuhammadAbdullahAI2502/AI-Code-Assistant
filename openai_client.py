import openai
import asyncio
import time
from typing import List, Dict, Optional, AsyncGenerator
import logging

logger = logging.getLogger(__name__)

class OpenAIClient:
    def __init__(self, api_key: str, max_retries: int = 3, retry_delay: float = 1.0):
        self.client = openai.AsyncOpenAI(api_key=api_key)
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    async def get_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-4o-mini",
        max_tokens: int = 1000,
        temperature: float = 0.7,
        stream: bool = True
    ) -> str:
        """Get completion from OpenAI with retry logic and streaming support."""
        
        for attempt in range(self.max_retries):
            try:
                if stream:
                    return await self._stream_completion(
                        messages, model, max_tokens, temperature
                    )
                else:
                    return await self._single_completion(
                        messages, model, max_tokens, temperature
                    )
            
            except openai.RateLimitError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}")
                    await asyncio.sleep(wait_time)
                    continue
                raise e
            
            except openai.APIError as e:
                if attempt < self.max_retries - 1:
                    wait_time = self.retry_delay * (2 ** attempt)
                    logger.warning(f"API error: {e}, retrying in {wait_time}s")
                    await asyncio.sleep(wait_time)
                    continue
                raise e
            
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                raise e
    
    async def _single_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Get single completion response."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=False
        )
        
        return response.choices[0].message.content or ""
    
    async def _stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str,
        max_tokens: int,
        temperature: float
    ) -> str:
        """Get streaming completion response."""
        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=max_tokens,
            temperature=temperature,
            stream=True
        )
        
        content = ""
        async for chunk in response:
            if chunk.choices[0].delta.content:
                content += chunk.choices[0].delta.content
        
        return content