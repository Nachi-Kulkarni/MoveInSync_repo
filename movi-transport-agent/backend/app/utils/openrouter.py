"""
OpenRouter API client for multimodal LLM requests.
Supports text, image, audio, and video inputs via the OpenRouter API.
"""
import httpx
from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class OpenRouterConfig(BaseModel):
    """Configuration for OpenRouter API client."""
    api_key: str
    base_url: str = "https://openrouter.ai/api/v1"
    default_model: str = "google/gemini-2.5-pro"
    timeout: int = 120


class OpenRouterClient:
    """
    OpenRouter API client for making multimodal requests.

    Supports:
    - Text messages
    - Image inputs (URL or base64)
    - Audio inputs (base64 only)
    - Video inputs (URL or base64)
    """

    def __init__(self, config: Optional[OpenRouterConfig] = None):
        """
        Initialize OpenRouter client.

        Args:
            config: Optional configuration. If not provided, uses settings from config.
        """
        if config is None:
            from app.core.config import settings
            if not settings.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY not configured in settings")
            config = OpenRouterConfig(api_key=settings.OPENROUTER_API_KEY)

        self.config = config
        self.client = httpx.AsyncClient(timeout=config.timeout)

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Make a chat completion request to OpenRouter.

        Args:
            messages: List of message dictionaries following OpenAI format
            model: Model to use (defaults to config.default_model)
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response

        Returns:
            Response dictionary from OpenRouter API

        Raises:
            httpx.HTTPError: If the request fails
        """
        url = f"{self.config.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://moveinsync.com",  # Optional, for rankings
            "X-Title": "Movi Transport Agent"  # Optional, shows in rankings
        }

        payload = {
            "model": model or self.config.default_model,
            "messages": messages,
            "temperature": temperature,
        }

        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        if stream:
            payload["stream"] = True

        response = await self.client.post(url, headers=headers, json=payload)
        response.raise_for_status()

        return response.json()

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()


def create_text_content(text: str) -> Dict[str, str]:
    """
    Create a text content object.

    Args:
        text: The text content

    Returns:
        Content dict with type "text"
    """
    return {
        "type": "text",
        "text": text
    }


def create_image_content(image_data: str, is_url: bool = True) -> Dict[str, Any]:
    """
    Create an image content object for OpenRouter.

    Args:
        image_data: Either a URL or base64-encoded image string
        is_url: True if image_data is a URL, False if it's base64

    Returns:
        Content dict with type "image_url"
    """
    if is_url:
        url = image_data
    else:
        # Assume it's already in data URL format: data:image/jpeg;base64,{base64_data}
        if not image_data.startswith("data:image/"):
            # Add data URL prefix if missing
            url = f"data:image/jpeg;base64,{image_data}"
        else:
            url = image_data

    return {
        "type": "image_url",
        "image_url": {
            "url": url
        }
    }


def create_audio_content(audio_base64: str, format: str = "wav") -> Dict[str, Any]:
    """
    Create an audio content object for OpenRouter.

    Note: Audio inputs only support base64 encoding, not URLs.

    Args:
        audio_base64: Base64-encoded audio data
        format: Audio format ("wav" or "mp3")

    Returns:
        Content dict with type "input_audio"
    """
    return {
        "type": "input_audio",
        "input_audio": {
            "data": audio_base64,
            "format": format
        }
    }


def create_video_content(video_data: str, is_url: bool = True) -> Dict[str, Any]:
    """
    Create a video content object for OpenRouter.

    Args:
        video_data: Either a URL or base64-encoded video string
        is_url: True if video_data is a URL, False if it's base64

    Returns:
        Content dict with type "input_video"
    """
    if is_url:
        url = video_data
    else:
        # Assume it's already in data URL format: data:video/mp4;base64,{base64_data}
        if not video_data.startswith("data:video/"):
            # Add data URL prefix if missing
            url = f"data:video/mp4;base64,{video_data}"
        else:
            url = video_data

    return {
        "type": "input_video",
        "video_url": {
            "url": url
        }
    }
