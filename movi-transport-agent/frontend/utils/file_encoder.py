"""
File encoding utilities for multimodal input.
Converts files to base64 for API transmission.
"""

import base64
from typing import Optional


def encode_file_to_base64(filepath: Optional[str]) -> Optional[str]:
    """
    Convert a file to base64 string for API transmission.

    Args:
        filepath: Path to the file to encode

    Returns:
        Base64-encoded string, or None if filepath is None/empty

    Example:
        >>> audio_b64 = encode_file_to_base64("/tmp/audio.wav")
        >>> # Send to backend in multimodal_data field
    """
    if not filepath:
        return None

    try:
        with open(filepath, "rb") as f:
            file_bytes = f.read()
            b64_string = base64.b64encode(file_bytes).decode("utf-8")
            return b64_string
    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return None
    except Exception as e:
        print(f"Error encoding file {filepath}: {e}")
        return None


def get_file_data_url(filepath: Optional[str], mime_type: str) -> Optional[str]:
    """
    Convert a file to a data URL (base64 with MIME type).

    Args:
        filepath: Path to the file
        mime_type: MIME type (e.g., "audio/wav", "image/png")

    Returns:
        Data URL string, or None if filepath is None/empty

    Example:
        >>> data_url = get_file_data_url("/tmp/image.png", "image/png")
        >>> # Returns: "data:image/png;base64,iVBORw0K..."
    """
    b64_string = encode_file_to_base64(filepath)
    if not b64_string:
        return None

    return f"data:{mime_type};base64,{b64_string}"
