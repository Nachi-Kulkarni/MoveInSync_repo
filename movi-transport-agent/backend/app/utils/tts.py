"""
OpenAI Text-to-Speech (TTS) utility.

Uses OpenAI's gpt-4o-mini-tts model to convert text responses to audio.
Supports streaming for real-time playback.
"""
from typing import Optional, Literal
from io import BytesIO
from openai import AsyncOpenAI
from app.core.config import settings


# Voice options for OpenAI TTS
Voice = Literal["alloy", "ash", "ballad", "coral", "echo", "fable", "nova", "onyx", "sage", "shimmer"]

# Audio format options
AudioFormat = Literal["mp3", "opus", "aac", "flac", "wav", "pcm"]


class TTSClient:
    """
    OpenAI Text-to-Speech client using gpt-4o-mini-tts model.

    Features:
    - 11 built-in voices
    - Multiple output formats
    - Streaming support for real-time playback
    - Customizable instructions (tone, speed, emotion, etc.)
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize TTS client.

        Args:
            api_key: OpenAI API key. If not provided, uses settings.
        """
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.client = AsyncOpenAI(api_key=self.api_key)

    async def generate_speech(
        self,
        text: str,
        voice: Voice = "coral",
        response_format: AudioFormat = "mp3",
        instructions: Optional[str] = None,
        speed: float = 1.0
    ) -> bytes:
        """
        Generate speech audio from text.

        Args:
            text: Text to convert to speech
            voice: Voice to use (default: "coral" - cheerful and friendly)
            response_format: Audio format (default: "mp3")
            instructions: Custom instructions for speech (tone, accent, emotion, etc.)
            speed: Speech speed (0.25 to 4.0, default: 1.0)

        Returns:
            Audio file bytes

        Example:
            >>> tts = TTSClient()
            >>> audio = await tts.generate_speech(
            ...     "Hello! I'm Movi, your transport assistant.",
            ...     voice="coral",
            ...     instructions="Speak in a cheerful and helpful tone."
            ... )
        """
        # Default instructions for Movi
        if instructions is None:
            instructions = "Speak clearly and professionally as a helpful transport assistant."

        response = await self.client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            response_format=response_format,
            instructions=instructions,
            speed=speed
        )

        # Return audio bytes
        return response.content

    async def generate_speech_streaming(
        self,
        text: str,
        voice: Voice = "coral",
        response_format: AudioFormat = "wav",
        instructions: Optional[str] = None,
        speed: float = 1.0
    ):
        """
        Generate speech with streaming for real-time playback.

        Args:
            text: Text to convert to speech
            voice: Voice to use
            response_format: Audio format (recommended: "wav" or "pcm" for low latency)
            instructions: Custom instructions for speech
            speed: Speech speed (0.25 to 4.0)

        Yields:
            Audio chunk bytes

        Example:
            >>> tts = TTSClient()
            >>> async with tts.generate_speech_streaming(
            ...     "Processing your request...",
            ...     response_format="wav"
            ... ) as stream:
            ...     async for chunk in stream:
            ...         # Send chunk to frontend
            ...         yield chunk
        """
        if instructions is None:
            instructions = "Speak clearly and professionally as a helpful transport assistant."

        async with self.client.audio.speech.with_streaming_response.create(
            model="gpt-4o-mini-tts",
            voice=voice,
            input=text,
            response_format=response_format,
            instructions=instructions,
            speed=speed
        ) as response:
            async for chunk in response.iter_bytes(chunk_size=1024):
                yield chunk


# Singleton instance
_tts_client: Optional[TTSClient] = None


def get_tts_client() -> TTSClient:
    """
    Get or create TTS client singleton.

    Returns:
        TTSClient instance
    """
    global _tts_client
    if _tts_client is None:
        _tts_client = TTSClient()
    return _tts_client


async def text_to_speech(
    text: str,
    voice: Voice = "coral",
    streaming: bool = False
):
    """
    Convert text to speech audio.

    Args:
        text: Text to convert
        voice: Voice to use
        streaming: Whether to use streaming (for real-time playback)

    Returns:
        Audio bytes (if not streaming) or async generator (if streaming)

    Example (non-streaming):
        >>> audio_bytes = await text_to_speech("Hello, welcome to Movi!")

    Example (streaming):
        >>> async for chunk in text_to_speech("Hello!", streaming=True):
        ...     # Send chunk to frontend
        ...     yield chunk
    """
    tts = get_tts_client()

    if streaming:
        return tts.generate_speech_streaming(text, voice=voice, response_format="wav")
    else:
        return await tts.generate_speech(text, voice=voice)
