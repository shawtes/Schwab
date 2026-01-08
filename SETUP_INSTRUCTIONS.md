# Schwab API Setup Instructions

## Prerequisites

1. **Schwab Developer Account**: 
   - Create account at https://developer.schwab.com/login
   - Use the **same email** as your Schwab brokerage account
   
2. **Schwab Developer App**:
   - Go to https://developer.schwab.com/dashboard/apps
   - Create a new app with callback URL: `https://127.0.0.1`
   - Add both API products:
     - **Accounts and Trading Production**
     - **Market Data Production**
   - Wait until app status is **"Ready for use"** (not "Approved - Pending")
   
3. **Thinkorswim (TOS)**:
   - Enable Thinkorswim for your Schwab account
   - Log into Thinkorswim at least once

## Quick Setup

### Option 1: Automated Setup Script

Run the setup script:
```bash
python3 setup_schwab.py
```

This will prompt you for your credentials and create a `.env` file.

### Option 2: Manual Setup

1. Create a `.env` file in this directory:
```bash
touch .env
```

2. Add your credentials to `.env`:
```
app_key=YOUR_APP_KEY_HERE
app_secret=YOUR_APP_SECRET_HERE
callback_url=https://127.0.0.1
```

Replace `YOUR_APP_KEY_HERE` and `YOUR_APP_SECRET_HERE` with your actual credentials from the Schwab developer dashboard.

## Install Dependencies

Since this is the source code, you can either:

### Option A: Install schwabdev from PyPI (Recommended)
```bash
pip3 install schwabdev python-dotenv
```

### Option B: Install dependencies and use source code
```bash
pip3 install requests websockets cryptography aiohttp python-dotenv
```

If you get permission errors, use:
```bash
pip3 install --user schwabdev python-dotenv
```

Or use a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install schwabdev python-dotenv
```

## Test Your Setup

Once your `.env` file is configured and dependencies are installed, test with:

```bash
python3 docs/examples/api_demo.py
```

On first run, you'll need to:
1. Sign in to your Schwab account using the generated link
2. Agree to the terms and select account(s)
3. Copy the callback URL from your browser address bar
4. Paste it into the terminal

## Getting Your Credentials

Your App Key and App Secret can be found at:
https://developer.schwab.com/dashboard/apps

Click on your app to view the credentials.

## Additional Resources

- [Setup Guide](https://tylerebowers.github.io/Schwabdev/?source=pages%2Fsetupguide.html)
- [YouTube Tutorial](https://youtu.be/69cniU1CTf8)
- [Discord Community](https://discord.gg/m7SSjr9rs9)
- [Documentation](https://tylerebowers.github.io/Schwabdev/)


