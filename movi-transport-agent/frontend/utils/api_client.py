"""
API client for communicating with Movi backend.
Handles agent messages, confirmations, and TTS requests.
"""

import httpx
import os
from typing import Dict, Any, Optional, Tuple


# Backend URL from environment or default
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
API_BASE = f"{BACKEND_URL}/api/v1"


def send_message_to_agent(
    user_input: str,
    session_id: str,
    current_page: str,
    audio_file: Optional[str] = None,
    image_file: Optional[str] = None,
    video_file: Optional[str] = None,
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Send a message to the Movi agent.

    Args:
        user_input: Text input from user
        session_id: Session identifier
        current_page: Current page context ("busDashboard" or "manageRoute")
        audio_file: Optional path to audio file
        image_file: Optional path to image file
        video_file: Optional path to video file

    Returns:
        Tuple of (response_dict, error_message)
        - response_dict: Agent response with all fields
        - error_message: Error string if request failed, None otherwise

    Example:
        >>> response, error = send_message_to_agent(
        ...     "How many unassigned vehicles?",
        ...     "session-123",
        ...     "busDashboard"
        ... )
        >>> if error:
        ...     print(f"Error: {error}")
        ... else:
        ...     print(f"Agent: {response['response']}")
    """
    from .file_encoder import encode_file_to_base64

    try:
        print("\n" + "="*80)
        print("🔍 FRONTEND API CLIENT - send_message_to_agent()")
        print("="*80)
        print(f"📝 User Input: {user_input}")
        print(f"🔑 Session ID: {session_id}")
        print(f"📍 Page Context: {current_page}")
        print(f"🎤 Audio File: {audio_file}")
        print(f"📸 Image File: {image_file}")
        print(f"🎥 Video File: {video_file}")

        # Prepare multimodal data
        multimodal_data = {}
        if audio_file:
            print(f"🎤 Encoding audio file: {audio_file}")
            multimodal_data["audio"] = encode_file_to_base64(audio_file)
            print(f"   ✅ Audio encoded: {len(multimodal_data['audio'])} chars")

        if image_file:
            print(f"📸 Encoding image file: {image_file}")
            # Backend expects "images" as a list, not "image" as string
            encoded_image = encode_file_to_base64(image_file)
            multimodal_data["images"] = [encoded_image]
            print(f"   ✅ Image encoded: {len(encoded_image)} chars")
            print(f"   ✅ Set multimodal_data['images'] = [base64_string]")

        if video_file:
            print(f"🎥 Encoding video file: {video_file}")
            multimodal_data["video"] = encode_file_to_base64(video_file)
            print(f"   ✅ Video encoded: {len(multimodal_data['video'])} chars")

        print(f"\n📦 Multimodal data keys: {list(multimodal_data.keys())}")
        if multimodal_data:
            for key, val in multimodal_data.items():
                if isinstance(val, list):
                    print(f"   - {key}: list with {len(val)} items")
                    for i, item in enumerate(val):
                        print(f"     [{i}]: {type(item).__name__} ({len(item) if isinstance(item, str) else 0} chars)")
                else:
                    print(f"   - {key}: {type(val).__name__} ({len(val) if isinstance(val, str) else 0} chars)")

        # Prepare request payload
        payload = {
            "user_input": user_input,
            "session_id": session_id,
            "context": {
                "page": current_page
            }
        }

        # Add multimodal data if present
        if multimodal_data:
            payload["multimodal_data"] = multimodal_data
            print(f"\n✅ Added multimodal_data to payload")
        else:
            print(f"\n⚠️  No multimodal data - text-only request")

        print(f"\n🚀 Sending POST to {API_BASE}/agent/message")
        print(f"📦 Payload keys: {list(payload.keys())}")
        if "multimodal_data" in payload:
            print(f"   - multimodal_data keys: {list(payload['multimodal_data'].keys())}")

        # Send request to backend
        with httpx.Client(timeout=90.0) as client:  # Increased from 30s to 90s for slower LLM responses
            response = client.post(
                f"{API_BASE}/agent/message",
                json=payload
            )

            print(f"\n📡 Response Status: {response.status_code}")

            if response.status_code == 200:
                response_data = response.json()
                print(f"✅ Response received - keys: {list(response_data.keys())}")
                if response_data.get("error"):
                    print(f"❌ Error in response: {response_data.get('error')}")

                # Handle nested JSON responses
                if "response" in response_data and isinstance(response_data["response"], str):
                    try:
                        # Try to parse the inner JSON response
                        import json
                        inner_response = json.loads(response_data["response"])
                        response_data.update(inner_response)
                        print(f"   Parsed nested JSON response")
                        return response_data, None
                    except (json.JSONDecodeError, KeyError):
                        # If parsing fails, use the raw response
                        pass
                print("="*80 + "\n")
                return response_data, None
            else:
                error_msg = f"Backend error: {response.status_code} - {response.text}"
                print(f"❌ {error_msg}")
                print("="*80 + "\n")
                return {}, error_msg

    except httpx.TimeoutException:
        return {}, "Request timed out. Please try again."
    except httpx.ConnectError:
        return {}, "Unable to reach Movi backend. Please ensure the server is running."
    except Exception as e:
        return {}, f"Error communicating with agent: {str(e)}"


def send_confirmation(
    session_id: str,
    confirmed: bool,
    user_input: str,
    current_page: str
) -> Tuple[Dict[str, Any], Optional[str]]:
    """
    Send confirmation response for high-risk action.

    Args:
        session_id: Session identifier
        confirmed: True if user confirmed, False if cancelled
        user_input: Original user input that triggered confirmation
        current_page: Current page context

    Returns:
        Tuple of (response_dict, error_message)

    Example:
        >>> response, error = send_confirmation(
        ...     "session-123",
        ...     True,  # User clicked "Yes"
        ...     "Remove vehicle from Bulk - 00:01",
        ...     "busDashboard"
        ... )
    """
    try:
        payload = {
            "session_id": session_id,
            "confirmed": confirmed,
            "user_input": user_input,
            "context": {
                "page": current_page
            }
        }

        with httpx.Client(timeout=90.0) as client:  # Increased from 30s to 90s for slower LLM responses
            response = client.post(
                f"{API_BASE}/agent/confirm",
                json=payload
            )

            if response.status_code == 200:
                response_data = response.json()
                # Handle nested JSON responses for confirmation too
                if "response" in response_data and isinstance(response_data["response"], str):
                    try:
                        import json
                        inner_response = json.loads(response_data["response"])
                        response_data.update(inner_response)
                        return response_data, None
                    except (json.JSONDecodeError, KeyError):
                        # If parsing fails, use the raw response
                        pass
                return response_data, None
            else:
                error_msg = f"Confirmation error: {response.status_code} - {response.text}"
                return {}, error_msg

    except httpx.TimeoutException:
        return {}, "Request timed out. Please try again."
    except httpx.ConnectError:
        return {}, "Unable to reach Movi backend. Please ensure the server is running."
    except Exception as e:
        return {}, f"Error sending confirmation: {str(e)}"


def generate_tts(text: str, voice: str = "coral") -> Tuple[Optional[bytes], Optional[str]]:
    """
    Generate TTS audio from text.

    Args:
        text: Text to convert to speech
        voice: Voice to use (default: "coral")

    Returns:
        Tuple of (audio_bytes, error_message)
        - audio_bytes: MP3 audio data if successful, None otherwise
        - error_message: Error string if request failed, None otherwise

    Example:
        >>> audio, error = generate_tts("Hello, welcome to Movi!")
        >>> if not error and audio:
        ...     # Play audio or save to file
        ...     with open("speech.mp3", "wb") as f:
        ...         f.write(audio)
    """
    try:
        payload = {
            "text": text,
            "voice": voice,
            "streaming": False
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                f"{API_BASE}/agent/tts",
                json=payload
            )

            if response.status_code == 200:
                return response.content, None
            else:
                error_msg = f"TTS error: {response.status_code}"
                return None, error_msg

    except httpx.TimeoutException:
        return None, "TTS request timed out"
    except httpx.ConnectError:
        return None, "Unable to reach TTS service"
    except Exception as e:
        return None, f"TTS generation failed: {str(e)}"
