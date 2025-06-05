#!/bin/bash

# LangGraph Agent + Chat UI Stop Script
echo "🛑 Stopping LangGraph Agent + Chat UI servers..."
echo "==============================================="

# Kill LangGraph server
echo "🔄 Stopping LangGraph server..."
pkill -f "langgraph dev" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ LangGraph server stopped"
else
    echo "ℹ️  No LangGraph server was running"
fi

# Kill Chat UI server
echo "🔄 Stopping Chat UI server..."
pkill -f "pnpm dev" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Chat UI server stopped"
else
    echo "ℹ️  No Chat UI server was running"
fi

# Clean up any lingering processes on the ports
echo "🧹 Cleaning up ports..."
if lsof -Pi :2024 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔄 Freeing port 2024..."
    lsof -ti :2024 | xargs kill -9 2>/dev/null
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "🔄 Freeing port 3000..."
    lsof -ti :3000 | xargs kill -9 2>/dev/null
fi

# Clean up PID files
rm -f .langgraph_pid .chatui_pid 2>/dev/null

echo "✅ All servers stopped and ports freed"
echo "🚀 To start again, run: ./run.sh" 