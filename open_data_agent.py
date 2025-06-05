import os
import asyncio
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain.chat_models import init_chat_model
from langchain_mcp_adapters.client import MultiServerMCPClient

# Load environment variables
load_dotenv()

async def create_open_data_agent():
    """Create an Open Data Agent that can search and analyze CKAN datasets."""
    
    # Check if API key is available
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")
    
    # Create MCP client for CKAN server
    client = MultiServerMCPClient({
        "ckan": {
            "command": "python",
            "args": [os.path.abspath("mcp_ckan_server.py")],
            "transport": "stdio",
        }
    })
    
    # Get tools from MCP server
    tools = await client.get_tools()
    
    # Initialize the model
    model = init_chat_model(
        "openai:gpt-3.5-turbo",
        temperature=0.1
    )
    
    # Create the agent with MCP tools
    agent = create_react_agent(
        model=model,
        tools=tools,
        prompt="""You are an Open Data Agent specialized in finding and analyzing open government datasets through CKAN data portals.

Your capabilities include:
- Searching for datasets using keywords
- Getting detailed information about specific datasets
- Analyzing dataset metadata, resources, and descriptions
- Helping users understand what data is available and how to access it

When users ask about data, try to:
1. Search for relevant datasets first
2. Provide clear summaries of what you find
3. Include important details like data formats, update frequency, and access URLs
4. Suggest related datasets that might be useful

Always be helpful in explaining what the data contains and how it might be used."""
    )
    
    return agent

# For testing the agent directly
async def main():
    try:
        agent = await create_open_data_agent()
        print("Open Data Agent created successfully!")
        
        # Test query
        config = {"configurable": {"thread_id": "test"}}
        response = await agent.ainvoke(
            {"messages": [{"role": "user", "content": "Search for datasets about climate change"}]},
            config
        )
        
        print("Test response:", response['messages'][-1].content)
        
    except Exception as e:
        print(f"Error creating Open Data Agent: {e}")

if __name__ == "__main__":
    asyncio.run(main()) 