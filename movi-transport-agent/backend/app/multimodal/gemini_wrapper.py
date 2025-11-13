"""
Gemini 2.5 Wrapper for Multimodal Input Processing.
Processes text, audio, image, and video inputs and outputs structured comprehension.
"""
import base64
import json
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

from ..utils.openrouter import (
    OpenRouterClient,
    create_text_content,
    create_image_content,
    create_audio_content,
    create_video_content
)


class MultimodalInput:
    """
    Represents a multimodal input that can be text, audio, image, or video.
    """

    def __init__(
        self,
        text: Optional[str] = None,
        audio_file: Optional[Union[str, Path]] = None,
        image_file: Optional[Union[str, Path]] = None,
        video_file: Optional[Union[str, Path]] = None,
        current_page: str = "busDashboard"
    ):
        """
        Initialize multimodal input.

        Args:
            text: Text input
            audio_file: Path to audio file or URL
            image_file: Path to image file or URL
            video_file: Path to video file or URL
            current_page: Current UI page context for better understanding
        """
        self.text = text
        self.audio_file = audio_file
        self.image_file = image_file
        self.video_file = video_file
        self.current_page = current_page


class GeminiMultimodalProcessor:
    """
    Processes multimodal inputs using Gemini 2.5 Pro via OpenRouter.

    Handles:
    - Text: pass through
    - Audio: transcribe to text
    - Image: extract UI elements, trip names, visual pointers
    - Video: extract key frames + temporal context
    """

    TRANSPORT_SYSTEM_PROMPT = """You are processing input for a transport management system called "MoveInSync Shuttle".

The system operates on this data flow:
- Static Assets: Stops -> Paths -> Routes (managed on manageRoute page)
- Dynamic Operations: Deployments -> Trips -> Trip-Sheets (managed on busDashboard page)

Your task is to extract structured information from user input:

1. **Action Intent**: What the user wants to do (e.g., "remove_vehicle", "assign_vehicle", "create_stop", "list_trips")
2. **Entities**: Specific identifiers mentioned:
   - Trip IDs or names (e.g., "Bulk - 00:01", "Path Path - 00:02")
   - Vehicle IDs or license plates (e.g., "MH-12-3456", "KA-01-1234")
   - Stop names (e.g., "Gavipuram", "Peenya")
   - Path names (e.g., "Path-1", "Tech-Loop")
   - Route names (e.g., "Path2 - 19:45")
3. **Visual Indicators**: If processing an image/video, identify:
   - UI elements being pointed to (arrows, circles, highlights)
   - Selected rows or items
   - Button or action locations

Current UI context: {current_page}

Respond in JSON format with this structure:
{{
  "comprehension": "A clear natural language description of what the user wants",
  "action_intent": "The primary action (e.g., remove_vehicle, assign_vehicle, create_stop, list_trips, help)",
  "extracted_entities": {{
    "trip_ids": ["list of trip IDs or display names"],
    "vehicle_ids": ["list of vehicle IDs or license plates"],
    "stop_names": ["list of stop names"],
    "path_names": ["list of path names"],
    "route_names": ["list of route names"],
    "visual_indicators": ["description of visual pointers like arrows, highlights"]
  }},
  "confidence": "high|medium|low"
}}
"""

    def __init__(self, openrouter_client: Optional[OpenRouterClient] = None):
        """
        Initialize the Gemini multimodal processor.

        Args:
            openrouter_client: Optional OpenRouter client. If not provided, creates one.
        """
        self.client = openrouter_client or OpenRouterClient()

    async def process_multimodal_input(
        self,
        multimodal_input: MultimodalInput
    ) -> Dict[str, Any]:
        """
        Process multimodal input and return structured output.

        Args:
            multimodal_input: The multimodal input to process

        Returns:
            Dictionary with structure:
            {
                "original_text": str,
                "modality": "text|audio|image|video|mixed",
                "comprehension": str,
                "extracted_entities": {
                    "trip_ids": [],
                    "vehicle_ids": [],
                    "action_intent": str
                }
            }
        """
        # Determine modality
        modality = self._determine_modality(multimodal_input)

        # Build messages for OpenRouter
        messages = await self._build_messages(multimodal_input)

        # Call Gemini via OpenRouter
        try:
            response = await self.client.chat_completion(
                messages=messages,
                temperature=0.1,  # Lower for faster, consistent extraction
                max_tokens=500  # Reduced for faster responses
            )

            # Parse response
            gemini_output = response["choices"][0]["message"]["content"]

            # Clean markdown code blocks if present
            cleaned_output = gemini_output.strip()
            if cleaned_output.startswith("```json"):
                cleaned_output = cleaned_output[7:]  # Remove ```json
            elif cleaned_output.startswith("```"):
                cleaned_output = cleaned_output[3:]  # Remove ```
            if cleaned_output.endswith("```"):
                cleaned_output = cleaned_output[:-3]  # Remove trailing ```
            cleaned_output = cleaned_output.strip()

            # Try to parse as JSON
            parsed_output = None
            try:
                parsed_output = json.loads(cleaned_output)
                comprehension = parsed_output.get("comprehension", gemini_output)
                action_intent = parsed_output.get("action_intent", "unknown")
                extracted_entities = parsed_output.get("extracted_entities", {})
            except json.JSONDecodeError:
                # Fallback if Gemini doesn't return valid JSON
                comprehension = gemini_output
                action_intent = "unknown"
                extracted_entities = {}

            return {
                "original_text": multimodal_input.text or "",
                "modality": modality,
                "comprehension": comprehension,
                "extracted_entities": {
                    "trip_ids": extracted_entities.get("trip_ids", []),
                    "vehicle_ids": extracted_entities.get("vehicle_ids", []),
                    "stop_names": extracted_entities.get("stop_names", []),
                    "path_names": extracted_entities.get("path_names", []),
                    "route_names": extracted_entities.get("route_names", []),
                    "visual_indicators": extracted_entities.get("visual_indicators", []),
                    "action_intent": action_intent
                },
                "confidence": parsed_output.get("confidence", "medium") if isinstance(parsed_output, dict) else "medium"
            }

        except Exception as e:
            return {
                "original_text": multimodal_input.text or "",
                "modality": modality,
                "comprehension": f"Error processing input: {str(e)}",
                "extracted_entities": {
                    "trip_ids": [],
                    "vehicle_ids": [],
                    "action_intent": "error"
                },
                "error": str(e)
            }

    def _determine_modality(self, multimodal_input: MultimodalInput) -> str:
        """Determine the input modality."""
        modalities = []
        if multimodal_input.text:
            modalities.append("text")
        if multimodal_input.audio_file:
            modalities.append("audio")
        if multimodal_input.image_file:
            modalities.append("image")
        if multimodal_input.video_file:
            modalities.append("video")

        if len(modalities) == 0:
            return "text"
        elif len(modalities) == 1:
            return modalities[0]
        else:
            return "mixed"

    async def _build_messages(
        self,
        multimodal_input: MultimodalInput
    ) -> List[Dict[str, Any]]:
        """Build OpenRouter messages from multimodal input."""
        # System message with transport context
        system_message = {
            "role": "system",
            "content": self.TRANSPORT_SYSTEM_PROMPT.format(
                current_page=multimodal_input.current_page
            )
        }

        # User message with multimodal content
        user_content = []

        # Add text prompt (always first)
        prompt_text = multimodal_input.text or "Please analyze this input and extract relevant transport management information."
        user_content.append(create_text_content(prompt_text))

        # Add image if provided
        if multimodal_input.image_file:
            image_content = await self._process_image(multimodal_input.image_file)
            user_content.append(image_content)

        # Add audio if provided
        if multimodal_input.audio_file:
            audio_content = await self._process_audio(multimodal_input.audio_file)
            user_content.append(audio_content)

        # Add video if provided
        if multimodal_input.video_file:
            video_content = await self._process_video(multimodal_input.video_file)
            user_content.append(video_content)

        user_message = {
            "role": "user",
            "content": user_content
        }

        return [system_message, user_message]

    async def _process_image(self, image_source: Union[str, Path]) -> Dict[str, Any]:
        """Process image input (URL or file path)."""
        image_source = str(image_source)

        # Check if it's a URL
        if image_source.startswith(("http://", "https://")):
            return create_image_content(image_source, is_url=True)

        # Otherwise, read file and convert to base64
        image_path = Path(image_source)
        if not image_path.exists():
            raise FileNotFoundError(f"Image file not found: {image_source}")

        # Determine image format from extension
        ext = image_path.suffix.lower()
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }
        mime_type = mime_types.get(ext, "image/jpeg")

        with open(image_path, "rb") as f:
            image_bytes = f.read()
            base64_image = base64.b64encode(image_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{base64_image}"

        return create_image_content(data_url, is_url=False)

    async def _process_audio(self, audio_source: Union[str, Path]) -> Dict[str, Any]:
        """Process audio input (file path only, URLs not supported)."""
        audio_source = str(audio_source)

        # Audio URLs are not supported by OpenRouter
        if audio_source.startswith(("http://", "https://")):
            raise ValueError("Audio URLs are not supported. Please provide a file path.")

        # Read file and convert to base64
        audio_path = Path(audio_source)
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_source}")

        # Determine audio format from extension
        ext = audio_path.suffix.lower()
        audio_format = "wav" if ext in [".wav", ".wave"] else "mp3"

        with open(audio_path, "rb") as f:
            audio_bytes = f.read()
            base64_audio = base64.b64encode(audio_bytes).decode("utf-8")

        return create_audio_content(base64_audio, format=audio_format)

    async def _process_video(self, video_source: Union[str, Path]) -> Dict[str, Any]:
        """Process video input (URL or file path)."""
        video_source = str(video_source)

        # Check if it's a URL (including YouTube)
        if video_source.startswith(("http://", "https://")):
            return create_video_content(video_source, is_url=True)

        # Otherwise, read file and convert to base64
        video_path = Path(video_source)
        if not video_path.exists():
            raise FileNotFoundError(f"Video file not found: {video_source}")

        # Determine video format from extension
        ext = video_path.suffix.lower()
        mime_types = {
            ".mp4": "video/mp4",
            ".mpeg": "video/mpeg",
            ".mov": "video/mov",
            ".webm": "video/webm"
        }
        mime_type = mime_types.get(ext, "video/mp4")

        with open(video_path, "rb") as f:
            video_bytes = f.read()
            base64_video = base64.b64encode(video_bytes).decode("utf-8")
            data_url = f"data:{mime_type};base64,{base64_video}"

        return create_video_content(data_url, is_url=False)

    async def close(self):
        """Close the OpenRouter client."""
        await self.client.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
