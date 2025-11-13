"""
Chat interface component for Movi Assistant.
Supports text, voice, image, and video input with TTS output.
"""

import gradio as gr
import uuid
import tempfile
import os
import sys
from typing import List, Tuple, Optional, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils import send_message_to_agent, send_confirmation, generate_tts


def create_chat_interface(page_name: str) -> dict:
    """
    Create chat interface with multimodal inputs and TTS output.

    Args:
        page_name: Page context ("busDashboard" or "manageRoute")

    Returns:
        Dictionary of Gradio components for the chat interface
    """

    # Session state
    session_id_state = gr.State(lambda: str(uuid.uuid4()))
    pending_confirmation_state = gr.State(None)  # Stores pending confirmation data
    tts_enabled_state = gr.State(True)  # TTS enabled by default

    with gr.Column() as chat_col:
        gr.Markdown("### 💬 Movi Assistant")
        gr.Markdown("Ask me anything about trips, routes, vehicles, and more!")

        # Chat history display
        chatbot = gr.Chatbot(
            label="Chat with Movi",
            height=400,
            bubble_full_width=False,
            avatar_images=(None, "🤖"),
            type="tuples"  # Using tuples format for compatibility
        )

        # Text input row
        with gr.Row():
            msg_input = gr.Textbox(
                placeholder="Ask Movi anything... (e.g., 'How many unassigned vehicles?')",
                show_label=False,
                scale=4,
                container=False
            )
            send_btn = gr.Button("Send", variant="primary", scale=1)

        # Multimodal inputs (collapsible)
        with gr.Accordion("🎤 Multimodal Inputs", open=False):
            with gr.Row():
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="filepath",
                    label="Voice Input",
                    show_label=True
                )

            with gr.Row():
                image_input = gr.Image(
                    type="filepath",
                    label="Image Upload (e.g., screenshot)",
                    show_label=True
                )

            with gr.Row():
                video_input = gr.Video(
                    label="Video Upload",
                    show_label=True
                )

        # TTS controls
        with gr.Row():
            tts_enabled = gr.Checkbox(
                label="🔊 Enable Voice Output",
                value=True,
                scale=2
            )
            clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary", scale=1)

        # Hidden audio player for TTS (auto-play)
        tts_audio = gr.Audio(
            visible=True,
            autoplay=True,
            label="Movi's Voice",
            show_label=False
        )

        # Confirmation buttons (hidden by default)
        with gr.Row(visible=False) as confirmation_row:
            with gr.Column():
                confirmation_message = gr.Markdown("")
                with gr.Row():
                    confirm_yes = gr.Button("✅ Yes, Proceed", variant="primary")
                    confirm_no = gr.Button("❌ No, Cancel", variant="secondary")

    # Handler functions
    def handle_message(
        user_input: str,
        history: List[Tuple[str, str]],
        session_id: str,
        audio: Optional[str],
        image: Optional[str],
        video: Optional[str],
        tts_on: bool,
        pending_confirmation: Optional[Dict]
    ) -> Tuple[List[Tuple[str, str]], str, Optional[str], Dict, Dict, Optional[str]]:
        """
        Handle user message and get agent response.

        Returns:
            Tuple of (updated_history, cleared_input, audio_output, confirmation_row_update, pending_confirmation, error)
        """
        # Don't process empty messages
        if not user_input.strip() and not audio and not image and not video:
            return history, "", None, gr.update(), None, gr.update(visible=False)

        # Check if user is responding to pending confirmation with text
        if pending_confirmation and user_input.strip().lower() in ['yes', 'y', 'confirm', 'proceed']:
            # Add user's confirmation to history
            history = history + [[user_input, None]]
            # Treat as confirmation YES
            hist, conf_row, pend, audio, conf_msg = handle_confirmation_yes(history, pending_confirmation, tts_on)
            return (hist, "", audio, gr.update(), pend, conf_row)
        elif pending_confirmation and user_input.strip().lower() in ['no', 'n', 'cancel', 'abort']:
            # Add user's cancellation to history
            history = history + [[user_input, None]]
            # Treat as confirmation NO
            hist, conf_row, pend = handle_confirmation_no(history, pending_confirmation)
            return (hist, "", None, gr.update(), pend, conf_row)

        # Add user message to history
        history = history + [[user_input, None]]

        # Send to backend
        response, error = send_message_to_agent(
            user_input=user_input,
            session_id=session_id,
            current_page=page_name,
            audio_file=audio,
            image_file=image,
            video_file=video
        )

        if error:
            # Show error in chat
            history[-1][1] = f"❌ Error: {error}"
            return history, "", None, "", None, gr.update(visible=False)

        # Check if confirmation is required
        if response.get("requires_confirmation", False):
            confirmation_msg = response.get("confirmation_message", "Please confirm this action.")
            ui_action = response.get("ui_action") or {}
            risk_level = ui_action.get("risk_level", "medium")

            # Get consequence details from metadata if available
            metadata = response.get("metadata") or {}
            consequences = metadata.get("consequences", [])
            affected_count = metadata.get("affected_count", 0)

            # Format consequences as bullet points
            consequence_bullets = ""
            if consequences:
                consequence_bullets = "\n".join([f"• {c}" for c in consequences])
            elif "will cancel" in confirmation_msg.lower() or "booking" in confirmation_msg.lower():
                # Extract key consequences from message
                consequence_bullets = "• This action will affect bookings\n• Trip-sheet generation may be impacted"

            # Add affected count if available
            if affected_count > 0:
                consequence_bullets += f"\n• **Affects {affected_count} employees**"

            # Format confirmation message with enhanced warning styling
            risk_emoji = "🚨" if risk_level == "high" else "⚠️"
            formatted_msg = f"""
{risk_emoji} **WARNING: High-Risk Action Detected**

---

{confirmation_msg}

**Consequences:**
{consequence_bullets if consequence_bullets else "• This action may have significant consequences"}

---

**⚡ Do you want to proceed?**
            """

            # Store pending confirmation data
            pending_data = {
                "user_input": user_input,
                "session_id": session_id,
                "response": response
            }

            # Show confirmation warning in chat
            history[-1][1] = formatted_msg

            return (
                history,
                "",
                None,
                gr.update(value=formatted_msg),  # Update confirmation message
                pending_data,
                gr.update(visible=True)  # Make confirmation row with buttons visible
            )

        # Check for errors and provide the best error message
        if response.get("error") and not response.get("execution_success", True):
            # Use the error field if it's more specific than the response
            error_msg = response.get("error", "Operation failed")
            response_msg = response.get("response", "")

            # Show the more specific/technical error if it differs from the response
            if error_msg != response_msg and len(error_msg) > len(response_msg):
                agent_response = f"❌ {error_msg}"
            else:
                agent_response = f"❌ {response_msg}"
        else:
            # Normal response
            # Use the actual response from the backend
            agent_response = response.get("response", "I'm sorry, I couldn't process that request.")

        history[-1][1] = agent_response

        # Generate TTS if enabled
        audio_output = None
        if tts_on and agent_response:
            audio_bytes, tts_error = generate_tts(agent_response)
            if audio_bytes and not tts_error:
                # Save to temporary file for Gradio
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(audio_bytes)
                    audio_output = tmp.name

        return history, "", audio_output, "", None, gr.update(visible=False)

    def handle_confirmation_yes(
        history: List[Tuple[str, str]],
        pending_data: Optional[Dict],
        tts_on: bool
    ) -> Tuple[List[Tuple[str, str]], Dict, Dict, Optional[str], Optional[str]]:
        """Handle user confirming the action."""
        if not pending_data:
            return history, gr.update(visible=False), None, None, ""

        # Send confirmation to backend
        response, error = send_confirmation(
            session_id=pending_data["session_id"],
            confirmed=True,
            user_input=pending_data["user_input"],
            current_page=page_name
        )

        if error:
            # Use the backend's response if available, otherwise show error
            backend_response = response.get("response", f"Error: {error}")
            # If execution failed and there's a specific error, show that instead
            if response.get("error") and not response.get("execution_success", True):
                backend_response = f"❌ {response.get('error', error)}"
            history = history + [["[Confirmation]", backend_response]]
            return history, gr.update(visible=False), None, None, ""

        # Add agent response
        agent_response = response.get("response", "Action completed.")
        history = history + [["[Confirmed]", agent_response]]

        # Generate TTS if enabled
        audio_output = None
        if tts_on and agent_response:
            audio_bytes, tts_error = generate_tts(agent_response)
            if audio_bytes and not tts_error:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
                    tmp.write(audio_bytes)
                    audio_output = tmp.name

        return history, gr.update(visible=False), None, audio_output, ""

    def handle_confirmation_no(
        history: List[Tuple[str, str]],
        pending_data: Optional[Dict]
    ) -> Tuple[List[Tuple[str, str]], Dict, Optional[str]]:
        """Handle user cancelling the action."""
        if not pending_data:
            return history, gr.update(visible=False), None

        # Send cancellation to backend
        response, error = send_confirmation(
            session_id=pending_data["session_id"],
            confirmed=False,
            user_input=pending_data["user_input"],
            current_page=page_name
        )

        if error:
            # Use the most informative error message
            if response.get("error"):
                agent_response = f"❌ {response.get('error', error)}"
            else:
                agent_response = f"Error: {error}"
        else:
            agent_response = response.get("response", "Action cancelled.")
        history = history + [["[Cancelled]", agent_response]]

        return history, gr.update(visible=False), None

    def clear_chat():
        """Clear chat history and reset session."""
        return [], str(uuid.uuid4()), None, gr.update(visible=False), None

    # Wire up event handlers
    msg_submit = msg_input.submit(
        fn=handle_message,
        inputs=[msg_input, chatbot, session_id_state, audio_input, image_input, video_input, tts_enabled, pending_confirmation_state],
        outputs=[chatbot, msg_input, tts_audio, confirmation_message, pending_confirmation_state, confirmation_row]
    )

    send_btn.click(
        fn=handle_message,
        inputs=[msg_input, chatbot, session_id_state, audio_input, image_input, video_input, tts_enabled, pending_confirmation_state],
        outputs=[chatbot, msg_input, tts_audio, confirmation_message, pending_confirmation_state, confirmation_row]
    )

    confirm_yes.click(
        fn=handle_confirmation_yes,
        inputs=[chatbot, pending_confirmation_state, tts_enabled],
        outputs=[chatbot, confirmation_row, pending_confirmation_state, tts_audio, confirmation_message]
    )

    confirm_no.click(
        fn=handle_confirmation_no,
        inputs=[chatbot, pending_confirmation_state],
        outputs=[chatbot, confirmation_row, pending_confirmation_state]
    )

    clear_btn.click(
        fn=clear_chat,
        inputs=[],
        outputs=[chatbot, session_id_state, tts_audio, confirmation_row, pending_confirmation_state]
    )

    # Update TTS enabled state
    tts_enabled.change(
        fn=lambda x: x,
        inputs=[tts_enabled],
        outputs=[tts_enabled_state]
    )

    # Return components for external access
    return {
        "column": chat_col,
        "chatbot": chatbot,
        "msg_input": msg_input,
        "send_btn": send_btn,
        "audio_input": audio_input,
        "image_input": image_input,
        "video_input": video_input,
        "tts_enabled": tts_enabled,
        "tts_audio": tts_audio,
        "confirmation_row": confirmation_row,
        "confirmation_message": confirmation_message,
        "confirm_yes": confirm_yes,
        "confirm_no": confirm_no,
        "clear_btn": clear_btn,
        "session_id_state": session_id_state,
        "pending_confirmation_state": pending_confirmation_state
    }
