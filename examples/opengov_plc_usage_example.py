#!/usr/bin/env python3
"""
Example: Using OpenGov Permitting & Licensing MCP Server with LangGraph

This example demonstrates how to integrate the OpenGov PLC MCP server with LangGraph agents
following the LangGraph MCP integration pattern.
"""

import asyncio
import os
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent

async def main():
    """Main example function"""
    
    # Ensure environment variables are set
    if not os.getenv("OG_PLC_CLIENT_ID") or not os.getenv("OG_PLC_SECRET"):
        print("Please set OG_PLC_CLIENT_ID and OG_PLC_SECRET environment variables")
        return
    
    # Configure MCP client with OpenGov PLC server
    client = MultiServerMCPClient(
        {
            "opengov_plc": {
                "command": "python",
                # Replace with absolute path to your opengov_plc_mcp_server.py file
                "args": ["/absolute/path/to/opengov_plc_mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    
    # Get tools from the MCP server
    print("Loading OpenGov PLC tools...")
    tools = await client.get_tools()
    print(f"Loaded {len(tools)} tools from OpenGov PLC MCP server")
    
    # Create a LangGraph agent with the tools
    agent = create_react_agent(
        "anthropic:claude-3-5-sonnet-latest",  # or your preferred model
        tools
    )
    
    # Example queries you can run
    examples = [
        "Get all records for the community 'demo'",
        "Show me the departments in the 'demo' community",
        "List the record types available in 'demo'",
        "Get organization information for 'demo'",
        "Find all users in the 'demo' community",
    ]
    
    print("\nExample queries you can ask:")
    for i, example in enumerate(examples, 1):
        print(f"{i}. {example}")
    
    # Example: Get records
    print("\n" + "="*50)
    print("EXAMPLE: Getting records from demo community")
    print("="*50)
    
    try:
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "Get all records for the community 'demo'"}]
        })
        print("Response:", response)
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure your OpenGov API credentials are valid and the 'demo' community exists.")
    
    # Example: Get organization info
    print("\n" + "="*50)
    print("EXAMPLE: Getting organization information")
    print("="*50)
    
    try:
        response = await agent.ainvoke({
            "messages": [{"role": "user", "content": "Get organization information for the community 'demo'"}]
        })
        print("Response:", response)
    except Exception as e:
        print(f"Error: {e}")

async def interactive_mode():
    """Interactive mode for testing queries"""
    
    # Configure MCP client
    client = MultiServerMCPClient(
        {
            "opengov_plc": {
                "command": "python",
                "args": ["/absolute/path/to/opengov_plc_mcp_server.py"],
                "transport": "stdio",
            }
        }
    )
    
    tools = await client.get_tools()
    agent = create_react_agent("anthropic:claude-3-5-sonnet-latest", tools)
    
    print("OpenGov PLC Interactive Mode")
    print("Type 'quit' to exit")
    print("-" * 40)
    
    while True:
        try:
            user_input = input("\nEnter your query: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if not user_input:
                continue
                
            response = await agent.ainvoke({
                "messages": [{"role": "user", "content": user_input}]
            })
            
            print(f"\nResponse: {response}")
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Error: {e}")
    
    print("\nGoodbye!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_mode())
    else:
        asyncio.run(main()) 