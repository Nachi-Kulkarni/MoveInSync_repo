"""
Manage Routes tab component for Gradio UI.
Displays route table with filtering and actions.
"""

import gradio as gr
import pandas as pd
from typing import Tuple
from .data_fetcher import fetch_routes_sync


def load_routes_data() -> pd.DataFrame:
    """
    Load routes data from backend.

    Returns:
        DataFrame with route information
    """
    try:
        routes_df = fetch_routes_sync()
        return routes_df

    except Exception as e:
        print(f"Error loading routes data: {e}")
        # Return empty DataFrame on error
        return pd.DataFrame(columns=[
            "Route ID", "Route Name", "Direction", "Shift Time",
            "Start Point", "End Point", "Status"
        ])


def refresh_routes() -> pd.DataFrame:
    """
    Refresh routes data.

    Returns:
        Updated routes DataFrame
    """
    return load_routes_data()


def filter_routes(df: pd.DataFrame, status_filter: str) -> pd.DataFrame:
    """
    Filter routes by status.

    Args:
        df: Routes DataFrame
        status_filter: Status to filter by ("All", "Active", "Deactivated")

    Returns:
        Filtered DataFrame
    """
    if df.empty or status_filter == "All":
        return df

    # Filter by status
    if status_filter in ["Active", "Deactivated"]:
        return df[df["Status"].str.lower() == status_filter.lower()]

    return df


def handle_create_route() -> str:
    """
    Handle create route button click.

    Returns:
        Message about route creation
    """
    return "Route creation form will be available in TICKET #9 via Movi chat interface"


def create_routes_tab() -> dict:
    """
    Create the Manage Routes tab with route table.

    Returns:
        Dictionary of Gradio components
    """
    with gr.Column() as routes_col:
        gr.Markdown("## 🛣️ Manage Routes")
        gr.Markdown("View and manage all routes")

        with gr.Row():
            with gr.Column(scale=3):
                # Filter controls
                with gr.Row():
                    status_filter = gr.Dropdown(
                        choices=["All", "Active", "Deactivated"],
                        value="All",
                        label="Filter by Status",
                        scale=2
                    )
                    refresh_btn = gr.Button("🔄 Refresh", variant="secondary", scale=1)
                    create_btn = gr.Button("➕ Create Route", variant="primary", scale=1)

                # Route table
                routes_dataframe = gr.Dataframe(
                    headers=[
                        "Route ID", "Route Name", "Direction", "Shift Time",
                        "Start Point", "End Point", "Status"
                    ],
                    datatype=["str", "str", "str", "str", "str", "str", "str"],
                    label="Route List",
                    interactive=False,
                    wrap=True
                )

                # Status message
                status_message = gr.Textbox(
                    label="Status",
                    interactive=False,
                    visible=False
                )

        # Chat interface placeholder
        gr.Markdown("---")
        gr.Markdown("### 💬 Movi Assistant")
        gr.Markdown("*Chat interface will be added in TICKET #9*")

    # Return components for external access
    return {
        "column": routes_col,
        "routes_dataframe": routes_dataframe,
        "status_filter": status_filter,
        "refresh_btn": refresh_btn,
        "create_btn": create_btn,
        "status_message": status_message,
        "load_data_fn": load_routes_data,
        "refresh_fn": refresh_routes,
        "filter_fn": filter_routes,
        "create_route_fn": handle_create_route
    }
