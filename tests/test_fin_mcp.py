#!/usr/bin/env python3
"""
Test script for OpenGov FIN GraphQL MCP Server

This script tests the basic functionality of the MCP server.
"""

import asyncio
import os
import sys
import importlib.util
from dotenv import load_dotenv

# Import the module directly by file path to avoid naming conflicts
try:
    spec = importlib.util.spec_from_file_location(
        "opengov_fin_mcp_server", 
        os.path.join(os.path.dirname(__file__), "src", "mcp-servers", "opengov_fin_mcp_server.py")
    )
    opengov_fin_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(opengov_fin_module)
    
    # Extract the functions we need
    get_client = opengov_fin_module.get_client
    introspect_schema = opengov_fin_module.introspect_schema
    query_graphql = opengov_fin_module.query_graphql
    get_schema_types = opengov_fin_module.get_schema_types
    
except Exception as e:
    print(f"❌ Import error: {e}")
    print("Make sure you're running this from the project root directory")
    print("Current working directory:", os.getcwd())
    print("Expected file location: src/mcp-servers/opengov_fin_mcp_server.py")
    sys.exit(1)

async def test_fin_mcp_server():
    """Test the OpenGov FIN GraphQL MCP server"""
    print("🧪 Testing OpenGov FIN GraphQL MCP Server")
    print("=" * 50)
    
    # Load environment variables
    load_dotenv()
    
    # Check if required environment variables are set
    bearer_token = os.getenv("OG_FIN_BEARER_TOKEN")
    if not bearer_token:
        print("❌ Error: OG_FIN_BEARER_TOKEN environment variable not set")
        print("Please copy env.example to .env and set your bearer token")
        return
    
    print(f"✅ Bearer token configured (length: {len(bearer_token)})")
    
    try:
        # Test 1: Basic connectivity with a simple query
        print("\n📡 Test 1: Basic connectivity")
        result = await query_graphql("{ __typename }")
        if "error" in result:
            print(f"❌ Basic query failed: {result['error']}")
            return
        else:
            print("✅ Basic connectivity successful")
            print(f"   Response: {result}")
        
        # Test 2: Schema introspection
        print("\n🔍 Test 2: Schema introspection")
        schema_result = await introspect_schema()
        if "error" in schema_result:
            print(f"❌ Schema introspection failed: {schema_result['error']}")
            return
        else:
            print("✅ Schema introspection successful")
            if "schema_sdl" in schema_result:
                sdl_lines = schema_result["schema_sdl"].split('\n')
                print(f"   Schema SDL preview (first 10 lines):")
                for i, line in enumerate(sdl_lines[:10]):
                    print(f"   {line}")
                if len(sdl_lines) > 10:
                    print(f"   ... and {len(sdl_lines) - 10} more lines")
        
        # Test 3: Get schema types
        print("\n📋 Test 3: Get schema types")
        types_result = await get_schema_types()
        if "error" in types_result:
            print(f"❌ Get schema types failed: {types_result['error']}")
            return
        else:
            print("✅ Get schema types successful")
            print(f"   Total types: {types_result.get('total_types', 0)}")
            if "types" in types_result:
                print("   Sample types:")
                for type_info in types_result["types"][:5]:
                    print(f"   - {type_info['name']} ({type_info['kind']})")
        
        print("\n🎉 All tests passed! The OpenGov FIN GraphQL MCP server is working correctly.")
        
    except Exception as e:
        print(f"❌ Test failed with exception: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_fin_mcp_server()) 