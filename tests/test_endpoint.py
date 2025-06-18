#!/usr/bin/env python3
import asyncio
import sys
sys.path.append('src')
sys.path.append('src/mcp-servers')
from opengov_plc_mcp_server import get_client

async def test():
    client = get_client()
    result = await client.make_request('GET', '/public_api/records', 'Presentation-Alex', params={})
    print('Result:', result)

asyncio.run(test()) 