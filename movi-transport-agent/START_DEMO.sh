#!/bin/bash

# Movi Transport Agent - Demo Startup Script
# This script starts both backend and frontend for the demo

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║         Movi Transport Agent - Interview Demo Startup         ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run: python3.11 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

echo "✅ Using Python $(python3 --version)"
echo ""

# Check if backend is already running
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "✅ Backend already running on port 8000"
else
    echo "🚀 Starting backend server..."
    cd backend
    python3 -m uvicorn main:app --reload --port 8000 > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    cd ..
    sleep 3
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
        echo "✅ Backend started successfully (PID: $BACKEND_PID)"
    else
        echo "❌ Backend failed to start. Check backend.log"
        exit 1
    fi
fi

echo ""

# Check if frontend is already running
if lsof -Pi :7860 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Frontend already running on port 7860"
    echo "    Kill it with: kill \$(lsof -ti:7860)"
    exit 1
else
    echo "🚀 Starting Gradio frontend..."
    cd frontend
    python3 gradio_app.py
fi
