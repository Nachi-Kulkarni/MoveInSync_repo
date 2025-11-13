"""
Movi Transport Agent - Gradio UI
Main application entry point with two-tab layout.
"""

import gradio as gr
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components import create_dashboard_tab, create_routes_tab


def create_app():
    """
    Create and configure the main Gradio application.

    Returns:
        Gradio Blocks app
    """
    # Custom theme
    theme = gr.themes.Soft(
        primary_hue="blue",
        secondary_hue="gray",
        neutral_hue="slate",
    )

    with gr.Blocks(
        theme=theme,
        title="Movi Transport Agent",
        css="""
        .gradio-container {
            max-width: 1400px !important;
        }
        /* Enhanced warning message styling */
        .warning-high {
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #c92a2a;
            margin: 10px 0;
        }
        .warning-medium {
            background: linear-gradient(135deg, #ffd93d 0%, #ffb700 100%);
            color: #1a1a1a;
            padding: 15px;
            border-radius: 10px;
            border-left: 5px solid #f59f00;
            margin: 10px 0;
        }
        /* Confirmation buttons styling */
        button[variant="primary"] {
            background: #28a745 !important;
            border-color: #28a745 !important;
        }
        button[variant="secondary"] {
            background: #dc3545 !important;
            border-color: #dc3545 !important;
        }
        /* Chat message styling */
        .chatbot .message {
            padding: 12px;
            border-radius: 8px;
        }
        /* Audio player styling */
        audio {
            width: 100%;
            max-width: 400px;
        }
        """
    ) as app:
        # Header
        gr.Markdown(
            """
            # 🚌 Movi Transport Agent
            ### Multimodal AI Assistant for MoveInSync Transport Management

            Navigate between **Bus Dashboard** and **Manage Routes** tabs below.
            """
        )

        # State to track current page context
        current_page = gr.State("busDashboard")

        # Create tabs
        with gr.Tabs() as tabs:
            # Tab 1: Bus Dashboard
            with gr.Tab("🚌 Bus Dashboard", id="dashboard") as dashboard_tab:
                dashboard_components = create_dashboard_tab()

                # Load initial data
                dashboard_tab.select(
                    fn=lambda: ("busDashboard", *dashboard_components["load_data_fn"]()),
                    inputs=[],
                    outputs=[current_page, dashboard_components["trips_dataframe"], dashboard_components["map_display"]]
                )

                # Refresh button handler
                dashboard_components["refresh_btn"].click(
                    fn=dashboard_components["refresh_fn"],
                    inputs=[],
                    outputs=[dashboard_components["trips_dataframe"], dashboard_components["map_display"]]
                )

            # Tab 2: Manage Routes
            with gr.Tab("🛣️ Manage Routes", id="routes") as routes_tab:
                routes_components = create_routes_tab()

                # Load initial data
                routes_tab.select(
                    fn=lambda: ("manageRoute", routes_components["load_data_fn"]()),
                    inputs=[],
                    outputs=[current_page, routes_components["routes_dataframe"]]
                )

                # Refresh button handler
                routes_components["refresh_btn"].click(
                    fn=routes_components["refresh_fn"],
                    inputs=[],
                    outputs=[routes_components["routes_dataframe"]]
                )

                # Filter handler
                routes_components["status_filter"].change(
                    fn=lambda status: routes_components["filter_fn"](routes_components["load_data_fn"](), status),
                    inputs=[routes_components["status_filter"]],
                    outputs=[routes_components["routes_dataframe"]]
                )

                # Create route button handler
                routes_components["create_btn"].click(
                    fn=routes_components["create_route_fn"],
                    inputs=[],
                    outputs=[routes_components["status_message"]]
                ).then(
                    lambda: gr.update(visible=True),
                    inputs=[],
                    outputs=[routes_components["status_message"]]
                )

        # Footer
        gr.Markdown(
            """
            ---
            **Movi Transport Agent** | Built with LangGraph, Claude Sonnet 4.5, and Gemini 2.5 Pro

            🎤 **Features:** Multimodal Input (Text, Voice, Image, Video) | 🔊 Text-to-Speech | ⚠️ Consequence-Aware Actions
            """
        )

    return app


def main():
    """
    Main entry point - launch the Gradio app.
    """
    # Get configuration from environment
    server_name = os.getenv("GRADIO_SERVER_NAME", "0.0.0.0")
    server_port = int(os.getenv("GRADIO_SERVER_PORT", "7860"))
    share = os.getenv("GRADIO_SHARE", "false").lower() == "true"

    # Create and launch app
    app = create_app()

    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║                  Movi Transport Agent - Gradio UI              ║
    ╚════════════════════════════════════════════════════════════════╝

    🚀 Starting Gradio server...
    📍 Server: http://{server_name}:{server_port}

    ⚠️  Make sure backend is running at: http://localhost:8000

    Press Ctrl+C to stop the server.
    """)

    app.launch(
        server_name=server_name,
        server_port=server_port,
        share=share,
        show_error=True,
        quiet=False
    )


if __name__ == "__main__":
    main()
