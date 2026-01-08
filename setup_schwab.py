#!/usr/bin/env python3
"""
Setup script for Schwab API credentials
This script helps you set up your .env file with Schwab API credentials
"""

import os
from pathlib import Path

def create_env_file():
    """Create or update .env file with user's credentials"""
    env_path = Path(__file__).parent / '.env'
    
    # Check if .env already exists
    if env_path.exists():
        print(f"\n.env file already exists at {env_path}")
        response = input("Do you want to overwrite it? (y/n): ").strip().lower()
        if response != 'y':
            print("Keeping existing .env file.")
            return
    
    print("\n" + "="*60)
    print("Schwab API Credentials Setup")
    print("="*60)
    print("\nYou need to get your credentials from:")
    print("  https://developer.schwab.com/dashboard/apps")
    print("\nMake sure you have:")
    print("  1. Created a Schwab developer account")
    print("  2. Created an app with callback URL: https://127.0.0.1")
    print("  3. Added both API products: 'Accounts and Trading Production' and 'Market Data Production'")
    print("  4. Wait until app status is 'Ready for use'")
    print("\n" + "-"*60)
    
    app_key = input("\nEnter your App Key: ").strip()
    app_secret = input("Enter your App Secret: ").strip()
    callback_url = input("Enter callback URL (default: https://127.0.0.1): ").strip() or "https://127.0.0.1"
    
    # Validate inputs
    if not app_key or not app_secret:
        print("\nError: App Key and App Secret are required!")
        return
    
    # Create .env content
    env_content = f"""# Schwab API Credentials
# Get these from https://developer.schwab.com/dashboard/apps

app_key={app_key}
app_secret={app_secret}
callback_url={callback_url}

# Optional: Encryption key for token database (see encrypted_db_setup.py example)
# encryption=YOUR_ENCRYPTION_KEY_HERE
"""
    
    # Write .env file
    try:
        env_path.write_text(env_content)
        print(f"\n✓ Successfully created .env file at {env_path}")
        print("\nNext steps:")
        print("  1. Make sure your Schwab developer app is 'Ready for use'")
        print("  2. Run one of the example scripts (e.g., docs/examples/api_demo.py)")
        print("  3. On first run, you'll need to authenticate via the browser")
    except Exception as e:
        print(f"\nError creating .env file: {e}")
        print("\nYou can manually create a .env file with:")
        print("  app_key=YOUR_APP_KEY")
        print("  app_secret=YOUR_APP_SECRET")
        print("  callback_url=https://127.0.0.1")

if __name__ == "__main__":
    create_env_file()


