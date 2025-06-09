#!/usr/bin/env python3
"""
Direct test of OpenGov API to verify credentials and find valid communities
"""

import os
import asyncio
import aiohttp
from dotenv import load_dotenv

load_dotenv()

async def test_opengov_api():
    """Test OpenGov API directly"""
    
    client_id = os.getenv("OG_PLC_CLIENT_ID")
    client_secret = os.getenv("OG_PLC_SECRET")
    base_url = os.getenv("OG_PLC_BASE_URL", "https://api.plce.opengov.com/plce-dome")
    auth_url = "https://accounts.viewpointcloud.com/oauth/token"
    
    print(f"🔑 Testing OpenGov API credentials...")
    print(f"   Client ID: {client_id[:10]}..." if client_id else "   Client ID: Not set")
    print(f"   Base URL: {base_url}")
    
    if not client_id or not client_secret:
        print("❌ Missing credentials!")
        return
    
    # Step 1: Get access token
    print("\n🔐 Step 1: Getting access token...")
    try:
        async with aiohttp.ClientSession() as session:
            data = {
                "grant_type": "client_credentials",
                "client_id": client_id,
                "client_secret": client_secret,
                "audience": "viewpointcloud.com/api/production"
            }
            
            async with session.post(auth_url, data=data) as response:
                if response.status != 200:
                    error_text = await response.text()
                    print(f"❌ Failed to get access token: {response.status}")
                    print(f"   Error: {error_text}")
                    return
                
                token_data = await response.json()
                access_token = token_data["access_token"]
                print(f"✅ Got access token: {access_token[:20]}...")
                
    except Exception as e:
        print(f"❌ Exception getting token: {e}")
        return
    
    # Step 2: Test different communities
    print("\n🏘️  Step 2: Testing different communities...")
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    test_communities = ["demo", "test", "sandbox", "example", "dev"]
    
    async with aiohttp.ClientSession() as session:
        for community in test_communities:
            print(f"\n   Testing community: {community}")
            url = f"{base_url}/v2/{community}/records"
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"      Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"      ✅ SUCCESS! Found {len(data.get('data', []))} records")
                        print(f"      Sample response keys: {list(data.keys())}")
                        return community  # Return the first working community
                    elif response.status == 403:
                        print(f"      ❌ Access forbidden (403)")
                    elif response.status == 404:
                        print(f"      ❌ Not found (404)")
                    elif response.status == 500:
                        error_text = await response.text()
                        print(f"      ❌ Server error (500): {error_text[:100]}...")
                    else:
                        error_text = await response.text()
                        print(f"      ❌ Error {response.status}: {error_text[:100]}...")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
    
    # Step 3: Try to find organization info (might give us clues)
    print("\n🏢 Step 3: Testing organization endpoint...")
    
    async with aiohttp.ClientSession() as session:
        for community in test_communities:
            print(f"\n   Testing organization for: {community}")
            url = f"{base_url}/v2/{community}/organization"
            
            try:
                async with session.get(url, headers=headers) as response:
                    print(f"      Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"      ✅ SUCCESS! Organization found")
                        print(f"      Organization data: {data}")
                        return community
                    else:
                        error_text = await response.text()
                        print(f"      ❌ Error {response.status}: {error_text[:100]}...")
                        
            except Exception as e:
                print(f"      ❌ Exception: {e}")
    
    print("\n❌ No valid communities found. The API credentials may be for a specific community not in our test list.")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_opengov_api())
    if result:
        print(f"\n🎉 Found working community: {result}")
        print(f"💡 Update your test script to use community='{result}' instead of 'demo'")
    else:
        print("\n💡 You may need to contact OpenGov support to get the correct community identifier for your credentials.") 