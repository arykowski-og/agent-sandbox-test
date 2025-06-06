#!/usr/bin/env python3
"""Test script to verify environment variables are loaded correctly"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Test the OpenGov environment variables
client_id = os.getenv("OG_PLC_CLIENT_ID")
client_secret = os.getenv("OG_PLC_SECRET")
base_url = os.getenv("OG_PLC_BASE_URL")

print("Environment Variables Test:")
print(f"OG_PLC_CLIENT_ID: {'✓ Found' if client_id else '✗ Missing'}")
print(f"OG_PLC_SECRET: {'✓ Found' if client_secret else '✗ Missing'}")
print(f"OG_PLC_BASE_URL: {'✓ Found' if base_url else '✗ Missing'}")

if client_id and client_secret:
    print("\n✅ All required environment variables are loaded successfully!")
    print(f"Client ID (first 10 chars): {client_id[:10]}...")
    print(f"Base URL: {base_url}")
else:
    print("\n❌ Some required environment variables are missing!") 