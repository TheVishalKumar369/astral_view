#!/usr/bin/env python3
"""
Launch Script for 3D Cosmic Worlds

This script provides an easy way to launch different 3D visualization modes
of the cosmic data.
"""

import subprocess
import sys
from pathlib import Path
import argparse

def launch_desktop_app():
    """Launch the Ursina desktop 3D world"""
    print("🚀 Launching Enhanced Desktop Cosmic Explorer...")
    desktop_script = Path(__file__).parent / "desktop_app" / "cosmic_explorer.py"
    
    try:
        subprocess.run([sys.executable, str(desktop_script)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch desktop app: {e}")
    except FileNotFoundError:
        print("❌ Desktop app script not found. Make sure cosmic_explorer.py exists.")

def launch_web_portal():
    """Launch the web portal development server"""
    print("🌐 Launching Enhanced Web Portal...")
    web_dir = Path(__file__).parent / "web_portal"
    
    try:
        # Check if npm is available
        subprocess.run(["npm", "--version"], check=True, capture_output=True)
        
        # Install dependencies if needed
        print("📦 Installing dependencies...")
        subprocess.run(["npm", "install"], cwd=web_dir, check=True)
        
        # Start development server
        print("🚀 Starting development server...")
        subprocess.run(["npm", "start"], cwd=web_dir, check=True)
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to launch web portal: {e}")
    except FileNotFoundError:
        print("❌ npm not found. Please install Node.js and npm to run the web portal.")

def generate_new_worlds():
    """Generate fresh 3D world files"""
    print("🔄 Generating fresh 3D worlds...")
    generator_script = Path(__file__).parent / "scripts" / "generate_3d_world.py"
    
    try:
        subprocess.run([
            sys.executable, 
            str(generator_script), 
            "--data-dir", "data/processed",
            "--output-dir", "generated_worlds",
            "--format", "all"
        ], check=True)
        print("✅ Successfully generated new 3D worlds!")
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to generate worlds: {e}")

def show_stats():
    """Show statistics about the cosmic data"""
    print("📊 Cosmic Data Statistics")
    print("=" * 50)
    
    data_dir = Path(__file__).parent / "data" / "processed"
    cosmic_file = data_dir / "cosmic_world.json"
    
    if cosmic_file.exists():
        import json
        with open(cosmic_file, 'r') as f:
            data = json.load(f)
        
        metadata = data.get('metadata', {})
        stars = data.get('stars', {}).get('catalog', [])
        
        print(f"Total Objects: {metadata.get('total_objects', 0)}")
        print(f"Stellar Objects: {len(stars)}")
        print(f"Data Sources: {', '.join(metadata.get('data_sources', []))}")
        print(f"Created: {metadata.get('created_at', 'Unknown')}")
        
        # Star type distribution
        star_types = {}
        for star in stars:
            star_type = star.get('star_type', 'Unknown')
            star_types[star_type] = star_types.get(star_type, 0) + 1
        
        print("\nStellar Type Distribution:")
        for star_type, count in sorted(star_types.items(), key=lambda x: x[1], reverse=True):
            print(f"  {star_type}: {count}")
        
    else:
        print("❌ Cosmic data not found. Run data processing first.")

def main():
    parser = argparse.ArgumentParser(description="Launch 3D Cosmic Worlds")
    parser.add_argument("mode", nargs='?', default="menu", 
                       choices=["desktop", "web", "generate", "stats", "menu"],
                       help="Launch mode")
    
    args = parser.parse_args()
    
    if args.mode == "menu":
        print("🌌 Enhanced Cosmic World Launcher")
        print("=" * 40)
        print("1. 🖥️  Launch Desktop App (Ursina)")
        print("2. 🌐 Launch Web Portal (Three.js)")
        print("3. 🔄 Generate New Worlds")
        print("4. 📊 Show Data Statistics")
        print("5. ❌ Exit")
        print("=" * 40)
        
        while True:
            try:
                choice = input("Enter your choice (1-5): ").strip()
                
                if choice == '1':
                    launch_desktop_app()
                    break
                elif choice == '2':
                    launch_web_portal()
                    break
                elif choice == '3':
                    generate_new_worlds()
                    break
                elif choice == '4':
                    show_stats()
                    break
                elif choice == '5':
                    print("👋 Goodbye!")
                    break
                else:
                    print("❌ Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
                
    elif args.mode == "desktop":
        launch_desktop_app()
    elif args.mode == "web":
        launch_web_portal()
    elif args.mode == "generate":
        generate_new_worlds()
    elif args.mode == "stats":
        show_stats()

if __name__ == "__main__":
    main()
