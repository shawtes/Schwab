#!/bin/bash

echo "🚀 Starting Schwab Pro Trading Platform..."
echo ""
echo "Starting WebSocket Server on port 4001..."

# Kill any existing processes on ports 3000 and 4001
lsof -ti:3000 | xargs kill -9 2>/dev/null
lsof -ti:4001 | xargs kill -9 2>/dev/null

# Start WebSocket server in background
npm run mock:ws &
WS_PID=$!

# Wait for WebSocket server to start
sleep 2

echo ""
echo "✅ WebSocket server started (PID: $WS_PID)"
echo ""
echo "Starting Next.js dev server on port 3000..."
echo ""

# Start Next.js dev server
npm run dev

# Cleanup on exit
trap "kill $WS_PID 2>/dev/null" EXIT


