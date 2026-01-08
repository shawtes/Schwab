#!/usr/bin/env python3
"""
Quick test script to verify Schwab API is working
"""

import sys
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import os
from dotenv import load_dotenv
import schwabdev

print("Loading credentials from .env file...")
load_dotenv()

app_key = os.getenv('app_key')
app_secret = os.getenv('app_secret')
callback_url = os.getenv('callback_url', 'https://127.0.0.1')

print("Creating Schwab client...")
client = schwabdev.Client(app_key, app_secret, callback_url)

print("\n✓ Client created successfully!")
print("\nTesting API call - Getting quote for AAPL...")
try:
    quote = client.quotes("AAPL").json()
    print("✓ API call successful!")
    print(f"\nAAPL Quote: {quote}")
except Exception as e:
    print(f"Error making API call: {e}")
    print("\nThis might be your first time - you may need to authenticate.")
    print("The authentication URL should have appeared above.")


