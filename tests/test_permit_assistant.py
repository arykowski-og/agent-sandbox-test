#!/usr/bin/env python3
"""
Test script for the permit assistant to verify it's working correctly
"""

import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_permit_assistant():
    """Test the permit assistant functionality"""
    try:
        print("🧪 Testing Permit Assistant...")
        print("=" * 50)
        
        # Test 1: Check if tools are loading correctly
        print("1. Testing MCP tool loading...")
        from src.agents.permit_assistant.tools import get_permit_tools
        
        tools = await get_permit_tools()
        print(f"   ✅ Loaded {len(tools)} tools from MCP server")
        
        if len(tools) > 0:
            print("   📋 Available tools:")
            for i, tool in enumerate(tools[:10]):  # Show first 10 tools
                if hasattr(tool, 'name'):
                    print(f"      {i+1}. {tool.name}")
                else:
                    print(f"      {i+1}. {type(tool).__name__}")
            if len(tools) > 10:
                print(f"      ... and {len(tools) - 10} more tools")
        else:
            print("   ❌ No tools loaded - this might be the issue!")
            return
        
        # Test 2: Check if the graph can be created
        print("\n2. Testing graph creation...")
        from src.agents.permit_assistant.graph import create_permit_agent
        
        graph = await create_permit_agent()
        print("   ✅ Graph created successfully")
        
        # Test 3: Test a simple interaction
        print("\n3. Testing permit search interaction...")
        
        # Create a test message asking for permits
        from langchain_core.messages import HumanMessage
        test_messages = [
            HumanMessage(content="Search for all permits in presentation-alex community")
        ]
        
        # Invoke the graph
        result = await graph.ainvoke({
            "messages": test_messages,
            "ui": [],
            "ui_handled": False
        })
        
        print("   📝 Response received:")
        if "messages" in result:
            last_message = result["messages"][-1]
            if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                print(f"   ✅ LLM called {len(last_message.tool_calls)} tools:")
                for tool_call in last_message.tool_calls:
                    print(f"      - {tool_call.get('name', 'unknown')} with args: {tool_call.get('args', {})}")
                print("   🎉 SUCCESS: The permit assistant is now calling tools correctly!")
            else:
                print(f"   ❌ LLM did not call any tools. Response: {last_message.content[:200]}...")
                print("   This means our fix didn't work - the LLM is still not calling tools.")
        
        print("\n🎉 Test completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_permit_assistant()) 