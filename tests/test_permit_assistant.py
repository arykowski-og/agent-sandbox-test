#!/usr/bin/env python3
"""
Test script for Permit Assistant Agent

This script tests the integration of the permit assistant with the OpenGov MCP server.
"""

import os
import sys
import asyncio
from typing import Dict, Any

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY", "OG_PLC_CLIENT_ID", "OG_PLC_SECRET"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these variables and try again.")
        return False
    
    print("✅ Environment variables are set")
    return True

def test_imports():
    """Test if all required packages can be imported"""
    try:
        from dotenv import load_dotenv
        from langgraph.prebuilt import create_react_agent
        from langchain.chat_models import init_chat_model
        from langchain_mcp_adapters.client import MultiServerMCPClient
        print("✅ All required packages imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import required packages: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_agent_module():
    """Test if the permit assistant module can be imported"""
    try:
        # Add src to path (go up one level from tests/ to project root, then into src/)
        project_root = os.path.dirname(os.path.dirname(__file__))
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from agents import permit_assistant
        print("✅ Permit assistant module imported successfully")
        
        # Check if graph is available
        if hasattr(permit_assistant, 'graph'):
            print("✅ Permit assistant graph is available")
            return True
        else:
            print("❌ Permit assistant graph not found")
            return False
            
    except Exception as e:
        print(f"❌ Failed to import permit assistant: {e}")
        return False

def test_mcp_server_file():
    """Test if MCP server file exists and is accessible"""
    mcp_path = os.path.join("src", "mcp-servers", "opengov_plc_mcp_server.py")
    
    if os.path.exists(mcp_path):
        print("✅ OpenGov MCP server file found")
        return True
    else:
        print(f"❌ OpenGov MCP server file not found at: {mcp_path}")
        return False

async def test_mcp_tools_loading():
    """Test if MCP tools can be loaded"""
    try:
        # Add src to path (go up one level from tests/ to project root, then into src/)
        project_root = os.path.dirname(os.path.dirname(__file__))
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from agents.permit_assistant.tools import get_permit_tools
        
        tools = await get_permit_tools()
        
        if tools:
            print(f"✅ Successfully loaded {len(tools)} MCP tools")
            
            # List some tool names
            tool_names = [tool.name for tool in tools[:5]]
            print(f"   Sample tools: {', '.join(tool_names)}")
            return True
        else:
            print("❌ No MCP tools loaded")
            return False
            
    except Exception as e:
        print(f"❌ Failed to load MCP tools: {e}")
        return False

async def test_short_term_memory():
    """Test if short-term memory is enabled in the permit assistant"""
    try:
        # Add src to path (go up one level from tests/ to project root, then into src/)
        project_root = os.path.dirname(os.path.dirname(__file__))
        src_path = os.path.join(project_root, 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from agents.permit_assistant.graph import create_permit_agent
        
        # Create the agent
        agent = await create_permit_agent()
        
        # Check if the agent has a checkpointer (indicates memory is enabled)
        if hasattr(agent, 'checkpointer') and agent.checkpointer is not None:
            print("✅ Short-term memory is enabled (checkpointer found)")
            print(f"   Checkpointer type: {type(agent.checkpointer).__name__}")
            return True
        else:
            print("❌ Short-term memory not enabled (no checkpointer found)")
            return False
            
    except Exception as e:
        print(f"❌ Failed to test short-term memory: {e}")
        return False

def test_langgraph_config():
    """Test if langgraph.json includes the permit assistant"""
    try:
        import json
        
        # Get the project root directory (go up one level from tests/)
        project_root = os.path.dirname(os.path.dirname(__file__))
        langgraph_path = os.path.join(project_root, 'langgraph.json')
        
        with open(langgraph_path, 'r') as f:
            config = json.load(f)
        
        graphs = config.get('graphs', {})
        
        if 'permit_assistant' in graphs:
            print("✅ Permit assistant found in langgraph.json")
            print(f"   Path: {graphs['permit_assistant']}")
            return True
        else:
            print("❌ Permit assistant not found in langgraph.json")
            return False
            
    except Exception as e:
        print(f"❌ Failed to read langgraph.json: {e}")
        return False

async def main():
    """Main test function"""
    print("Permit Assistant Integration Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Environment variables (informational only)
    print("📋 Test 1: Environment variables check (informational)")
    env_check = check_environment()
    if not env_check:
        print("ℹ️  Note: Environment variables not set - this is expected for basic testing")
    
    print()
    
    # Test 2: Package imports
    total_tests += 1
    if test_imports():
        tests_passed += 1
    
    print()
    
    # Test 3: MCP server file
    total_tests += 1
    if test_mcp_server_file():
        tests_passed += 1
    
    print()
    
    # Test 4: Agent module
    total_tests += 1
    if test_agent_module():
        tests_passed += 1
    
    print()
    
    # Test 5: LangGraph config
    total_tests += 1
    if test_langgraph_config():
        tests_passed += 1
    
    print()
    
    # Test 6: MCP tools loading (requires credentials)
    if os.getenv("OG_PLC_CLIENT_ID") and os.getenv("OG_PLC_SECRET"):
        total_tests += 1
        if await test_mcp_tools_loading():
            tests_passed += 1
    else:
        print("⚠️  Skipping MCP tools test - OpenGov credentials not configured")
        # Still test MCP tools loading without credentials to verify the server works
        total_tests += 1
        if await test_mcp_tools_loading():
            tests_passed += 1
    
    print()
    
    # Test 7: Short-term memory
    total_tests += 1
    if await test_short_term_memory():
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your permit assistant is ready to use.")
        print("\nNext steps:")
        print("1. Start LangGraph server: langgraph dev")
        print("2. Open agent-chat-ui with: http://localhost:3000/chat?assistantId=permit_assistant&apiUrl=http://localhost:8123")
        print("3. Start chatting with the permit assistant!")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
        if tests_passed >= 4:  # Core functionality works
            print("\nCore integration appears to work. Consider:")
            print("- Setting up OpenGov credentials for full functionality")
            print("- Testing with real OpenGov API endpoints")

if __name__ == "__main__":
    asyncio.run(main()) 