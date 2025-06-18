#!/usr/bin/env python3
"""
Debug script to test OpenGov API calls and identify pagination issues
"""

import asyncio
import sys
import os
import json

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

async def test_api_calls():
    """Test different API call scenarios to identify the issue"""
    try:
        print("🔍 Debugging OpenGov API calls...")
        print("=" * 50)
        
        from src.agents.permit_assistant.tools import get_permit_tools
        
        tools = await get_permit_tools()
        print(f"✅ Loaded {len(tools)} tools")
        
        # Find the get_records tool
        get_records_tool = None
        for tool in tools:
            if hasattr(tool, 'name') and tool.name == 'get_records':
                get_records_tool = tool
                break
        
        if not get_records_tool:
            print("❌ get_records tool not found!")
            return
        
        print("🧪 Testing different API call scenarios...")
        
        # Test 1: Basic call with default pagination
        print("\n1. Testing basic call with default pagination...")
        try:
            result1 = await get_records_tool.ainvoke({
                "community": "Presentation-Alex"
            })
            print(f"   Result: {type(result1)} - {str(result1)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 2: Call with smaller page size
        print("\n2. Testing with smaller page size...")
        try:
            result2 = await get_records_tool.ainvoke({
                "community": "Presentation-Alex",
                "page_size": 5
            })
            print(f"   Result: {type(result2)} - {str(result2)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 3: Call without enhanced details
        print("\n3. Testing without enhanced details...")
        try:
            result3 = await get_records_tool.ainvoke({
                "community": "Presentation-Alex",
                "include_enhanced_details": False
            })
            print(f"   Result: {type(result3)} - {str(result3)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 4: Call with page number 0 (might be causing issues)
        print("\n4. Testing with page number 0...")
        try:
            result4 = await get_records_tool.ainvoke({
                "community": "Presentation-Alex",
                "page_number": 0,
                "include_enhanced_details": False
            })
            print(f"   Result: {type(result4)} - {str(result4)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        # Test 5: Call with no pagination parameters using direct import
        print("\n5. Testing with no pagination parameters (direct API call)...")
        try:
            # Import the MCP server module directly
            sys.path.append('src/mcp-servers')
            from opengov_plc_mcp_server import get_client
            
            client = get_client()
            result5 = await client.make_request("GET", "/records", "Presentation-Alex", params={})
            print(f"   Result type: {type(result5)}")
            if isinstance(result5, dict):
                print(f"   Keys: {list(result5.keys())}")
                if 'error' in result5:
                    print(f"   Error details: {json.dumps(result5, indent=2)}")
                else:
                    print(f"   Success! Data type: {type(result5.get('data'))}")
                    if 'data' in result5:
                        print(f"   Number of records: {len(result5['data']) if isinstance(result5['data'], list) else 'not a list'}")
        except Exception as e:
            print(f"   Error: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 6: Check authentication
        print("\n6. Testing authentication...")
        try:
            sys.path.append('src/mcp-servers')
            from opengov_plc_mcp_server import get_client
            
            client = get_client()
            token = await client.get_access_token()
            print(f"   Token obtained: {token[:20]}..." if token else "   No token obtained")
        except Exception as e:
            print(f"   Auth error: {e}")
        
        # Test 7: Try a different endpoint
        print("\n7. Testing organization endpoint...")
        try:
            sys.path.append('src/mcp-servers')
            from opengov_plc_mcp_server import get_client
            
            client = get_client()
            result7 = await client.make_request("GET", "/organization", "Presentation-Alex", params={})
            print(f"   Organization result: {type(result7)} - {str(result7)[:200]}...")
        except Exception as e:
            print(f"   Error: {e}")
        
        print("\n🎉 Debug completed!")
        
    except Exception as e:
        print(f"❌ Debug failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_api_calls()) 