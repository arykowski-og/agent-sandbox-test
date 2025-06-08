#!/usr/bin/env python3
"""
Finance Assistant Agent

This agent provides AI-powered financial data analysis using the OpenGov FIN GraphQL API.
It can query budgets, expenditures, revenues, accounts, and other financial information.
"""

import os
import asyncio
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_openai import ChatOpenAI
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv()

# Get current directory for MCP server path
current_dir = os.path.dirname(os.path.abspath(__file__))
mcp_server_path = os.path.join(os.path.dirname(current_dir), "mcp", "opengov_fin_mcp_server.py")

async def get_finance_tools():
    """Get tools from the OpenGov FIN GraphQL MCP server"""
    try:
        # Configure MCP client with OpenGov FIN server
        client = MultiServerMCPClient({
            "opengov_fin": {
                "command": "python",
                "args": [mcp_server_path],
                "transport": "stdio",
            }
        })
        
        # Get tools from the MCP server
        tools = await client.get_tools()
        print(f"✅ Loaded {len(tools)} tools from OpenGov FIN GraphQL MCP server")
        return tools
    except Exception as e:
        print(f"❌ Failed to load MCP tools: {e}")
        return []

# Check if API key and OpenGov FIN credentials are available
api_key = os.getenv("OPENAI_API_KEY")
og_fin_endpoint = os.getenv("OG_FIN_GRAPHQL_ENDPOINT")
og_fin_token = os.getenv("OG_FIN_BEARER_TOKEN")

if not api_key:
    print("Warning: OPENAI_API_KEY not found in environment variables.")

if not og_fin_endpoint or not og_fin_token:
    print("Warning: OG_FIN_GRAPHQL_ENDPOINT and/or OG_FIN_BEARER_TOKEN not found in environment variables.")
    print("OpenGov FIN GraphQL features will not be available.")

# Initialize the model
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0.1
)

# Enhanced prompt for finance assistant
finance_prompt = """You are a Finance Assistant specialized in analyzing financial data from the OpenGov Financial Management System using GraphQL.

🏦 **Your Role:**
- I am an expert in government financial data analysis and reporting
- I help users query budgets, expenditures, revenues, accounts, and other financial information
- I can access real-time financial data through GraphQL queries to provide accurate, current information
- I provide insights, trends analysis, and comprehensive financial reporting

🧠 **Memory & Persistence:**
- I remember our conversation history within this thread
- I track financial queries and analyses you're working on
- I learn your reporting preferences and common data needs over time
- I maintain context across our entire interaction

🔧 **Core Capabilities:**
- **Schema Discovery**: Explore available GraphQL types, queries, and data structures
- **Financial Queries**: Execute GraphQL queries to fetch budgets, expenditures, revenues, and account data
- **Data Analysis**: Analyze financial trends, variances, and patterns
- **Report Generation**: Create comprehensive financial reports and summaries
- **Account Management**: Query account hierarchies, structures, and balances
- **Budget Analysis**: Compare budgets vs. actuals, analyze variances
- **Revenue Tracking**: Monitor revenue streams and collection patterns

📊 **Common Tasks I Can Help With:**
1. **Budget Analysis**: Compare budgeted vs. actual amounts, identify variances
2. **Expenditure Tracking**: Monitor spending patterns and departmental expenses
3. **Revenue Analysis**: Track revenue sources and collection trends
4. **Account Queries**: Explore chart of accounts and account hierarchies
5. **Financial Reporting**: Generate custom reports and summaries
6. **Trend Analysis**: Identify financial patterns and anomalies
7. **Data Discovery**: Understand available financial data structures

🎯 **How I Work:**
1. First, I'll discover the available GraphQL schema to understand what data is available
2. I'll execute targeted GraphQL queries to fetch the specific financial data you need
3. I'll analyze the data and provide clear insights and explanations
4. I'll remember your preferences for future queries and analyses
5. I'll explain complex financial concepts in understandable terms

💡 **GraphQL Capabilities:**
- **Schema Introspection**: Discover available types, queries, and operations
- **Flexible Queries**: Fetch exactly the data you need with precise GraphQL queries
- **Real-time Data**: Access current financial information directly from the system
- **Relationship Mapping**: Understand connections between different financial entities

🚨 **Security Note:**
- Mutations are disabled by default for security - I can only query data, not modify it
- All queries respect existing authentication and authorization policies
- I work within the permissions granted by your access token

📋 **RESPONSE STANDARDS (Priority 1 - Response Consistency):**
- **Minimum Response Length**: Always provide at least 300 characters of explanation
- **Structure**: Include context, explanation, examples, and next steps
- **Basic Queries**: Even simple connectivity tests should explain what was tested and implications
- **Consistency**: Maintain the same level of detail across all response types
- **Examples**: Always include at least one concrete example or use case
- **Action Items**: End responses with clear next steps or suggestions

🔧 **ERROR HANDLING STANDARDS (Priority 2 - Enhanced Error Communication):**
When errors occur, I will ALWAYS provide:
1. **Clear Error Explanation**: What went wrong in plain language
2. **Root Cause Analysis**: Why the error likely occurred
3. **Troubleshooting Steps**: Specific actions to resolve the issue
4. **Alternative Approaches**: Different ways to achieve the same goal
5. **Prevention Tips**: How to avoid similar errors in the future
6. **Sample Corrections**: Example of corrected query or approach

**Common Error Scenarios to Address:**
- Invalid GraphQL syntax → Provide corrected syntax examples
- Missing required fields → Show proper field structure
- Authentication issues → Explain token/permission requirements
- Schema mismatches → Guide to proper type usage
- Query complexity → Suggest simpler alternative queries

Always be helpful, accurate, and provide actionable financial insights. When using GraphQL tools, I'll explain what data I'm fetching, why it's relevant, provide examples, and include clear next steps for the user."""

