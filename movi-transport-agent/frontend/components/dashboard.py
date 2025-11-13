"""
Dashboard tab component for Gradio UI.
Displays trip list and map with stops.
"""

import gradio as gr
import pandas as pd
import folium
from typing import Tuple, Optional
from .data_fetcher import fetch_trips_sync, fetch_stops_sync


def create_map_html(stops_data: list) -> str:
    """
    Create an interactive map with stop markers using Folium.

    Args:
        stops_data: List of stop dictionaries with latitude, longitude, name

    Returns:
        HTML string of the rendered map
    """
    # Default center (Bangalore coordinates)
    center_lat = 12.9716
    center_lon = 77.5946

    # If we have stops, center on first stop
    if stops_data and len(stops_data) > 0:
        center_lat = stops_data[0].get('latitude', center_lat)
        center_lon = stops_data[0].get('longitude', center_lon)

    # Create map
    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=12,
        tiles='OpenStreetMap'
    )

    # Add markers for each stop
    for stop in stops_data:
        lat = stop.get('latitude')
        lon = stop.get('longitude')
        name = stop.get('name', 'Unknown Stop')

        if lat and lon:
            folium.Marker(
                location=[lat, lon],
                popup=name,
                tooltip=name,
                icon=folium.Icon(color='blue', icon='bus', prefix='fa')
            ).add_to(m)

    # Return HTML string
    return m._repr_html_()


def load_dashboard_data() -> Tuple[pd.DataFrame, str]:
    """
    Load dashboard data (trips and map).

    Returns:
        Tuple of (trips_dataframe, map_html)
    """
    try:
        # Fetch trips data
        trips_df = fetch_trips_sync()

        # Fetch stops for map
        stops_data = fetch_stops_sync()
        map_html = create_map_html(stops_data)

        return trips_df, map_html

    except Exception as e:
        print(f"Error loading dashboard data: {e}")
        # Return empty data on error
        empty_df = pd.DataFrame(columns=["Trip Name", "Booking %", "Live Status"])
        error_html = f"<div style='padding: 20px; text-align: center;'>Error loading map: {str(e)}</div>"
        return empty_df, error_html


def refresh_dashboard() -> Tuple[pd.DataFrame, str]:
    """
    Refresh dashboard data.

    Returns:
        Tuple of (updated_trips_dataframe, updated_map_html)
    """
    return load_dashboard_data()


def create_dashboard_tab() -> dict:
    """
    Create the dashboard tab with trip list and map.

    Returns:
        Dictionary of Gradio components
    """
    with gr.Column() as dashboard_col:
        gr.Markdown("## 🚌 Bus Dashboard")
        gr.Markdown("View all trips and stop locations")

        with gr.Row():
            # Left panel - Trip list
            with gr.Column(scale=1):
                gr.Markdown("### Daily Trips")
                trips_dataframe = gr.Dataframe(
                    headers=["Trip Name", "Booking %", "Live Status"],
                    datatype=["str", "str", "str"],
                    label="Trip List",
                    interactive=False,
                    wrap=True,
                    height=400
                )

                refresh_btn = gr.Button("🔄 Refresh Data", variant="secondary", size="sm")

            # Right panel - Map
            with gr.Column(scale=2):
                gr.Markdown("### Stop Locations")
                map_display = gr.HTML(
                    label="Map",
                    value="<div style='padding: 20px; text-align: center;'>Loading map...</div>"
                )

        # Chat interface placeholder
        gr.Markdown("---")
        gr.Markdown("### 💬 Movi Assistant")
        gr.Markdown("*Chat interface will be added in TICKET #9*")

    # Return components for external access
    return {
        "column": dashboard_col,
        "trips_dataframe": trips_dataframe,
        "map_display": map_display,
        "refresh_btn": refresh_btn,
        "load_data_fn": load_dashboard_data,
        "refresh_fn": refresh_dashboard
    }
