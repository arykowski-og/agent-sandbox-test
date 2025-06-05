#!/bin/bash

# LangGraph Agent + Chat UI Startup Script
echo "🚀 Starting LangGraph Agent + Chat UI..."
echo "====================================="

# Check if virtual environment exists, create if not
VENV_DIR="./langgraph_agent/langgraph_env"
if [ ! -d "$VENV_DIR" ]; then
    echo "📦 Virtual environment not found. Creating it..."
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed. Please install Python 3.9 or higher."
        exit 1
    fi
    
    echo "✅ Python 3 found: $(python3 --version)"
    
    # Create virtual environment
    mkdir -p ./langgraph_agent
    python3 -m venv $VENV_DIR
    
    # Activate and install dependencies
    source $VENV_DIR/bin/activate
    echo "📋 Installing Python dependencies..."
    pip install -q -r requirements.txt
    echo "✅ Dependencies installed"
else
    echo "✅ Virtual environment found"
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create one with your OPENAI_API_KEY."
    echo "💡 You can copy env.example to .env and add your API key."
    exit 1
fi

# Check if agent-chat-ui exists
if [ ! -d "agent-chat-ui" ]; then
    echo "❌ agent-chat-ui directory not found. Please ensure it's in the project root."
    exit 1
fi

# Check if agent-chat-ui dependencies are installed
if [ ! -d "agent-chat-ui/node_modules" ]; then
    echo "📦 Installing Chat UI dependencies..."
    cd agent-chat-ui
    pnpm install
    cd ..
    echo "✅ Chat UI dependencies installed"
fi

# Function to kill existing processes
cleanup() {
    echo "🛑 Stopping servers..."
    pkill -f "langgraph dev" 2>/dev/null
    pkill -f "pnpm dev" 2>/dev/null
    pkill -f "npm run dev" 2>/dev/null
    sleep 2
    echo "✅ Servers stopped."
}

# Handle Ctrl+C gracefully
trap cleanup EXIT

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
cleanup

# Check if ports are available
if lsof -Pi :2024 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 2024 is in use. Trying to free it..."
    lsof -ti :2024 | xargs kill -9 2>/dev/null
    sleep 2
fi

if lsof -Pi :3000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 3000 is in use. Trying to free it..."
    lsof -ti :3000 | xargs kill -9 2>/dev/null
    sleep 2
fi

echo "🔄 Starting LangGraph server..."
# Start LangGraph server in background
source $VENV_DIR/bin/activate
(
    export PYTHONPATH="${PYTHONPATH}:$(pwd)"
    langgraph dev --port 2024 2>&1 | sed 's/^/[LangGraph] /' &
    echo $! > .langgraph_pid
) &

echo "⏳ Waiting for LangGraph server to start..."
sleep 8

# Check if LangGraph server is running
if ! curl -s http://localhost:2024/docs >/dev/null 2>&1; then
    echo "⚠️  LangGraph server may still be starting..."
else
    echo "✅ LangGraph server is running on http://localhost:2024"
fi

echo "🔄 Starting Chat UI..."
# Start Chat UI in background
cd agent-chat-ui
(
    pnpm dev 2>&1 | sed 's/^/[Chat UI] /' &
    echo $! > ../.chatui_pid
) &
cd ..

echo "⏳ Waiting for Chat UI to start..."
sleep 10

# Check if Chat UI is running
if ! curl -s http://localhost:3000 >/dev/null 2>&1; then
    echo "⚠️  Chat UI may still be starting..."
else
    echo "✅ Chat UI is running on http://localhost:3000"
fi

echo ""
echo "🎉 Both servers are running!"
echo "============================"
echo "📊 LangGraph API Server:"
echo "   🌐 URL: http://localhost:2024"
echo "   📚 API Docs: http://localhost:2024/docs"
echo "   🎨 Studio: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024"
echo ""
echo "💬 Agent Chat UI:"
echo "   🌐 URL: http://localhost:3000"
echo "   🧪 Test: Try asking 'What's the weather in Paris?'"
echo ""
echo "⚡ Quick Commands:"
echo "   • Stop servers: Ctrl+C or ./stop.sh"
echo "   • View logs: Check terminal output above"
echo ""
echo "🔍 Monitoring both servers... Press Ctrl+C to stop"

# Wait for both processes and show their status
while true; do
    sleep 30
    
    # Check LangGraph server
    if ! pgrep -f "langgraph dev" > /dev/null; then
        echo "❌ LangGraph server stopped unexpectedly!"
        break
    fi
    
    # Check Chat UI
    if ! pgrep -f "pnpm dev" > /dev/null; then
        echo "❌ Chat UI stopped unexpectedly!"
        break
    fi
    
    echo "✅ Both servers are running... ($(date))"
done

echo "🛑 One or more servers stopped. Cleaning up..." 