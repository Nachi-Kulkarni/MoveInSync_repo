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

import re
from typing import Dict, Any, List
from app.agent.state import AgentState
from app.multimodal.gemini_wrapper import GeminiMultimodalProcessor, MultimodalInput


def extract_entities_from_text(text: str) -> Dict[str, Any]:
    """
    Extract entities from text using regex patterns (lightweight alternative to Gemini).
    Used for text-only inputs to maintain performance while providing basic entity extraction.

    Args:
        text: The text to extract entities from

    Returns:
        Dictionary with extracted entities and action intent
    """
    entities = {
        "trip_ids": [],
        "vehicle_ids": [],
        "stop_names": [],
        "path_names": [],
        "route_names": [],
        "action_intent": "unknown"
    }

    # Extract vehicle IDs (patterns like MH-12-3456, KA-01-1234)
    vehicle_pattern = r'\b[A-Z]{2}-\d{2}-[A-Z0-9]{4}\b'
    vehicles = re.findall(vehicle_pattern, text, re.IGNORECASE)
    if vehicles:
        entities["vehicle_ids"] = vehicles

    # Extract trip display names (patterns like "Bulk - 00:01", "Path Path - 00:02")
    # This matches: word(s) - time format
    trip_pattern = r'\b(?:[A-Z][a-z]+(?: [A-Z][a-z]+)*)\s*-\s*\d{2}:\d{2}\b'
    trips = re.findall(trip_pattern, text)
    if trips:
        entities["trip_ids"] = trips

    # Common stop names (from seed data)
    known_stops = [
        "Gavipuram", "Peenya", "Temple", "BTM", "Hebbal",
        "Madiwala", "Jayanagar", "Koramangala", "Electronic City", "Whitefield"
    ]
    for stop in known_stops:
        if stop.lower() in text.lower():
            entities["stop_names"].append(stop)

    # Extract path names (patterns like "Path-1", "Path-2")
    path_pattern = r'\bPath-\d+\b'
    paths = re.findall(path_pattern, text, re.IGNORECASE)
    if paths:
        entities["path_names"] = paths

    # Infer action intent from keywords
    text_lower = text.lower()
    if any(word in text_lower for word in ["remove", "delete", "unassign"]):
        entities["action_intent"] = "remove_vehicle"
    elif any(word in text_lower for word in ["assign", "add", "deploy", "attach"]):
        entities["action_intent"] = "assign_vehicle"
    elif any(word in text_lower for word in ["create", "add new"]):
        if "stop" in text_lower:
            entities["action_intent"] = "create_stop"
        elif "path" in text_lower:
            entities["action_intent"] = "create_path"
        elif "route" in text_lower:
            entities["action_intent"] = "create_route"
        else:
            entities["action_intent"] = "create"
    elif any(word in text_lower for word in ["list", "show", "display", "get"]):
        if "unassigned" in text_lower and "vehicle" in text_lower:
            entities["action_intent"] = "list_unassigned_vehicles"
        elif "trip" in text_lower:
            entities["action_intent"] = "list_trips"
        elif "route" in text_lower:
            entities["action_intent"] = "list_routes"
        else:
            entities["action_intent"] = "list"
    elif any(word in text_lower for word in ["status", "check", "what", "how many"]):
        entities["action_intent"] = "query_status"

    return entities


