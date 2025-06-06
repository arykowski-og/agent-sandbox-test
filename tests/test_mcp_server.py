#!/usr/bin/env python3
"""Test script to verify the MCP server works correctly"""

import asyncio
import sys
import os
sys.path.append('src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.mcp.opengov_plc_mcp_server import get_client

async def test_mcp_functions():
    """Test the core MCP functions"""
    try:
        print("🔍 Testing MCP server functions...")
        
        client = get_client()
        
        # Test 1: get_records
        print("Test 1: Testing get_records...")
        result1 = await client.make_request("GET", "/records", "presentation-alex")
        record_count1 = len(result1.get('data', []))
        print(f"✅ get_records: Retrieved {record_count1} records")
        
        # Test 2: get_locations
        print("Test 2: Testing get_locations...")
        result2 = await client.make_request("GET", "/locations", "presentation-alex")
        location_count = len(result2.get('data', []))
        print(f"✅ get_locations: Retrieved {location_count} locations")
        
        # Test 3: get_users
        print("Test 3: Testing get_users...")
        result3 = await client.make_request("GET", "/users", "presentation-alex")
        user_count = len(result3.get('data', []))
        print(f"✅ get_users: Retrieved {user_count} users")
        
        # Test 4: get_record_types
        print("Test 4: Testing get_record_types...")
        result4 = await client.make_request("GET", "/recordTypes", "presentation-alex")
        type_count = len(result4.get('data', []))
        print(f"✅ get_record_types: Retrieved {type_count} record types")
        
        # Test 5: get_organization
        print("Test 5: Testing get_organization...")
        result5 = await client.make_request("GET", "/organization", "presentation-alex")
        org_name = result5.get('name', 'Unknown')
        print(f"✅ get_organization: Retrieved organization '{org_name}'")
        
        print("🎉 All MCP server functions working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing MCP functions: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_mcp_functions())
    sys.exit(0 if success else 1) 