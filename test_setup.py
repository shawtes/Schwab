#!/usr/bin/env python3
"""
Quick test script to verify Schwab API setup
This script uses the source code directly (no installation needed)
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path so we can import schwabdev
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

try:
    from dotenv import load_dotenv
    import schwabdev
    
    print("✓ Dependencies loaded successfully")
    
    # Load environment variables
    env_path = project_root / '.env'
    if not env_path.exists():
        print(f"\n❌ Error: .env file not found at {env_path}")
        print("Please run: python3 setup_schwab.py")
        sys.exit(1)
    
    load_dotenv(env_path)
    
    app_key = os.getenv('app_key')
    app_secret = os.getenv('app_secret')
    callback_url = os.getenv('callback_url', 'https://127.0.0.1')
    
    if not app_key or not app_secret:
        print("\n❌ Error: app_key or app_secret not found in .env file")
        sys.exit(1)
    
    print(f"✓ Found credentials in .env file")
    print(f"  App Key: {app_key[:10]}...")
    print(f"  Callback URL: {callback_url}")
    
    # Try to create a client (this will test the setup)
    print("\nAttempting to create Schwab client...")
    print("Note: On first run, you'll need to authenticate via browser")
    
    client = schwabdev.Client(app_key, app_secret, callback_url)
    print("✓ Client created successfully!")
    
    print("\n" + "="*60)
    print("Setup looks good! You can now use schwabdev.")
    print("="*60)
    print("\nTry running:")
    print("  python3 docs/examples/api_demo.py")
    print("\nOr use it in your own scripts:")
    print("  import sys")
    print("  sys.path.insert(0, '/Users/sineshawmesfintesfaye/Schwabdev')")
    print("  import schwabdev")
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMissing dependencies. Install them with:")
    print("  pip install requests websockets cryptography aiohttp python-dotenv")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nThis might be due to:")
    print("  1. Python version (requires 3.11+, you may have 3.8)")
    print("  2. Missing credentials")
    print("  3. Authentication needed (first time setup)")
    sys.exit(1)