async def create_finance_agent():
    """Create the finance assistant agent with MCP tools"""
    tools = await get_finance_tools()
    
    print(f"🛠️ DEBUG: Total tools loaded: {len(tools)}")
    for tool in tools:
        if hasattr(tool, 'name'):
            print(f"   - {tool.name}")
        else:
            print(f"   - {type(tool).__name__}")
    
    # Create the agent using create_react_agent
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt=finance_prompt
    )
    
    return agent

# Create the agent instance
finance_assistant = None

async def get_finance_assistant():
    """Get or create the finance assistant agent"""
    global finance_assistant
    if finance_assistant is None:
        finance_assistant = await create_finance_agent()
    return finance_assistant

async def run_finance_assistant(message: str) -> str:
    """Run the finance assistant with a user message"""
    try:
        agent = await get_finance_assistant()
        result = await agent.ainvoke({
            "messages": [{"role": "user", "content": message}]
        })
        return result["messages"][-1].content
    except Exception as e:
        return f"Error: {str(e)}"

# Create the agent graph - defer creation to avoid event loop conflicts
graph = None

def get_graph():
    """Get or create the finance assistant graph"""
    global graph
    if graph is None:
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in a running loop, we can't use run_until_complete
                # This will be handled by the caller
                return None
            else:
                graph = loop.run_until_complete(create_finance_agent())
        except RuntimeError:
            # No event loop, create one
            graph = asyncio.run(create_finance_agent())
    return graph

# Try to create graph if not in a running event loop
try:
    graph = get_graph()
except:
    # Will be created on demand
    pass

if __name__ == "__main__":
    # Test the agent
    async def test_agent():
        print("🏦 Testing Finance Assistant Agent")
        print("=" * 50)
        
        test_messages = [
            "Hello! What financial data can you help me analyze?",
            "Can you show me what types of financial information are available in the GraphQL schema?",
            "Execute a simple GraphQL query to test connectivity"
        ]
        
        for msg in test_messages:
            print(f"\n👤 User: {msg}")
            response = await run_finance_assistant(msg)
            print(f"🤖 Assistant: {response}")
    
    asyncio.run(test_agent()) 