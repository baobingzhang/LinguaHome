"""
LinguaHome LLM Provider

Simplified LLM provider supporting only OpenAI, Anthropic, and Gemini.
"""

import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class LLMModel(Enum):
    """Supported LLM models."""
    # OpenAI
    GPT_4O = "gpt-4o"
    GPT_4O_MINI = "gpt-4o-mini"
    GPT_4_TURBO = "gpt-4-turbo"
    
    # Anthropic
    CLAUDE_35_SONNET = "claude-3-5-sonnet-20241022"
    CLAUDE_35_HAIKU = "claude-3-5-haiku-20241022"
    CLAUDE_3_OPUS = "claude-3-opus-20240229"
    
    # Google Gemini
    GEMINI_2_FLASH = "gemini/gemini-2.0-flash"
    GEMINI_15_PRO = "gemini/gemini-1.5-pro"
    GEMINI_15_FLASH = "gemini/gemini-1.5-flash"


# Model aliases for convenience
MODEL_ALIASES = {
    # OpenAI
    "gpt-4o": "gpt-4o",
    "gpt4o": "gpt-4o",
    "gpt-4o-mini": "gpt-4o-mini",
    "gpt4": "gpt-4-turbo",
    
    # Anthropic
    "claude": "claude-3-5-sonnet-20241022",
    "claude-sonnet": "claude-3-5-sonnet-20241022",
    "claude-haiku": "claude-3-5-haiku-20241022",
    "claude-opus": "claude-3-opus-20240229",
    
    # Gemini
    "gemini": "gemini/gemini-2.0-flash",
    "gemini-flash": "gemini/gemini-2.0-flash",
    "gemini-pro": "gemini/gemini-1.5-pro",
    "gemini-2": "gemini/gemini-2.0-flash",
    "gemini-1.5": "gemini/gemini-1.5-pro",
}


@dataclass
class Message:
    """Chat message."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass
class LLMResponse:
    """LLM response."""
    content: str
    model: str
    usage: Dict[str, int]


def resolve_model(model: str) -> str:
    """Resolve model alias to full model name."""
    return MODEL_ALIASES.get(model.lower(), model)


def get_provider_from_model(model: str) -> str:
    """Determine provider from model name."""
    model_lower = model.lower()
    if model_lower.startswith("gpt") or model_lower.startswith("o1"):
        return "openai"
    elif model_lower.startswith("claude"):
        return "anthropic"
    elif model_lower.startswith("gemini"):
        return "google"
    else:
        return "unknown"


class LLMProvider:
    """
    LLM provider using litellm for OpenAI, Anthropic, and Gemini.
    """
    
    def __init__(
        self,
        model: str = "gpt-4o",
        temperature: float = 0.1,
        max_tokens: int = 4096,
    ):
        self.model = resolve_model(model)
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.provider = get_provider_from_model(self.model)
        
        # Check for litellm
        try:
            import litellm
            self._litellm = litellm
            litellm.set_verbose = False
        except ImportError:
            raise ImportError("litellm is required. Install with: pip install litellm")
        
        # Verify API key is set
        self._verify_api_key()
    
    def _verify_api_key(self) -> None:
        """Verify that the required API key is set."""
        if self.provider == "openai":
            if not os.environ.get("OPENAI_API_KEY"):
                raise ValueError("OPENAI_API_KEY environment variable not set")
        elif self.provider == "anthropic":
            if not os.environ.get("ANTHROPIC_API_KEY"):
                raise ValueError("ANTHROPIC_API_KEY environment variable not set")
        elif self.provider == "google":
            if not os.environ.get("GEMINI_API_KEY") and not os.environ.get("GOOGLE_API_KEY"):
                raise ValueError("GEMINI_API_KEY or GOOGLE_API_KEY environment variable not set")
    
    async def chat_async(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Async chat completion."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = await self._litellm.acompletion(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    def chat(
        self,
        messages: List[Message],
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
    ) -> LLMResponse:
        """Synchronous chat completion."""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        response = self._litellm.completion(
            model=self.model,
            messages=formatted_messages,
            temperature=temperature or self.temperature,
            max_tokens=max_tokens or self.max_tokens,
        )
        
        return LLMResponse(
            content=response.choices[0].message.content,
            model=response.model,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        )
    
    def get_info(self) -> Dict:
        """Get provider information."""
        return {
            "model": self.model,
            "provider": self.provider,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }


def list_supported_models() -> Dict[str, List[str]]:
    """List all supported models grouped by provider."""
    return {
        "OpenAI": [
            "gpt-4o (default)",
            "gpt-4o-mini",
            "gpt-4-turbo",
        ],
        "Anthropic": [
            "claude-3-5-sonnet-20241022 (alias: claude)",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
        ],
        "Google Gemini": [
            "gemini/gemini-2.0-flash (alias: gemini)",
            "gemini/gemini-1.5-pro",
            "gemini/gemini-1.5-flash",
        ],
    }


def create_provider(
    model: str = None,
    temperature: float = 0.1,
) -> LLMProvider:
    """Create an LLM provider with default settings."""
    model = model or os.environ.get("LINGUAHOME_MODEL", "gpt-4o")
    return LLMProvider(model=model, temperature=temperature)


if __name__ == "__main__":
    print("LinguaHome LLM Provider")
    print("=" * 50)
    print("\nSupported Models:")
    
    for provider, models in list_supported_models().items():
        print(f"\n{provider}:")
        for m in models:
            print(f"  - {m}")
    
    print("\n" + "=" * 50)
    print("Environment Variables:")
    print("  OPENAI_API_KEY     - For GPT models")
    print("  ANTHROPIC_API_KEY  - For Claude models")
    print("  GEMINI_API_KEY     - For Gemini models")
    print("  LINGUAHOME_MODEL   - Default model (gpt-4o)")
