# LangGraph Agent Local Deployment

This project provides two ways to run your LangGraph agent:

1. **🚀 Integrated Setup (Recommended)**: LangGraph server + Beautiful Chat UI
2. **⚡ Standalone Mode**: Command-line interface only

## 🚀 **One-Command Setup**

The simplest way to get everything running:

```bash
# That's it! This handles setup AND starts both servers
./run.sh
```

Then open http://localhost:3000 for the Chat UI!

*The script automatically handles:*
- ✅ Virtual environment creation
- ✅ Python dependency installation  
- ✅ Chat UI dependency installation
- ✅ Starting both servers

## 📋 What You Get

### **Integrated Setup** (`./run.sh`)
- **LangGraph API Server** (http://localhost:2024) - Your agent accessible via API
- **Beautiful Chat UI** (http://localhost:3000) - Modern web interface 
- **Memory & Persistence** - Conversations are remembered
- **Auto-Setup** - Dependencies installed automatically
- **Real-time Monitoring** - Status updates every 30 seconds
- **Graceful Shutdown** - Ctrl+C stops both servers cleanly

### **Standalone Mode** (`python agent.py`)
- **Command-line Interface** - Terminal-based chat
- **Single Process** - Just the agent, no web UI
- **Development/Testing** - Good for debugging

## 🛠 **Available Scripts**

| Script | Purpose | What it does |
|--------|---------|--------------|
| `./run.sh` | **🎯 Main Command** | Auto-setup + start both servers |
| `./stop.sh` | **Stop Servers** | Clean shutdown of all processes |
| `python agent.py` | **Standalone Mode** | Terminal chat (legacy) |

## 🎯 **Super Simple Workflow**

**First time:**
```bash
# 1. Add your OpenAI API key
cp env.example .env
# Edit .env and add your OPENAI_API_KEY

# 2. Start everything
./run.sh
```

**Every time after:**
```bash
./run.sh          # Just this!
# Open http://localhost:3000 in browser
# When done: Ctrl+C
```

## 🔧 **Prerequisites**

The only things you need installed:

1. **Python 3.9+** - Check with `python3 --version`
2. **Node.js + pnpm** - For the Chat UI (usually pre-installed)
3. **OpenAI API Key** - Add to `.env` file

Everything else is handled automatically!

## 🔧 **Configuration**

### Main Environment File (`.env`)
```bash
OPENAI_API_KEY=your_openai_api_key_here

# Persistence Configuration
PERSISTENCE_TYPE=sqlite  # Options: memory, sqlite, postgres
DATABASE_URL=postgresql://username:password@localhost:5432/dbname  # For postgres only
SQLITE_DB_PATH=chat_history.db  # Custom SQLite file path (optional)
```

### Chat UI Configuration (`agent-chat-ui/.env`)
```bash
NEXT_PUBLIC_API_URL=http://localhost:2024
NEXT_PUBLIC_ASSISTANT_ID=agent
```

## 🧠 **Enhanced Persistence & Memory**

This project now includes comprehensive persistence and memory capabilities:

### **🔄 Thread Persistence**
- **Conversation History**: All messages are saved and restored across sessions
- **Multiple Threads**: Create separate conversation threads with unique IDs
- **Cross-Session**: Conversations persist even after restarting the server

### **💾 Storage Options**
| Type | Use Case | Persistence | Performance |
|------|----------|-------------|-------------|
| **Memory** | Development/Testing | ❌ Lost on restart | ⚡ Fastest |
| **SQLite** | Production (Single User) | ✅ File-based | 🚀 Fast |
| **PostgreSQL** | Production (Multi-User) | ✅ Database | 🏢 Scalable |

### **🎯 Memory Store Features**
- **Cross-Thread Memory**: Remember user preferences across different conversations
- **Semantic Search**: Find relevant memories using natural language queries
- **User Profiles**: Maintain persistent user preferences and context
- **Smart Retrieval**: Automatically recall relevant information during conversations

### **📝 How It Works**

1. **Within Thread**: 
   ```
   User: "My name is Alice and I love hiking"
   AI: "Nice to meet you Alice! Hiking is great exercise..."
   User: "What do you remember about me?"
   AI: "You told me your name is Alice and you love hiking!"
   ```

2. **Across Threads**: 
   ```
   Thread 1: User mentions loving pizza
   Thread 2: AI can reference pizza preference from previous conversation
   ```

3. **Memory Storage**:
   ```python
   # Automatically saves important user information
   agent.save_memory("user_123", "food_pref", {
       "memory": "User loves Italian food, especially pasta",
       "context": "Mentioned during dining discussion"
   })
   ```

### **🛠 Setting Up Persistence**

**Quick Start (SQLite - Recommended)**:
```bash
# Already configured by default!
./run.sh
# Chat history automatically saved to chat_history.db
```

**PostgreSQL Setup**:
```bash
# 1. Install PostgreSQL dependencies
pip install langgraph-checkpoint-postgres

# 2. Configure environment
echo "PERSISTENCE_TYPE=postgres" >> .env
echo "DATABASE_URL=postgresql://user:pass@localhost/dbname" >> .env

# 3. Start
./run.sh
```

**Memory-Only (Development)**:
```bash
echo "PERSISTENCE_TYPE=memory" >> .env
./run.sh
```

## 🎨 **Architecture**

```
┌─────────────────┐    HTTP/API    ┌──────────────────┐
│   Chat UI       │ ◄────────────► │ LangGraph Server │
│ (localhost:3000)│                │ (localhost:2024) │
│                 │                │                  │
│ • Next.js UI    │                │ • Your Agent     │
│ • Beautiful UX  │                │ • Weather Tool   │
│ • Real-time     │                │ • Memory         │
└─────────────────┘                └──────────────────┘
```

## 🧪 **Testing Your Agent**

Once running (`./run.sh`), try these in the Chat UI:

- **Weather Tool**: "What's the weather in Paris?"
- **General Chat**: "Hello, how are you?"
- **Capabilities**: "What tools do you have?"

## 🔌 **MCP Servers**

This project includes Model Context Protocol (MCP) servers for integrating with external APIs:

### **OpenGov FIN GraphQL MCP Server**
A GraphQL-based MCP server for OpenGov Financial Management System, inspired by [mcp-graphql](https://github.com/blurrah/mcp-graphql).

**Features:**
- 🔍 **Schema Introspection**: Automatically discover available GraphQL operations
- 📊 **Financial Data Access**: Query budgets, expenditures, revenues, and accounts
- 🔒 **JWT Authentication**: Secure Bearer token authentication
- 🛡️ **Mutation Control**: Mutations disabled by default for security
- 📝 **SDL Formatting**: Human-readable schema documentation

**Configuration:**
```bash
# Add to your .env file
OG_FIN_GRAPHQL_ENDPOINT=https://opengovdemo.fms.opengov.com/oci/graphql
OG_FIN_BEARER_TOKEN=your_jwt_token_here
OG_FIN_ALLOW_MUTATIONS=false  # Set to true to enable mutations
```

**Available Tools:**
- `introspect_schema()` - Discover available GraphQL operations and types
- `query_graphql(query, variables)` - Execute GraphQL queries
- `get_schema_types()` - Get simplified list of available types
- `get_query_operations()` - List all available query operations
- `get_mutation_operations()` - List all available mutation operations

**Testing:**
```bash
# Test the MCP server
python test_fin_mcp.py
```

**Usage Example:**
```python
# Basic connectivity test
await query_graphql("{ __typename }")

# Query financial data (example)
await query_graphql("""
  query GetBudgets {
    budgets {
      id
      name
      totalAmount
      fiscalYear
    }
  }
""")
```

### **Other MCP Servers**
- `opengov_plc_mcp_server.py` - OpenGov Permitting & Licensing API
- `opengov_open_data_mcp_server.py` - CKAN Open Data API

## 🔧 **Development**

### Adding New Tools
1. Edit `langgraph_server.py`
2. Add your tool function
3. Include it in the `tools=[get_weather, your_new_tool]` array
4. Restart: `Ctrl+C` then `./run.sh`

### Customizing the UI
1. Modify files in `agent-chat-ui/src/`
2. The UI will auto-reload on changes

### Debugging
- **LangGraph Logs**: Check terminal output prefixed with `[LangGraph]`
- **Chat UI Logs**: Check terminal output prefixed with `[Chat UI]`
- **API Documentation**: http://localhost:2024/docs
- **LangSmith Studio**: https://smith.langchain.com/studio/?baseUrl=http://127.0.0.1:2024

## 📁 **File Structure**

```
agent-sandbox-test/
├── 🚀 MAIN COMMANDS
│   ├── run.sh                  # 🎯 Start everything (auto-setup)
│   └── stop.sh                 # Stop both servers
│
├── 🤖 AGENT CODE
│   ├── langgraph_server.py     # LangGraph API server
│   ├── langgraph.json         # LangGraph configuration  
│   ├── agent.py               # Standalone version
│   └── agent-chat-ui/         # Beautiful web interface
│
├── ⚙️ CONFIG
│   ├── requirements.txt       # Python dependencies
│   ├── .env                   # Your API keys
│   ├── env.example           # Template
│   └── langgraph_agent/      # Auto-created virtual env
│
└── 📚 DOCS
    └── README.md             # This file
```

## 🎯 **Next Steps**

1. **🎨 Customize**: Add your own tools and modify the UI
2. **🚀 Deploy**: Use LangGraph Cloud for production
3. **📊 Monitor**: Set up analytics and logging
4. **🔐 Secure**: Add authentication for production use

---

## 🏆 **Success!**

Your LangGraph agent is now running with a beautiful web interface!

**🌐 Open**: http://localhost:3000  
**💬 Test**: "What's the weather in Tokyo?"  
**🛑 Stop**: Ctrl+C or `./stop.sh`

## 💡 **Pro Tips**

- **First run**: Takes ~1-2 minutes to install dependencies
- **Subsequent runs**: Start instantly  
- **Development**: Leave running and edit code - auto-reloads!
- **Stuck?**: Use `./stop.sh` to force-stop everything 