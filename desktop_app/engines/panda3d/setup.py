#!/usr/bin/env python3
"""
Setup script for Advanced Cosmic Engine
Installs all dependencies and configures the environment
"""

import subprocess
import sys
import os
from pathlib import Path

def install_requirements():
    """Install required packages"""
    print("🚀 Installing Cosmic Engine Requirements...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        # Install from requirements.txt
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ])
        print("✅ All requirements installed successfully!")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing requirements: {e}")
        return False
        
    return True

def setup_directories():
    """Create necessary directories"""
    print("📁 Setting up directories...")
    
    dirs_to_create = [
        "models",
        "textures", 
        "shaders",
        "material_cache",
        "logs"
    ]
    
    for dir_name in dirs_to_create:
        dir_path = Path(__file__).parent / dir_name
        dir_path.mkdir(exist_ok=True)
        print(f"  Created: {dir_name}")
        
    print("✅ Directories created!")

def download_sample_data():
    """Download or copy sample astronomical data"""
    print("🌟 Setting up sample cosmic data...")
    
    data_dir = Path(__file__).parent.parent / "data" / "processed"
    
    if not data_dir.exists():
        print("⚠️  No existing cosmic data found.")
        print("   Run your existing data processing scripts first, or")
        print("   place cosmic_world.json in ../data/processed/")
    else:
        print("✅ Cosmic data directory found!")

def test_installation():
    """Test if everything is working"""
    print("🔬 Testing installation...")
    
    try:
        # Test core imports
        import numpy
        import panda3d
        from panda3d.core import *
        print("  ✅ Panda3D: OK")
        
        import astropy
        print("  ✅ Astropy: OK")
        
        import noise
        print("  ✅ Noise: OK")
        
        from PIL import Image
        print("  ✅ PIL: OK")
        
        import cv2
        print("  ✅ OpenCV: OK")
        
        # Test physics module
        sys.path.append(str(Path(__file__).parent))
        from physics import PhysicsEngine
        print("  ✅ Physics Engine: OK")
        
        from materials import MaterialSystem
        print("  ✅ Material System: OK")
        
        print("🎉 All tests passed! Ready to explore the cosmos!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def create_launcher():
    """Create a launcher script"""
    print("🚀 Creating launcher...")
    
    launcher_content = '''@echo off
REM Advanced Cosmic Engine Launcher
echo Starting Cosmic Engine v2.0...
echo.

REM Check if virtual environment exists
if exist "..\\venv\\Scripts\\activate.bat" (
    echo Activating virtual environment...
    call "..\\venv\\Scripts\\activate.bat"
) else (
    echo No virtual environment found, using system Python
)

echo Launching Cosmic Engine...
python main.py

echo.
echo Cosmic Engine exited.
pause
'''

    launcher_path = Path(__file__).parent / "run_cosmic_engine.bat"
    with open(launcher_path, 'w') as f:
        f.write(launcher_content)
    
    print(f"✅ Launcher created: {launcher_path}")

def main():
    """Main setup function"""
    print("=" * 60)
    print("🌌 ADVANCED COSMIC ENGINE SETUP")
    print("   Realistic 3D Space Simulation")
    print("=" * 60)
    print()
    
    # Step 1: Install requirements
    if not install_requirements():
        print("❌ Setup failed at requirements installation")
        return False
    
    print()
    
    # Step 2: Create directories
    setup_directories()
    print()
    
    # Step 3: Setup data
    download_sample_data()
    print()
    
    # Step 4: Test installation
    if not test_installation():
        print("❌ Setup failed at testing phase")
        return False
    
    print()
    
    # Step 5: Create launcher
    create_launcher()
    print()
    
    print("=" * 60)
    print("🎉 SETUP COMPLETE!")
    print("   • Run 'python main.py' to start the simulation")
    print("   • Or double-click 'run_cosmic_engine.bat'")
    print("   • Check logs/ directory for any issues")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n❌ Setup failed. Check error messages above.")
        input("Press Enter to exit...")
        sys.exit(1)
    else:
        print("\n✅ Setup completed successfully!")
        
        # Ask if user wants to run the engine now
        choice = input("\nWould you like to start the Cosmic Engine now? (y/N): ").lower()
        if choice in ['y', 'yes']:
            print("\nStarting Cosmic Engine...")
            try:
                from main import CosmicEngine
                app = CosmicEngine()
                app.run()
            except Exception as e:
                print(f"Error starting engine: {e}")
                input("Press Enter to exit...")
        else:
            input("Press Enter to exit...")
