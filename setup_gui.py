#!/usr/bin/env python3
"""
Setup script for Trading GUI
Checks and installs required dependencies
"""

import sys
import subprocess

def check_and_install(package, import_name=None):
    """Check if package is installed, install if not"""
    if import_name is None:
        import_name = package
    
    try:
        __import__(import_name)
        print(f"✓ {package} is installed")
        return True
    except ImportError:
        print(f"✗ {package} is NOT installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])
            print(f"✓ {package} installed successfully")
            return True
        except subprocess.CalledProcessError:
            print(f"✗ Failed to install {package}")
            return False

def main():
    print("=" * 60)
    print("Trading GUI - Dependency Checker")
    print("=" * 60)
    print(f"\nPython: {sys.executable}")
    print(f"Version: {sys.version}\n")
    
    # Required packages
    packages = [
        ("python-dotenv", "dotenv"),
        ("numpy", "numpy"),
        ("pandas", "pandas"),
        ("matplotlib", "matplotlib"),
        ("scikit-learn", "sklearn"),
    ]
    
    print("Checking core dependencies...")
    all_ok = True
    for package, import_name in packages:
        if not check_and_install(package, import_name):
            all_ok = False
    
    print("\nChecking GUI framework...")
    # Try PySide6 first
    try:
        import PySide6
        print("✓ PySide6 is installed")
        gui_ok = True
    except ImportError:
        # Try PyQt5
        try:
            import PyQt5
            print("✓ PyQt5 is installed")
            gui_ok = True
        except ImportError:
            print("✗ Neither PySide6 nor PyQt5 is installed")
            print("  Installing PySide6 (recommended)...")
            if check_and_install("PySide6", "PySide6"):
                gui_ok = True
            else:
                print("  Trying PyQt5...")
                if check_and_install("PyQt5", "PyQt5"):
                    gui_ok = True
                else:
                    gui_ok = False
                    all_ok = False
    
    print("\n" + "=" * 60)
    if all_ok and gui_ok:
        print("✓ All dependencies are installed!")
        print("\nYou can now launch the GUI with:")
        print("  python3 launch_gui.py")
        print("=" * 60)
        return 0
    else:
        print("✗ Some dependencies failed to install")
        print("\nPlease install manually:")
        print("  pip install -r requirements.txt")
        print("=" * 60)
        return 1

if __name__ == '__main__':
    sys.exit(main())


