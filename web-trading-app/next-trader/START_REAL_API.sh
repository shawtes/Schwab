#!/bin/bash

echo "🚀 Starting Schwab Trading Platform with REAL API"
echo "=================================================="
echo ""

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
BACKEND_DIR="$PROJECT_ROOT/web-trading-app/server"
FRONTEND_DIR="$PROJECT_ROOT/web-trading-app/next-trader"

echo "📂 Project root: $PROJECT_ROOT"
echo "📂 Backend: $BACKEND_DIR"
echo "📂 Frontend: $FRONTEND_DIR"
echo ""

# Check if backend server directory exists
if [ ! -d "$BACKEND_DIR" ]; then
    echo "❌ Backend server directory not found at $BACKEND_DIR"
    exit 1
fi

# Check if frontend directory exists
if [ ! -d "$FRONTEND_DIR" ]; then
    echo "❌ Frontend directory not found at $FRONTEND_DIR"
    exit 1
fi

# Kill any existing processes on ports 3000 and 3001
echo "🔄 Cleaning up existing processes..."
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:3001 | xargs kill -9 2>/dev/null || true
sleep 1

# Start backend server in background
echo ""
echo "🟢 Starting Backend Server (Port 3001)..."
cd "$BACKEND_DIR"
npm run dev > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"

# Wait for backend to start
echo "   Waiting for backend to be ready..."
sleep 5

# Check if backend is running
if ! lsof -ti:3001 > /dev/null; then
    echo "❌ Backend failed to start. Check logs: tail -f /tmp/backend.log"
    kill $BACKEND_PID 2>/dev/null || true
    exit 1
fi

echo "   ✅ Backend ready on http://localhost:3001"

# Start frontend
echo ""
echo "🟢 Starting Frontend (Port 3000)..."
cd "$FRONTEND_DIR"
echo "   Frontend running on http://localhost:3000"
echo ""
echo "=================================================="
echo "✅ READY! Open http://localhost:3000 in your browser"
echo "📊 Using REAL Schwab API data"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=================================================="
echo ""

# Run frontend in foreground (so Ctrl+C stops everything)
npm run dev

# Cleanup on exit
trap "echo ''; echo '🛑 Stopping servers...'; kill $BACKEND_PID 2>/dev/null || true; exit" INT TERM


