"""
Manage Routes tab component for Gradio UI.
Displays route table with filtering and actions.
"""

import gradio as gr
import pandas as pd
from .data_fetcher import fetch_routes_sync, fetch_stops_sync


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


def load_stops_data() -> pd.DataFrame:
    """
    Load stops data from backend.

    Returns:
        DataFrame with stop information
    """
    try:
        stops_list = fetch_stops_sync()

        # Transform to DataFrame
        stops_data = []
        for stop in stops_list:
            stops_data.append({
                "Stop ID": stop.get("stop_id", "N/A"),
                "Name": stop.get("name", "Unknown"),
                "Latitude": f"{stop.get('latitude', 0):.4f}",
                "Longitude": f"{stop.get('longitude', 0):.4f}"
            })

        return pd.DataFrame(stops_data)

    except Exception as e:
        print(f"Error loading stops data: {e}")
        return pd.DataFrame(columns=["Stop ID", "Name", "Latitude", "Longitude"])


def refresh_routes() -> pd.DataFrame:
    """
    Refresh routes data.

    Returns:
        Updated routes DataFrame
    """
    return load_routes_data()


def refresh_stops() -> pd.DataFrame:
    """
    Refresh stops data.

    Returns:
        Updated stops DataFrame
    """
    return load_stops_data()


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
        Helpful message directing users to chat interface
    """
    message = """✨ To create a route, use the Movi chat interface below!

Example commands:
• "Create a route using Path-1 at 08:00 AM for LOGIN"
• "Add a new route on Path-2 at 19:45 for LOGOUT"
• "Create route for Path-3 at 7:30 AM going to office"

💬 Just scroll down and type your request in the chat!"""

    return message


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

                # Stops table (to view created stops)
                gr.Markdown("### 📍 Stops")
                stops_dataframe = gr.Dataframe(
                    headers=["Stop ID", "Name", "Latitude", "Longitude"],
                    datatype=["str", "str", "str", "str"],
                    label="Stop List",
                    interactive=False,
                    wrap=True
                )

                # Status message (for create route button)
                status_message = gr.Markdown(
                    value="",
                    visible=False
                )

        # Chat interface
        gr.Markdown("---")
        from .chat_interface import create_chat_interface
        chat_components = create_chat_interface("manageRoute")

    # Return components for external access
    return {
        "column": routes_col,
        "routes_dataframe": routes_dataframe,
        "stops_dataframe": stops_dataframe,
        "status_filter": status_filter,
        "refresh_btn": refresh_btn,
        "create_btn": create_btn,
        "status_message": status_message,
        "load_data_fn": load_routes_data,
        "load_stops_fn": load_stops_data,
        "refresh_fn": refresh_routes,
        "refresh_stops_fn": refresh_stops,
        "filter_fn": filter_routes,
        "create_route_fn": handle_create_route,
        "chat_components": chat_components
    }
