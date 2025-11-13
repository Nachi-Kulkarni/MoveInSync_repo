#!/bin/bash

# Start script for Movi Transport Agent Gradio UI

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║       Movi Transport Agent - Gradio Frontend Startup          ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check if backend is running
echo "Checking if backend is running..."
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8000"
else
    echo "❌ Backend is NOT running!"
    echo ""
    echo "Please start the backend first:"
    echo "  cd ../backend"
    echo "  python -m uvicorn main:app --reload --port 8000"
    echo ""
    exit 1
fi

echo ""
echo "Installing dependencies (if needed)..."
pip install -q -r requirements.txt

echo ""
echo "Starting Gradio UI..."
echo ""
python gradio_app.py
