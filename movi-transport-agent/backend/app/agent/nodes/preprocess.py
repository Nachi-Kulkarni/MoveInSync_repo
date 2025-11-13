"""
Preprocess Input Node (TICKET #5 - Phase 4a)

This node handles multimodal input preprocessing using Gemini 2.5 Pro.
Supports: text, images, audio, video in any combination.

Responsibilities:
1. Process all input modalities (text/audio/image/video)
2. Extract entities and context indicators
3. Prepare structured input for classification node
4. Handle errors gracefully with fallback to text-only
"""

from typing import Dict, Any
from app.agent.state import AgentState
from app.multimodal.gemini_wrapper import GeminiMultimodalProcessor, MultimodalInput


async def preprocess_input_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Preprocess multimodal user input.
    
    Uses Gemini 2.5 Pro via OpenRouter to process:
    - Text messages
    - Images (screenshots, photos)
    - Audio (voice commands)
    - Video (demonstrations)
    
    Args:
        state: Current agent state with user_input and context
        
    Returns:
        State update with:
        - processed_input: Structured extraction from Gemini
        - input_modalities: List of detected modalities
        - error: Error message if processing fails
    """
    try:
        # Get input and context
        user_input = state.get("user_input", "")
        context = state.get("context", {})
        
        # Detect input type
        # For now, assume text-only (Phase 4a focuses on text)
        # Future: Detect images/audio/video from file paths or base64
        input_modalities = ["text"]
        
        # Create multimodal input
        multimodal_input = MultimodalInput(
            text=user_input,
            audio_file=None,  # Future: Extract from context
            image_file=None,  # Future: Extract from context
            video_file=None,  # Future: Extract from context
            current_page=context.get("page", "busDashboard")
        )
        
        # Process with Gemini
        processor = GeminiMultimodalProcessor()
        processed_result = await processor.process_multimodal_input(multimodal_input)
        
        # Return state update
        return {
            "processed_input": processed_result,
            "input_modalities": input_modalities,
            "error": None,
        }
        
    except Exception as e:
        # Fallback: Return raw input with error
        return {
            "processed_input": {
                "original_text": state.get("user_input", ""),
                "modality": "text",
                "comprehension": f"Error during preprocessing: {str(e)}",
                "extracted_entities": {},
                "confidence": "low"
            },
            "input_modalities": ["text"],
            "error": f"Preprocessing failed: {str(e)}",
            "error_node": "preprocess_input_node"
        }
