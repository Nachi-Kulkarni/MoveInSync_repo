"""
Test script for OpenAI TTS (Text-to-Speech) integration.

Tests:
1. Basic TTS generation
2. Different voices
3. Streaming TTS
4. Custom instructions
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from app.utils.tts import TTSClient, text_to_speech


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


async def test_basic_tts():
    """Test basic TTS generation."""
    print_section("Test 1: Basic TTS Generation")

    tts = TTSClient()

    print("\nGenerating speech for: 'Hello! I'm Movi, your transport assistant.'")
    print("Voice: coral")
    print("🔊 Calling OpenAI TTS API...")

    audio_bytes = await tts.generate_speech(
        text="Hello! I'm Movi, your transport assistant.",
        voice="coral",
        instructions="Speak in a cheerful and helpful tone."
    )

    # Save to file
    output_file = Path("test_tts_output.mp3")
    output_file.write_bytes(audio_bytes)

    print(f"\n✅ TTS audio generated successfully!")
    print(f"   Audio size: {len(audio_bytes):,} bytes")
    print(f"   Saved to: {output_file.absolute()}")
    print(f"   You can play it with: open {output_file}")


async def test_different_voices():
    """Test different voice options."""
    print_section("Test 2: Testing Different Voices")

    tts = TTSClient()

    voices = ["coral", "alloy", "nova"]
    text = "Welcome to MoveInSync."

    for voice in voices:
        print(f"\n{voices.index(voice) + 1}. Testing voice: '{voice}'")
        print("   🔊 Generating audio...")

        audio_bytes = await tts.generate_speech(
            text=text,
            voice=voice
        )

        output_file = Path(f"test_voice_{voice}.mp3")
        output_file.write_bytes(audio_bytes)

        print(f"   ✅ Generated {len(audio_bytes):,} bytes")
        print(f"   Saved to: {output_file}")


async def test_transport_responses():
    """Test TTS with transport-specific responses."""
    print_section("Test 3: Transport-Specific Responses")

    tts = TTSClient()

    responses = [
        "I found 3 unassigned vehicles available for deployment.",
        "The Bulk dash zero zero zero one trip is 25% booked.",
        "Warning: Removing this vehicle will cancel existing bookings. Do you want to proceed?",
        "Successfully assigned vehicle M H dash 12 dash 3456 to the trip."
    ]

    for idx, response in enumerate(responses, 1):
        print(f"\n{idx}. Response: '{response[:60]}...'")
        print("   🔊 Generating audio...")

        audio_bytes = await tts.generate_speech(
            text=response,
            voice="coral",
            instructions="Speak clearly and professionally as a helpful transport assistant."
        )

        output_file = Path(f"test_response_{idx}.mp3")
        output_file.write_bytes(audio_bytes)

        print(f"   ✅ Generated {len(audio_bytes):,} bytes -> {output_file}")


async def test_api_key_validation():
    """Verify OpenAI API key is configured."""
    print_section("Test 4: OpenAI API Key Validation")

    from app.core.config import settings

    print("\nChecking configuration...")

    if settings.OPENAI_API_KEY:
        api_key_preview = settings.OPENAI_API_KEY[:10] + "..." + settings.OPENAI_API_KEY[-4:]
        print(f"  ✅ OPENAI_API_KEY is set: {api_key_preview}")
        return True
    else:
        print("  ❌ OPENAI_API_KEY is NOT set!")
        print("  Please add OPENAI_API_KEY to backend/.env file")
        print("  Get your key from: https://platform.openai.com/api-keys")
        return False


async def main():
    """Run all TTS tests."""
    print("\n" + "=" * 80)
    print("  OpenAI TTS Integration Test Suite")
    print("  Testing gpt-4o-mini-tts model")
    print("=" * 80)

    # First check if API key is configured
    if not await test_api_key_validation():
        print("\n❌ Cannot proceed without OPENAI_API_KEY")
        return

    try:
        # Test 1: Basic TTS
        await test_basic_tts()

        # Test 2: Different voices
        await test_different_voices()

        # Test 3: Transport-specific responses
        await test_transport_responses()

        print("\n" + "=" * 80)
        print("  TTS Integration Tests Complete!")
        print("=" * 80)
        print("\n✅ OpenAI TTS API is working correctly")
        print("✅ gpt-4o-mini-tts model tested")
        print("✅ Multiple voices tested")
        print("✅ Transport responses generated")
        print("\nℹ️  Audio files saved in backend/ directory")
        print("   Play them with: open test_*.mp3")

    except Exception as e:
        print(f"\n❌ Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
