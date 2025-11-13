"""
Multimodal input processing module for Movi Transport Agent.

This module provides utilities for processing text, audio, image, and video
inputs using Gemini 2.5 Pro via OpenRouter.

Main exports:
- GeminiMultimodalProcessor: Core processor for all modalities
- MultimodalInput: Input data class
- transcribe_audio: Audio transcription
- analyze_screenshot: Image analysis
- analyze_video: Video analysis
"""

from .gemini_wrapper import (
    GeminiMultimodalProcessor,
    MultimodalInput
)
from .audio_processor import (
    transcribe_audio,
    process_voice_command
)
from .image_processor import (
    analyze_screenshot,
    extract_ui_elements,
    process_annotated_screenshot
)
from .video_processor import (
    analyze_video,
    extract_key_frames,
    process_ui_demo_video,
    stream_video_analysis
)

__all__ = [
    # Core classes
    "GeminiMultimodalProcessor",
    "MultimodalInput",
    # Audio processing
    "transcribe_audio",
    "process_voice_command",
    # Image processing
    "analyze_screenshot",
    "extract_ui_elements",
    "process_annotated_screenshot",
    # Video processing
    "analyze_video",
    "extract_key_frames",
    "process_ui_demo_video",
    "stream_video_analysis",
]
