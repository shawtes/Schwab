#!/bin/bash

# Start Schwab Real-Time Streaming Server and Trading App

echo "🚀 Starting Schwab Real-Time Streaming Trading Platform..."
echo ""

# Check if conda environment exists
if ! conda env list | grep -q schwabdev; then
    echo "❌ schwabdev conda environment not found!"
    echo "Please create it first: conda create -n schwabdev python=3.11"
    exit 1
fi

# Activate conda environment
echo "📦 Activating schwabdev environment..."
eval "$(conda shell.bash hook)"
conda activate schwabdev

# Check if websockets is installed
if ! python -c "import websockets" 2>/dev/null; then
    echo "📦 Installing websockets..."
    pip install websockets python-dotenv
fi

# Start the Schwab streaming server in the background
echo "🌐 Starting Schwab WebSocket Streaming Server..."
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app
python schwab_stream_server.py &
STREAM_PID=$!

# Wait for streaming server to initialize
sleep 3

# Start the Next.js frontend
echo ""
echo "🎨 Starting Next.js Frontend..."
cd /Users/sineshawmesfintesfaye/Schwabdev/web-trading-app/next-trader
npm run dev &
NEXTJS_PID=$!

echo ""
echo "✅ All services started!"
echo ""
echo "🌐 Schwab Streaming Server: ws://localhost:8765"
echo "🎨 Trading Interface: http://localhost:3000"
echo "📊 Backend API: http://localhost:3001"
echo ""
echo "Press Ctrl+C to stop all services..."
echo ""

# Wait for Ctrl+C
trap "echo ''; echo '🛑 Stopping services...'; kill $STREAM_PID $NEXTJS_PID 2>/dev/null; exit" INT
wait


