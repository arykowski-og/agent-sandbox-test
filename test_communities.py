#!/usr/bin/env python3
import asyncio
import sys
import json
sys.path.append('src')
sys.path.append('src/mcp-servers')
from opengov_plc_mcp_server import get_client

async def test_communities():
    client = get_client()
    
    # Test different community names
    communities_to_test = [
        "Presentation-Alex",
        "presentation-alex", 
        "PresentationAlex",
        "demo",
        "test",
        "sandbox"
    ]
    
    for community in communities_to_test:
        print(f"\n🧪 Testing community: {community}")
        
        # Try organization endpoint first (simpler)
        try:
            org_result = await client.make_request('GET', '/organization', community, params={})
            if 'error' not in org_result:
                print(f"   ✅ Organization endpoint works for {community}")
                print(f"   Organization data: {json.dumps(org_result, indent=2)[:200]}...")
            else:
                print(f"   ❌ Organization error: {org_result.get('status')} - {org_result.get('message')}")
        except Exception as e:
            print(f"   ❌ Organization exception: {e}")
        
        # Try records endpoint
        try:
            records_result = await client.make_request('GET', '/records', community, params={})
            if 'error' not in records_result:
                print(f"   ✅ Records endpoint works for {community}")
                if 'data' in records_result:
                    print(f"   Found {len(records_result['data'])} records")
            else:
                print(f"   ❌ Records error: {records_result.get('status')} - {records_result.get('message')}")
                if records_result.get('status') != 500:  # Show details for non-500 errors
                    print(f"   Details: {records_result.get('details', '')[:100]}...")
        except Exception as e:
            print(f"   ❌ Records exception: {e}")

asyncio.run(test_communities()) 