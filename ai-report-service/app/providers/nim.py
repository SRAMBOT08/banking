from __future__ import annotations
import httpx
from pydantic import SecretStr
from .base import ModelProvider, ProviderResponse


class NIMProvider(ModelProvider):
    def __init__(self, endpoint: str, model: str = 'meta/llama-3.1-70b-instruct', api_key: SecretStr | None = None, timeout: float = 30):
        self.endpoint, self.model, self.api_key, self.timeout = endpoint, model, api_key, timeout
    @property
    def model_name(self) -> str: return self.model
    async def generate(self, prompt: str) -> ProviderResponse:
        headers = {'Authorization': f'Bearer {self.api_key.get_secret_value()}'} if self.api_key else {}
        payload = {'model': self.model, 'messages': [{'role': 'user', 'content': prompt}], 'temperature': 0, 'stream': False}
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
        data = response.json()
        text = data['choices'][0]['message']['content']
        return ProviderResponse(text=text, model=self.model)
