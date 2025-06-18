#!/usr/bin/env python3
"""
Comprehensive OpenGov API test to find working communities and endpoints
"""

import os
import asyncio
import aiohttp
import json
from dotenv import load_dotenv

load_dotenv()

async def test_opengov_comprehensive():
    """Comprehensive test of OpenGov API"""
    
    client_id = os.getenv("OG_PLC_CLIENT_ID")
    client_secret = os.getenv("OG_PLC_SECRET")
    base_url = os.getenv("OG_PLC_BASE_URL", "https://api.plce.opengov.com/plce-dome")
    auth_url = "https://accounts.viewpointcloud.com/oauth/token"
    
    print(f"🔑 Comprehensive OpenGov API Test")
    print(f"   Client ID: {client_id[:10]}..." if client_id else "   Client ID: Not set")
    print(f"   Base URL: {base_url}")
    
    if not client_id or not client_secret:
        print("❌ Missing credentials!")
        return None
    
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
                    return None
                
                token_data = await response.json()
                access_token = token_data["access_token"]
                print(f"✅ Got access token successfully")
                
    except Exception as e:
        print(f"❌ Exception getting token: {e}")
        return None
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    # Step 2: Try to find the base API info
    print("\n🌐 Step 2: Testing base API endpoints...")
    
    base_endpoints = [
        f"{base_url}/v2",
        f"{base_url}/v1", 
        f"{base_url}",
        "https://api.plce.opengov.com/plce-dome/v2",
        "https://api.plce.opengov.com/v2"
    ]
    
    async with aiohttp.ClientSession() as session:
        for endpoint in base_endpoints:
            print(f"\n   Testing base endpoint: {endpoint}")
            try:
                async with session.get(endpoint, headers=headers) as response:
                    print(f"      Status: {response.status}")
                    if response.status == 200:
                        data = await response.text()
                        print(f"      ✅ SUCCESS! Response: {data[:200]}...")
                    elif response.status in [401, 403]:
                        print(f"      🔒 Authentication issue")
                    elif response.status == 404:
                        print(f"      ❌ Not found")
                    else:
                        error_text = await response.text()
                        print(f"      ❌ Error: {error_text[:100]}...")
            except Exception as e:
                print(f"      ❌ Exception: {e}")
    
    # Step 3: Try common community names and patterns
    print("\n🏘️  Step 3: Testing extended community list...")
    
    # Extended list of possible community names
    test_communities = [
        "demo", "test", "sandbox", "example", "dev", "staging",
        "sample", "trial", "pilot", "training", "qa", "uat",
        "default", "main", "primary", "public", "guest",
        # Common city/county patterns
        "city", "county", "municipality", "town", "village",
        # Common organization patterns  
        "org", "organization", "agency", "dept", "department"
    ]
    
    working_communities = []
    
    async with aiohttp.ClientSession() as session:
        for community in test_communities:
            print(f"\n   Testing community: {community}")
            
            # Test multiple endpoints for each community
            endpoints_to_test = [
                f"{base_url}/v2/{community}/organization",
                f"{base_url}/v2/{community}/recordTypes", 
                f"{base_url}/v2/{community}/departments",
                f"{base_url}/v2/{community}/users",
                f"{base_url}/v2/{community}/records"
            ]
            
            community_works = False
            for endpoint in endpoints_to_test:
                try:
                    async with session.get(endpoint, headers=headers) as response:
                        if response.status == 200:
                            data = await response.json()
                            print(f"      ✅ SUCCESS on {endpoint.split('/')[-1]}! Found data")
                            working_communities.append({
                                "community": community,
                                "endpoint": endpoint.split('/')[-1],
                                "data_sample": str(data)[:200]
                            })
                            community_works = True
                            break
                        elif response.status == 500:
                            error_text = await response.text()
                            if "INTERNAL_SERVER_ERROR" in error_text:
                                print(f"      ⚠️  Server error on {endpoint.split('/')[-1]} (500)")
                            else:
                                print(f"      ❌ Error on {endpoint.split('/')[-1]}: {error_text[:50]}...")
                        elif response.status in [403, 404]:
                            print(f"      ❌ {response.status} on {endpoint.split('/')[-1]}")
                        else:
                            print(f"      ❌ {response.status} on {endpoint.split('/')[-1]}")
                except Exception as e:
                    print(f"      ❌ Exception on {endpoint.split('/')[-1]}: {e}")
            
            if community_works:
                print(f"      🎉 Community '{community}' is working!")
                return community
    
    # Step 4: Check if it's a permissions issue
    print("\n🔐 Step 4: Analyzing error patterns...")
    
    if not working_communities:
        print("   No working communities found.")
        print("   All tested endpoints returned errors.")
        print("\n   Possible causes:")
        print("   1. API credentials are for a specific community not in our test list")
        print("   2. API server is experiencing issues (all 500 errors)")
        print("   3. Authentication scope is limited")
        print("   4. API endpoint structure has changed")
        
        # Try to get more info from the error responses
        print("\n   Analyzing error details...")
        async with aiohttp.ClientSession() as session:
            test_url = f"{base_url}/v2/demo/records"
            try:
                async with session.get(test_url, headers=headers) as response:
                    error_text = await response.text()
                    try:
                        error_json = json.loads(error_text)
                        print(f"   Sample error structure: {json.dumps(error_json, indent=2)}")
                    except:
                        print(f"   Sample error text: {error_text}")
            except Exception as e:
                print(f"   Could not get error details: {e}")
    
    return working_communities[0]["community"] if working_communities else None

async def main():
    result = await test_opengov_comprehensive()
    
    if result:
        print(f"\n🎉 Found working community: {result}")
        print(f"💡 Update your test script to use community='{result}' instead of 'demo'")
        
        # Update the test script automatically
        try:
            with open("test_permit_assistant_comprehensive.py", "r") as f:
                content = f.read()
            
            updated_content = content.replace(
                'self.test_community = "demo"',
                f'self.test_community = "{result}"'
            )
            
            with open("test_permit_assistant_comprehensive.py", "w") as f:
                f.write(updated_content)
            
            print(f"✅ Updated test script to use community '{result}'")
            
        except Exception as e:
            print(f"❌ Could not update test script: {e}")
    else:
        print("\n❌ No working communities found.")
        print("💡 Recommendations:")
        print("   1. Contact OpenGov support to get the correct community identifier")
        print("   2. Check if the API credentials have the right permissions")
        print("   3. Verify the API endpoint is correct")
        print("   4. Check if there are any API status issues")

if __name__ == "__main__":
    asyncio.run(main()) 