async def preprocess_input_node(state: AgentState) -> Dict[str, Any]:
    """
    Node 1: Preprocess multimodal user input.

    OPTIMIZATION: Skip Gemini for simple text-only queries (95% of requests)
    Only use Gemini when multimodal content is present (images/audio/video)

    Uses Gemini 2.5 Pro via OpenRouter to process:
    - Text messages (SKIP for simple queries)
    - Images (screenshots, photos) - USE GEMINI
    - Audio (voice commands) - USE GEMINI
    - Video (demonstrations) - USE GEMINI

    Args:
        state: Current agent state with user_input and context

    Returns:
        State update with:
        - processed_input: Structured extraction (from Gemini or passthrough)
        - input_modalities: List of detected modalities
        - error: Error message if processing fails
    """
    try:
        # CRITICAL: Skip preprocessing if state already has processed_input (confirmation flow)
        # This preserves the restored state from the session
        if state.get("user_confirmed") and state.get("processed_input"):
            print("\n" + "⏭️ "*50)
            print("⏭️  SKIPPING PREPROCESS - State already processed (confirmation flow)")
            print("⏭️ "*50 + "\n")
            return {}  # Return empty dict to preserve existing state
        
        print("\n" + "🔧"*50)
        print("🔧 BACKEND PREPROCESS NODE - preprocess_input_node()")
        print("🔧"*50)

        # Get input and context
        user_input = state.get("user_input", "")
        context = state.get("context", {})
        multimodal_data = state.get("multimodal_data", {}) or {}

        print(f"📝 User Input: {user_input}")
        print(f"🗂️  Context keys: {list(context.keys())}")
        print(f"📦 Multimodal data keys: {list(multimodal_data.keys())}")
        if multimodal_data:
            for key, val in multimodal_data.items():
                if isinstance(val, list):
                    print(f"   - {key}: list with {len(val)} items")
                    for i, item in enumerate(val):
                        print(f"     [{i}]: {type(item).__name__} ({len(item) if isinstance(item, str) else 0} chars)")
                else:
                    print(f"   - {key}: {type(val).__name__} ({len(val) if isinstance(val, str) else 0} chars)")

        # Detect input type - check both context and multimodal_data
        has_image = (multimodal_data.get("images") or
                    context.get("image_file") or
                    context.get("image_url") or
                    context.get("image_base64"))
        has_audio = (multimodal_data.get("audio") or
                    context.get("audio_file") or
                    context.get("audio_base64"))
        has_video = (multimodal_data.get("video") or
                    context.get("video_file") or
                    context.get("video_url"))
        has_multimodal = has_image or has_audio or has_video

        print(f"\n🔍 Multimodal Detection:")
        print(f"   - has_image: {bool(has_image)}")
        print(f"   - has_audio: {bool(has_audio)}")
        print(f"   - has_video: {bool(has_video)}")
        print(f"   - has_multimodal: {bool(has_multimodal)}")

        # OPTIMIZATION: Skip Gemini for text-only queries
        if not has_multimodal:
            print(f"\n⚡ Text-only mode - skipping Gemini (OPTIMIZATION)")
            # Use lightweight regex-based entity extraction (saves 2-3s per request vs Gemini)
            extracted_entities = extract_entities_from_text(user_input)
            print(f"   Extracted entities: {extracted_entities}")

            return {
                "processed_input": {
                    "original_text": user_input,
                    "modality": "text",
                    "comprehension": user_input,  # Claude will classify directly
                    "extracted_entities": extracted_entities,
                    "confidence": "high"
                },
                "input_modalities": ["text"],
                "error": None,
            }

        # Multimodal content detected - use Gemini
        print(f"\n🎬 Multimodal mode detected - calling Gemini!")
        input_modalities = ["text"]
        if has_image:
            input_modalities.append("image")
        if has_audio:
            input_modalities.append("audio")
        if has_video:
            input_modalities.append("video")
        print(f"   Input modalities: {input_modalities}")

        # Create multimodal input
        # Priority: use base64 from multimodal_data, fallback to file paths
        image_base64_data = multimodal_data.get("images", [None])[0] if multimodal_data.get("images") else None
        print(f"\n📸 Image data preparation:")
        print(f"   - image_file from context: {context.get('image_file')}")
        print(f"   - image_base64 from multimodal_data: {len(image_base64_data) if image_base64_data else 0} chars")

        multimodal_input = MultimodalInput(
            text=user_input,
            audio_file=context.get("audio_file"),
            image_file=context.get("image_file"),
            video_file=context.get("video_file"),
            current_page=context.get("page", "busDashboard"),
            # Add base64 data from multimodal_data
            image_base64=image_base64_data,
            audio_base64=multimodal_data.get("audio"),
            video_base64=multimodal_data.get("video")
        )

        print(f"\n🚀 Calling GeminiMultimodalProcessor.process_multimodal_input()...")
        # Process with Gemini (only for multimodal)
        try:
            processor = GeminiMultimodalProcessor()
            processed_result = await processor.process_multimodal_input(multimodal_input)
            print(f"✅ Gemini processing complete!")
            print(f"   Extracted entities: {processed_result.get('extracted_entities', {})}")
            print("🔧"*50 + "\n")

            return {
                "processed_input": processed_result,
                "input_modalities": input_modalities,
                "error": None,
            }
        except Exception as gemini_error:
            # Graceful fallback if Gemini API fails
            print(f"❌ Gemini processing failed: {str(gemini_error)}")
            print("🔧"*50 + "\n")
            return {
                "processed_input": {
                    "original_text": user_input,
                    "modality": "mixed",
                    "comprehension": f"Multimodal processing unavailable. Text: {user_input}",
                    "extracted_entities": {},
                    "confidence": "medium"
                },
                "input_modalities": input_modalities,
                "error": None,  # Don't fail the request, just skip Gemini
                "warning": f"Gemini API unavailable: {str(gemini_error)}"
            }

    except Exception as e:
        # Fallback: Return raw input with error
        return {
            "processed_input": {
                "original_text": state.get("user_input", ""),
                "modality": "text",
                "comprehension": state.get("user_input", ""),
                "extracted_entities": {},
                "confidence": "low"
            },
            "input_modalities": ["text"],
            "error": None,  # Don't fail - let Claude classify handle it
            "warning": f"Preprocessing error: {str(e)}"
        }
