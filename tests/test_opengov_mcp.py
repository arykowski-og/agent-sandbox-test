#!/usr/bin/env python3
"""
Test script for OpenGov Permitting & Licensing MCP Server

This script tests basic functionality of the MCP server without requiring
a full LangGraph setup.
"""

import os
import sys
import asyncio
import subprocess
import json
from typing import Dict, Any

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["OG_PLC_CLIENT_ID", "OG_PLC_SECRET"]
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

def test_server_import():
    """Test if the server can be imported successfully"""
    try:
        # Try to import the server module
        sys.path.insert(0, os.getcwd())
        import opengov_plc_mcp_server
        print("✅ Server module imports successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import server module: {e}")
        return False
    except Exception as e:
        print(f"❌ Error importing server: {e}")
        return False

def test_client_creation():
    """Test if the OpenGov client can be created"""
    try:
        sys.path.insert(0, os.getcwd())
        from opengov_plc_mcp_server import OpenGovPLCClient
        
        client = OpenGovPLCClient()
        print("✅ OpenGov client created successfully")
        print(f"   - Base URL: {client.base_url}")
        print(f"   - Auth URL: {client.auth_url}")
        return True, client
    except Exception as e:
        print(f"❌ Failed to create OpenGov client: {e}")
        return False, None

async def test_authentication(client):
    """Test OAuth2 authentication"""
    try:
        token = await client.get_access_token()
        print("✅ Authentication successful")
        print(f"   - Token obtained (length: {len(token)} chars)")
        return True
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return False

def test_dependencies():
    """Test if required dependencies are installed"""
    required_packages = ["mcp", "aiohttp"]
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\nInstall with: pip install -r requirements-opengov.txt")
        return False
    
    print("✅ All required dependencies are installed")
    return True

async def test_basic_api_call(client):
    """Test a basic API call"""
    try:
        # Test with a simple organization call
        result = await client.make_request("GET", "/organization", "demo")
        print("✅ Basic API call successful")
        print(f"   - Response type: {type(result)}")
        return True
    except Exception as e:
        print(f"⚠️  API call failed (this may be expected): {e}")
        print("   - This could be due to invalid community name or API permissions")
        return False

def count_mcp_tools():
    """Count the number of MCP tools defined"""
    try:
        sys.path.insert(0, os.getcwd())
        import opengov_plc_mcp_server
        
        # Count functions with @mcp.tool() decorator
        tool_count = 0
        for name in dir(opengov_plc_mcp_server):
            obj = getattr(opengov_plc_mcp_server, name)
            if callable(obj) and hasattr(obj, '__name__') and not name.startswith('_'):
                # Check if it's likely a tool function
                if asyncio.iscoroutinefunction(obj) and 'community' in str(obj.__annotations__.get('community', '')):
                    tool_count += 1
        
        print(f"✅ Found approximately {tool_count} MCP tools")
        return tool_count
    except Exception as e:
        print(f"❌ Failed to count tools: {e}")
        return 0

async def main():
    """Main test function"""
    print("OpenGov Permitting & Licensing MCP Server Test")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Environment variables
    total_tests += 1
    if check_environment():
        tests_passed += 1
    
    print()
    
    # Test 2: Dependencies
    total_tests += 1
    if test_dependencies():
        tests_passed += 1
    
    print()
    
    # Test 3: Server import
    total_tests += 1
    if test_server_import():
        tests_passed += 1
    
    print()
    
    # Test 4: Client creation
    total_tests += 1
    success, client = test_client_creation()
    if success:
        tests_passed += 1
    
    print()
    
    # Test 5: Authentication (only if client was created)
    if client:
        total_tests += 1
        if await test_authentication(client):
            tests_passed += 1
        
        print()
        
        # Test 6: Basic API call (only if authentication worked)
        total_tests += 1
        if await test_basic_api_call(client):
            tests_passed += 1
        
        print()
    
    # Test 7: Count tools
    total_tests += 1
    tool_count = count_mcp_tools()
    if tool_count > 0:
        tests_passed += 1
    
    print()
    print("=" * 50)
    print(f"Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Your OpenGov MCP server is ready to use.")
        print("\nNext steps:")
        print("1. Try the usage example: python opengov_plc_usage_example.py")
        print("2. Use with LangGraph as shown in the README")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        
        if tests_passed >= 5:  # Most core functionality works
            print("\nCore functionality appears to work. API failures may be due to:")
            print("- Invalid community name ('demo' used in tests)")
            print("- API permissions or network issues")
            print("- Staging vs production environment differences")

if __name__ == "__main__":
    asyncio.run(main()) 