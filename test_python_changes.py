#!/usr/bin/env python3
"""
Test script to verify Python file changes work without rebuilding.
This script can be modified and run to test the volume mount functionality.
"""

import sys
import os
from datetime import datetime

def main():
    print("🐍 Python Change Test Script")
    print("=" * 40)
    print(f"Timestamp: {datetime.now()}")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path: {sys.path}")
    
    # Test if we can access mounted directories
    print("\n📁 Checking mounted directories:")
    
    # Check scripts directory
    scripts_path = "/workspace/scripts"
    if os.path.exists(scripts_path):
        print(f"✅ Scripts directory: {scripts_path}")
        scripts_files = os.listdir(scripts_path)
        print(f"   Files: {scripts_files[:5]}...")  # Show first 5 files
    else:
        print(f"❌ Scripts directory not found: {scripts_path}")
    
    # Check desktop_app directory
    desktop_path = "/workspace/desktop_app"
    if os.path.exists(desktop_path):
        print(f"✅ Desktop app directory: {desktop_path}")
        desktop_files = os.listdir(desktop_path)
        print(f"   Files: {desktop_files[:5]}...")  # Show first 5 files
    else:
        print(f"❌ Desktop app directory not found: {desktop_path}")
    
    # Check data directory
    data_path = "/workspace/data"
    if os.path.exists(data_path):
        print(f"✅ Data directory: {data_path}")
        data_files = os.listdir(data_path)
        print(f"   Files: {data_files[:5]}...")  # Show first 5 files
    else:
        print(f"❌ Data directory not found: {data_path}")
    
    # Test importing from mounted directories
    print("\n🔍 Testing imports:")
    try:
        # Try to import from scripts
        sys.path.insert(0, '/workspace/scripts')
        print("✅ Added /workspace/scripts to Python path")
    except Exception as e:
        print(f"❌ Error adding scripts to path: {e}")
    
    try:
        # Try to import from desktop_app
        sys.path.insert(0, '/workspace/desktop_app')
        print("✅ Added /workspace/desktop_app to Python path")
    except Exception as e:
        print(f"❌ Error adding desktop_app to path: {e}")
    
    print("\n✅ Test completed successfully!")
    print("💡 Modify this file and run again to test volume mounts!")

if __name__ == "__main__":
    main() 