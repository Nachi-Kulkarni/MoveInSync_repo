"""
Image processing utilities for UI element extraction using Gemini 2.5 Vision.
"""
from typing import Union, Dict, Any, Optional
from pathlib import Path

from .gemini_wrapper import GeminiMultimodalProcessor, MultimodalInput


async def analyze_screenshot(
    image_file: Union[str, Path],
    user_query: Optional[str] = None,
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Analyze a screenshot of the transport management UI.

    Extracts:
    - UI elements (buttons, rows, tables)
    - Trip names and IDs
    - Vehicle information
    - Visual indicators (arrows, highlights, selections)

    Args:
        image_file: Path to image file or URL
        user_query: Optional text query about the image
        current_page: Current UI page context

    Returns:
        Dictionary with analysis results:
        {
            "comprehension": str,  # What Gemini understood from the image
            "extracted_entities": {
                "trip_ids": [],
                "vehicle_ids": [],
                "visual_indicators": [],
                "action_intent": str
            },
            "modality": "image"
        }
    """
    processor = GeminiMultimodalProcessor()

    try:
        prompt = user_query or (
            "Analyze this screenshot from the transport management system. "
            "Identify: "
            "1) Any trip names or IDs visible (e.g., 'Bulk - 00:01') "
            "2) Vehicle IDs or license plates "
            "3) Visual indicators like arrows, circles, or highlights pointing to specific items "
            "4) The user's intended action based on visual cues "
            "5) Any UI elements being referenced (buttons, rows, etc.)"
        )

        multimodal_input = MultimodalInput(
            text=prompt,
            image_file=image_file,
            current_page=current_page
        )

        result = await processor.process_multimodal_input(multimodal_input)
        return result

    finally:
        await processor.close()


async def extract_ui_elements(
    image_file: Union[str, Path],
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Extract specific UI elements from a screenshot.

    Focuses on identifying:
    - Table rows and their data
    - Selected items
    - Button states
    - Form fields

    Args:
        image_file: Path to image file or URL
        current_page: Current UI page context

    Returns:
        Dictionary with extracted UI elements
    """
    return await analyze_screenshot(
        image_file=image_file,
        user_query="Extract all visible UI elements, including table rows, buttons, and form fields. List all trips, vehicles, and any data shown.",
        current_page=current_page
    )


async def process_annotated_screenshot(
    image_file: Union[str, Path],
    user_query: str,
    current_page: str = "busDashboard"
) -> Dict[str, Any]:
    """
    Process a screenshot with user annotations (arrows, circles, etc.).

    This is particularly useful for the assignment requirement:
    "The user uploads a screenshot of the busDashboard and says,
    'Remove the vehicle from this trip' (the screenshot could have a red
    arrow pointing to the 'Bulk - 00:01' row)."

    Args:
        image_file: Path to annotated image file or URL
        user_query: User's text query (e.g., "Remove the vehicle from this trip")
        current_page: Current UI page context

    Returns:
        Dictionary with intent and identified target
    """
    processor = GeminiMultimodalProcessor()

    try:
        prompt = (
            f"{user_query}\n\n"
            "Important: This screenshot may contain visual indicators (arrows, circles, highlights) "
            "pointing to specific items. Identify what the visual indicator is pointing to, "
            "especially trip names, vehicle IDs, or table rows."
        )

        multimodal_input = MultimodalInput(
            text=prompt,
            image_file=image_file,
            current_page=current_page
        )

        result = await processor.process_multimodal_input(multimodal_input)
        return result

    finally:
        await processor.close()
