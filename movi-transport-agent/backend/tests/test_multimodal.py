"""
Test script for multimodal input processing.
Demonstrates text, image, audio, and video processing using Gemini 2.5.
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# Add the app directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from app.multimodal import (
    GeminiMultimodalProcessor,
    MultimodalInput,
    transcribe_audio,
    analyze_screenshot,
    analyze_video
)


async def test_text_only():
    """Test text-only input processing."""
    print("\n" + "="*60)
    print("TEST 1: Text-Only Input")
    print("="*60)

    processor = GeminiMultimodalProcessor()

    try:
        multimodal_input = MultimodalInput(
            text="How many vehicles are not assigned?",
            current_page="busDashboard"
        )

        result = await processor.process_multimodal_input(multimodal_input)

        print(f"Modality: {result['modality']}")
        print(f"Comprehension: {result['comprehension']}")
        print(f"Action Intent: {result['extracted_entities']['action_intent']}")
        print(f"Entities: {result['extracted_entities']}")

    finally:
        await processor.close()


async def test_image_url():
    """Test image processing with URL."""
    print("\n" + "="*60)
    print("TEST 2: Image URL Processing")
    print("="*60)

    processor = GeminiMultimodalProcessor()

    try:
        # Using a sample image URL (you can replace with your own)
        multimodal_input = MultimodalInput(
            text="What's in this image? Are there any UI elements visible?",
            image_file="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            current_page="busDashboard"
        )

        result = await processor.process_multimodal_input(multimodal_input)

        print(f"Modality: {result['modality']}")
        print(f"Comprehension: {result['comprehension']}")
        print(f"Entities: {result['extracted_entities']}")

    finally:
        await processor.close()


async def test_screenshot_analysis():
    """Test analyzing a transport dashboard screenshot."""
    print("\n" + "="*60)
    print("TEST 3: Screenshot Analysis (if screenshot file exists)")
    print("="*60)

    # Example: If you have a screenshot file
    screenshot_path = Path("demo/screenshots/dashboard.png")

    if not screenshot_path.exists():
        print(f"Screenshot not found at: {screenshot_path}")
        print("Skipping this test. Place a screenshot at the path above to test.")
        return

    result = await analyze_screenshot(
        image_file=screenshot_path,
        user_query="Remove the vehicle from this trip",
        current_page="busDashboard"
    )

    print(f"Modality: {result['modality']}")
    print(f"Comprehension: {result['comprehension']}")
    print(f"Action Intent: {result['extracted_entities']['action_intent']}")
    print(f"Trip IDs: {result['extracted_entities'].get('trip_ids', [])}")
    print(f"Vehicle IDs: {result['extracted_entities'].get('vehicle_ids', [])}")


async def test_mixed_input():
    """Test mixed text + image input."""
    print("\n" + "="*60)
    print("TEST 4: Mixed Input (Text + Image)")
    print("="*60)

    processor = GeminiMultimodalProcessor()

    try:
        multimodal_input = MultimodalInput(
            text="List all trips visible in this screenshot",
            image_file="https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
            current_page="busDashboard"
        )

        result = await processor.process_multimodal_input(multimodal_input)

        print(f"Modality: {result['modality']}")
        print(f"Comprehension: {result['comprehension']}")
        print(f"Confidence: {result.get('confidence', 'N/A')}")

    finally:
        await processor.close()


async def test_comprehension_output():
    """Test the structured output format."""
    print("\n" + "="*60)
    print("TEST 5: Structured Output Validation")
    print("="*60)

    processor = GeminiMultimodalProcessor()

    try:
        multimodal_input = MultimodalInput(
            text="Remove vehicle MH-12-3456 from Bulk - 00:01 trip",
            current_page="busDashboard"
        )

        result = await processor.process_multimodal_input(multimodal_input)

        # Validate output structure
        required_keys = ["original_text", "modality", "comprehension", "extracted_entities"]
        for key in required_keys:
            assert key in result, f"Missing required key: {key}"

        # Validate extracted_entities structure
        entity_keys = ["trip_ids", "vehicle_ids", "action_intent"]
        for key in entity_keys:
            assert key in result["extracted_entities"], f"Missing entity key: {key}"

        print("✓ Output structure validation passed")
        print(f"\nOutput:")
        print(f"  Original Text: {result['original_text']}")
        print(f"  Modality: {result['modality']}")
        print(f"  Comprehension: {result['comprehension']}")
        print(f"  Action Intent: {result['extracted_entities']['action_intent']}")
        print(f"  Trip IDs: {result['extracted_entities']['trip_ids']}")
        print(f"  Vehicle IDs: {result['extracted_entities']['vehicle_ids']}")

    finally:
        await processor.close()


async def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("MULTIMODAL INPUT PROCESSOR - TEST SUITE")
    print("Testing TICKET #4 Implementation")
    print("="*60)

    try:
        # Test 1: Text only
        await test_text_only()

        # Test 2: Image URL
        await test_image_url()

        # Test 3: Screenshot analysis (if file exists)
        await test_screenshot_analysis()

        # Test 4: Mixed input
        await test_mixed_input()

        # Test 5: Output structure validation
        await test_comprehension_output()

        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)

    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
