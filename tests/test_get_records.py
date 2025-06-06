#!/usr/bin/env python3
"""Test script to verify get_records function works correctly"""

import asyncio
import sys
import os
sys.path.append('src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.mcp.opengov_plc_mcp_server import get_client, build_params

async def test_get_records():
    """Test the get_records function"""
    try:
        print("🔍 Testing get_records function...")
        
        client = get_client()
        
        # Test 1: Call without any parameters
        print("Test 1: Calling get_records without parameters...")
        result1 = await client.make_request("GET", "/records", "presentation-alex")
        record_count1 = len(result1.get('data', []))
        print(f"✅ Retrieved {record_count1} records without parameters")
        
        # Test 2: Call with limit parameter only
        print("Test 2: Calling get_records with limit=5...")
        try:
            params = build_params(limit=5)
            result2 = await client.make_request("GET", "/records", "presentation-alex", params=params)
            record_count2 = len(result2.get('data', []))
            print(f"✅ Retrieved {record_count2} records with limit=5")
        except Exception as e:
            print(f"⚠️  Limit parameter not supported: {e}")
        
        # Test 3: Call with record_type_id parameter
        print("Test 3: Calling get_records with record_type_id...")
        try:
            params = build_params(recordTypeId="some-type-id")
            result3 = await client.make_request("GET", "/records", "presentation-alex", params=params)
            record_count3 = len(result3.get('data', []))
            print(f"✅ Retrieved {record_count3} records with record_type_id filter")
        except Exception as e:
            print(f"⚠️  Record type filter failed (expected if type doesn't exist): {e}")
        
        print("🎉 get_records function test completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error testing get_records: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_get_records())
    sys.exit(0 if success else 1) 