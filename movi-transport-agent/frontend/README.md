# Movi Transport Agent - Gradio Frontend

## Overview

This is the Gradio-based frontend for the Movi Transport Agent. It provides a user-friendly interface with two main tabs:

1. **🚌 Bus Dashboard** - View daily trips and stop locations on a map
2. **🛣️ Manage Routes** - View and manage routes with filtering capabilities

## Features

- **Real-time Data Display**: Fetches live data from backend API
- **Interactive Map**: Shows stop locations using Folium
- **Route Management**: Filter and view routes by status
- **Responsive Layout**: Clean, modern UI with Gradio Soft theme
- **Auto-refresh**: Manual refresh buttons for data updates

## Setup

### Prerequisites

- Python 3.10+
- Backend server running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
cd frontend
pip install -r requirements.txt
```

2. Set environment variables (optional):
```bash
export BACKEND_URL=http://localhost:8000
export GRADIO_SERVER_PORT=7860
export GRADIO_SHARE=false
```

### Running the App

```bash
python gradio_app.py
```

The app will be available at: `http://localhost:7860`

## Project Structure

```
frontend/
├── gradio_app.py           # Main application entry point
├── requirements.txt        # Python dependencies
├── components/
│   ├── __init__.py        # Package initialization
│   ├── data_fetcher.py    # API integration utilities
│   ├── dashboard.py       # Dashboard tab component
│   └── routes.py          # Routes tab component
└── assets/                # Static assets (images, etc.)
```

## Components

### Dashboard Tab
- **Trip List**: Displays all daily trips with booking percentage and status
- **Map**: Interactive map showing stop locations
- **Refresh Button**: Manually refresh trip and map data

### Routes Tab
- **Route Table**: Displays all routes with detailed information
- **Status Filter**: Filter routes by status (All/Active/Deactivated)
- **Create Button**: Placeholder for route creation (coming in TICKET #9)
- **Refresh Button**: Manually refresh route data

## API Integration

The frontend communicates with the backend API endpoints:

- `GET /api/v1/trips` - Fetch all trips
- `GET /api/v1/routes` - Fetch all routes
- `GET /api/v1/stops` - Fetch all stops

## Next Steps (TICKET #9)

- Add Movi chat interface to both tabs
- Implement multimodal input (text, audio, image, video)
- Add Text-to-Speech (TTS) output
- Add confirmation dialog for high-risk actions

## Troubleshooting

**Problem**: "Error fetching trips/routes/stops"
- **Solution**: Make sure the backend server is running on `http://localhost:8000`

**Problem**: Map not loading
- **Solution**: Check that stops data is available in the database

**Problem**: Port 7860 already in use
- **Solution**: Set `GRADIO_SERVER_PORT` to a different port or kill the existing process

## License

Part of the Movi Transport Agent project.
