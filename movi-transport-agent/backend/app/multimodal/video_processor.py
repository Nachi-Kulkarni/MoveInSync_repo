"""
Video processing utilities for extracting key frames and temporal context using Gemini 2.5.
"""
from typing import Union, Dict, Any, Optional
from pathlib import Path

from .gemini_wrapper import GeminiMultimodalProcessor, MultimodalInput


async def analyze_video(
    video_file: Union[str, Path],
    user_query: Optional[str] = None,
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Analyze a video using Gemini 2.5.

    Extracts:
    - Key frames and actions
    - Temporal context (sequence of events)
    - UI interactions shown in the video
    - Transport-related entities (trips, vehicles, routes)

    Args:
        video_file: Path to video file or URL (YouTube links supported for Gemini)
        user_query: Optional text query about the video
        current_page: Current UI page context

    Returns:
        Dictionary with analysis results:
        {
            "comprehension": str,  # What Gemini understood from the video
            "extracted_entities": {
                "trip_ids": [],
                "vehicle_ids": [],
                "action_intent": str
            },
            "modality": "video",
            "temporal_summary": str  # Sequence of events
        }
    """
    processor = GeminiMultimodalProcessor()

    try:
        prompt = user_query or (
            "Analyze this video from the transport management system. "
            "Provide: "
            "1) A temporal summary of what happens in the video (sequence of events) "
            "2) Any trip names or IDs visible "
            "3) Vehicle IDs or license plates shown "
            "4) UI interactions or actions performed "
            "5) The overall intent or purpose of the video"
        )

        multimodal_input = MultimodalInput(
            text=prompt,
            video_file=video_file,
            current_page=current_page
        )

        result = await processor.process_multimodal_input(multimodal_input)

        # Add temporal summary (alias for comprehension)
        result["temporal_summary"] = result.get("comprehension", "")

        return result

    finally:
        await processor.close()


async def extract_key_frames(
    video_file: Union[str, Path],
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Extract key frames and their context from a video.

    This focuses on identifying the most important moments
    and visual information in the video.

    Args:
        video_file: Path to video file or URL
        current_page: Current UI page context

    Returns:
        Dictionary with key frame analysis
    """
    return await analyze_video(
        video_file=video_file,
        user_query=(
            "Identify the key frames in this video. "
            "For each important moment, describe: "
            "1) What is visible (UI elements, data) "
            "2) What action is being performed "
            "3) Any trips, vehicles, or routes mentioned or shown"
        ),
        current_page=current_page
    )


async def process_ui_demo_video(
    video_file: Union[str, Path],
    user_query: str,
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Process a video demonstration of UI interactions.

    This is useful for understanding user workflows, tutorials,
    or recorded sessions showing transport management tasks.

    Args:
        video_file: Path to video file or URL
        user_query: User's question about the video
        current_page: Current UI page context

    Returns:
        Dictionary with workflow analysis and extracted entities
    """
    processor = GeminiMultimodalProcessor()

    try:
        prompt = (
            f"{user_query}\n\n"
            "This is a screen recording or demo of the transport management system. "
            "Analyze the workflow shown, identify all actions performed, "
            "and extract any relevant trip, vehicle, or route information."
        )

        multimodal_input = MultimodalInput(
            text=prompt,
            video_file=video_file,
            current_page=current_page
        )

        result = await processor.process_multimodal_input(multimodal_input)
        return result

    finally:
        await processor.close()


async def stream_video_analysis(
    video_file: Union[str, Path],
    user_query: Optional[str] = None,
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Stream analysis for longer videos (>30 seconds).

    Note: Actual streaming depends on OpenRouter/Gemini support.
    For now, this processes the video normally but is designed
    to handle longer content.

    Args:
        video_file: Path to video file or URL
        user_query: Optional text query
        current_page: Current UI page context

    Returns:
        Dictionary with video analysis (may be summarized for long videos)
    """
    # For videos >30s, Gemini may automatically summarize
    # The TICKET #4 requirement mentions "streaming response for video (if >30s)"
    return await analyze_video(
        video_file=video_file,
        user_query=user_query or "Provide a comprehensive summary of this video, focusing on key moments and transport operations.",
        current_page=current_page
    )
