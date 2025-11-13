#!/bin/bash

# Movi Transport Agent - Demo Stop Script

echo "🛑 Stopping Movi Transport Agent demo..."

# Stop frontend (port 7860)
if lsof -ti:7860 >/dev/null 2>&1; then
    echo "Stopping frontend (port 7860)..."
    kill $(lsof -ti:7860) 2>/dev/null
    echo "✅ Frontend stopped"
else
    echo "ℹ️  Frontend not running"
fi

# Stop backend (port 8000)
if lsof -ti:8000 >/dev/null 2>&1; then
    echo "Stopping backend (port 8000)..."
    kill $(lsof -ti:8000) 2>/dev/null
    echo "✅ Backend stopped"
else
    echo "ℹ️  Backend not running"
fi

# Also check for process by PID file
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID 2>/dev/null
        echo "✅ Backend process $BACKEND_PID stopped"
    fi
    rm backend.pid
fi

echo "✅ All services stopped"
