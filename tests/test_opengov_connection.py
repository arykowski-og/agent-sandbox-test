#!/usr/bin/env python3
import asyncio
import sys
import os
sys.path.append('src')

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

from src.mcp.opengov_plc_mcp_server import OpenGovPLCClient

async def test_connection():
    """Test the OpenGov API connection"""
    try:
        print("🔍 Testing OpenGov API connection...")
        
        # Create client instance
        client = OpenGovPLCClient()
        print(f"📍 Base URL: {client.base_url}")
        print(f"🔑 Client ID: {client.client_id[:10]}..." if client.client_id else "❌ No Client ID")
        # Test organization endpoint
        print("Testing organization lookup...")
        org_result = await client.make_request("GET", "/organization", "presentation-alex")
        print(f'✅ Organization data retrieved: {org_result.get("name", "Unknown")}')

          # Test records endpoint
        print("Testing records lookup...")
        records_result = await client.make_request("GET", "/records", "presentation-alex")
        record_count = len(records_result.get('data', []))
        print(f'✅ Records retrieved: {record_count} records')
        
        if record_count > 0:
            first_record = records_result['data'][0]
            print(f'📋 First record: {first_record.get("recordNumber", "Unknown")} - {first_record.get("recordType", {}).get("name", "Unknown Type")}')
            print(f'📊 Record status: {first_record.get("status", "Unknown")}')
            print(f'📅 Created: {first_record.get("createdAt", "Unknown")}')


        

        
        # Test record types
        print("Testing record types...")
        types_result = await client.make_request("GET", "/recordTypes", "presentation-alex")
        types_count = len(types_result.get('data', []))
        print(f'✅ Found {types_count} record types')
        
        print("🎉 OpenGov API connection successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error connecting to OpenGov API: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1) 