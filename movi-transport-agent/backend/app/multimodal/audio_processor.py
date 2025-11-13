"""
Audio processing utilities for speech-to-text using Gemini 2.5.
"""
from typing import Union, Dict, Any
from pathlib import Path

from .gemini_wrapper import GeminiMultimodalProcessor, MultimodalInput


async def transcribe_audio(
    audio_file: Union[str, Path],
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Transcribe audio file to text using Gemini 2.5.

    Args:
        audio_file: Path to audio file (wav or mp3)
        current_page: Current UI page context

    Returns:
        Dictionary with transcription and extracted entities:
        {
            "transcription": str,  # The transcribed text
            "comprehension": str,  # What Gemini understood
            "extracted_entities": { ... },  # Structured data
            "original_text": str,
            "modality": "audio"
        }
    """
    processor = GeminiMultimodalProcessor()

    try:
        multimodal_input = MultimodalInput(
            text="Please transcribe this audio and extract any transport management commands or queries.",
            audio_file=audio_file,
            current_page=current_page
        )

        result = await processor.process_multimodal_input(multimodal_input)

        # Add transcription key (alias for comprehension)
        result["transcription"] = result.get("comprehension", "")

        return result

    finally:
        await processor.close()


async def process_voice_command(
    audio_file: Union[str, Path],
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Process voice command for transport operations.

    This is a convenience function that transcribes audio and extracts
    action intents and entities specific to transport management.

    Args:
        audio_file: Path to audio file
        current_page: Current UI page context

    Returns:
        Dictionary with transcription, intent, and entities
    """
    return await transcribe_audio(audio_file, current_page)
