"""
Frontend components for Movi Transport Agent Gradio UI.
"""

from .data_fetcher import fetch_trips, fetch_routes, fetch_stops
from .dashboard import create_dashboard_tab
from .routes import create_routes_tab
from .chat_interface import create_chat_interface

__all__ = [
    'fetch_trips',
    'fetch_routes',
    'fetch_stops',
    'create_dashboard_tab',
    'create_routes_tab',
    'create_chat_interface'
]
