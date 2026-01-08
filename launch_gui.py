#!/usr/bin/env python3
"""
Quick launcher for Institutional Trading Platform GUI
"""

import sys
import os
from pathlib import Path

# Add project to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def check_environment():
    """Check if we're in the right environment"""
    python_path = sys.executable
    print(f"Using Python: {python_path}")
    
    # Check if we're in conda environment
    if 'conda' in python_path.lower() or 'envs' in python_path:
        print("✓ Conda environment detected")
    else:
        print("⚠ Warning: Not in conda environment")
        print("  If you have a conda environment, activate it first:")
        print("  conda activate schwabdev")
        print()

if __name__ == '__main__':
    check_environment()
    try:
        from trading_gui import main
        main()
    except ImportError as e:
        print("=" * 60)
        print("ERROR: Missing dependencies")
        print("=" * 60)
        print(f"\nError: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        print("\nOr if using conda:")
        print("  conda install -c conda-forge pyside6 python-dotenv matplotlib")
        print("\nMake sure you're in your conda environment:")
        print("  conda activate schwabdev")
        sys.exit(1)

