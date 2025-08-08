#!/usr/bin/env python3
"""
Cosmic Engine Manager - Handles Multiple 3D Engines
Prevents conflicts and manages dependencies between different engines
"""

import os
import sys
import importlib.util
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import json

class EngineManager:
    """Manages different 3D engines and prevents conflicts"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.engines = {
            'ursina_simple': UrsiaSimpleEngine(),
            'ursina_enhanced': UrsiaEnhancedEngine(), 
            'panda3d_advanced': Panda3DAdvancedEngine(),
            'threejs_web': ThreeJSWebEngine()
        }
        self.active_engine = None
        
    def list_engines(self) -> Dict[str, Dict]:
        """List all available engines with their status"""
        engine_info = {}
        
        for engine_id, engine in self.engines.items():
            engine_info[engine_id] = {
                'name': engine.name,
                'description': engine.description,
                'status': engine.check_availability(),
                'dependencies': engine.dependencies,
                'features': engine.features,
                'performance_level': engine.performance_level
            }
            
        return engine_info
    
    def launch_engine(self, engine_id: str, data_path: Optional[str] = None) -> bool:
        """Launch specified engine with proper isolation"""
        if engine_id not in self.engines:
            print(f"Unknown engine: {engine_id}")
            return False
            
        engine = self.engines[engine_id]
        
        # Check if engine is available
        if not engine.check_availability():
            print(f"Engine {engine_id} is not available. Missing dependencies.")
            return False
        
        # Stop any currently active engine
        if self.active_engine:
            self.stop_current_engine()
        
        # Launch new engine
        try:
            success = engine.launch(data_path)
            if success:
                self.active_engine = engine_id
            return success
        except Exception as e:
            print(f"Failed to launch {engine_id}: {e}")
            return False
    
    def stop_current_engine(self) -> bool:
        """Stop the currently active engine"""
        if not self.active_engine:
            return True
            
        try:
            engine = self.engines[self.active_engine]
            engine.stop()
            self.active_engine = None
            return True
        except Exception as e:
            print(f"Error stopping engine: {e}")
            return False
    
    def install_engine_dependencies(self, engine_id: str) -> bool:
        """Install dependencies for specified engine"""
        if engine_id not in self.engines:
            return False
            
        engine = self.engines[engine_id]
        return engine.install_dependencies()

class BaseEngine:
    """Base class for all engines"""
    
    def __init__(self):
        self.name = "Base Engine"
        self.description = "Base engine class"
        self.dependencies = []
        self.features = []
        self.performance_level = "Unknown"
        self.process = None
        
    def check_availability(self) -> str:
        """Check if engine dependencies are available"""
        for dep in self.dependencies:
            if not self._is_package_installed(dep):
                return "Missing Dependencies"
        return "Ready"
    
    def _is_package_installed(self, package_name: str) -> bool:
        """Check if a Python package is installed"""
        try:
            if package_name.startswith('system:'):
                # System dependency check
                return True  # Simplified for now
            else:
                spec = importlib.util.find_spec(package_name)
                return spec is not None
        except:
            return False
    
    def launch(self, data_path: Optional[str] = None) -> bool:
        """Launch the engine"""
        raise NotImplementedError
    
    def stop(self) -> bool:
        """Stop the engine"""
        if self.process and self.process.poll() is None:
            self.process.terminate()
            return True
        return False
    
    def install_dependencies(self) -> bool:
        """Install engine dependencies"""
        pip_packages = [dep for dep in self.dependencies if not dep.startswith('system:')]
        if not pip_packages:
            return True
            
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + pip_packages)
            return True
        except subprocess.CalledProcessError:
            return False

class UrsiaSimpleEngine(BaseEngine):
    """Simple Ursina engine implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Ursina Simple Explorer"
        self.description = "Lightweight 3D exploration with Ursina engine"
        self.dependencies = ['ursina', 'numpy']
        self.features = ['Basic 3D Navigation', 'Simple UI', 'Fast Loading']
        self.performance_level = "High Performance"
    
    def launch(self, data_path: Optional[str] = None) -> bool:
        script_path = Path(__file__).parent / "engines" / "ursina" / "cosmic_explorer_simple.py"
        if not script_path.exists():
            return False
            
        try:
            self.process = subprocess.Popen([sys.executable, str(script_path)])
            return True
        except Exception:
            return False

class UrsiaEnhancedEngine(BaseEngine):
    """Enhanced Ursina engine implementation"""
    
    def __init__(self):
        super().__init__()
        self.name = "Ursina Enhanced Explorer"
        self.description = "Enhanced 3D exploration with improved graphics"
        self.dependencies = ['ursina', 'numpy']
        self.features = ['Enhanced Graphics', 'Better Controls', 'Improved UI', 'More Objects']
        self.performance_level = "High Performance"
    
    def launch(self, data_path: Optional[str] = None) -> bool:
        script_path = Path(__file__).parent / "engines" / "ursina" / "cosmic_explorer_fixed.py"
        if not script_path.exists():
            return False
            
        try:
            self.process = subprocess.Popen([sys.executable, str(script_path)])
            return True
        except Exception:
            return False

class Panda3DAdvancedEngine(BaseEngine):
    """Advanced Panda3D engine with realistic physics"""
    
    def __init__(self):
        super().__init__()
        self.name = "Panda3D Advanced Simulation"
        self.description = "Professional 3D engine with realistic physics and advanced graphics"
        self.dependencies = ['panda3d', 'numpy', 'scipy', 'astropy', 'pybullet', 'pillow']
        self.features = [
            'Photorealistic Graphics', 
            'Real Physics Simulation', 
            'Advanced Lighting',
            'Orbital Mechanics',
            'HDR Rendering',
            'Professional Materials'
        ]
        self.performance_level = "Medium Performance"
    
    def launch(self, data_path: Optional[str] = None) -> bool:
        script_path = Path(__file__).parent / "engines" / "panda3d" / "main.py"
        if not script_path.exists():
            return False
            
        try:
            # Set up environment to prevent conflicts
            env = os.environ.copy()
            env['PANDA3D_ENGINE'] = '1'
            
            self.process = subprocess.Popen([sys.executable, str(script_path)], env=env)
            return True
        except Exception as e:
            print(f"Panda3D launch error: {e}")
            return False

class ThreeJSWebEngine(BaseEngine):
    """Three.js web-based engine"""
    
    def __init__(self):
        super().__init__()
        self.name = "Three.js Web Explorer"
        self.description = "Browser-based 3D exploration"
        self.dependencies = ['system:web_browser']
        self.features = ['Cross-Platform', 'No Installation', 'Web-Based', 'Easy Sharing']
        self.performance_level = "Medium Performance"
    
    def launch(self, data_path: Optional[str] = None) -> bool:
        web_path = Path(__file__).parent.parent / "web_portal" / "index.html"
        if not web_path.exists():
            return False
            
        try:
            import webbrowser
            webbrowser.open(f"file://{web_path.absolute()}")
            return True
        except Exception:
            return False

# Utility functions
def create_engine_isolation_script(engine_name: str, script_content: str) -> Path:
    """Create an isolated script for running engines without conflicts"""
    isolation_dir = Path(__file__).parent / "isolated_engines"
    isolation_dir.mkdir(exist_ok=True)
    
    script_path = isolation_dir / f"{engine_name}_isolated.py"
    
    # Add isolation header
    isolated_content = f'''#!/usr/bin/env python3
"""
Isolated {engine_name} Engine - Prevents conflicts with other engines
Auto-generated script
"""

# Clear any conflicting imports
import sys
modules_to_remove = [mod for mod in sys.modules.keys() if any(conflict in mod for conflict in ['ursina', 'panda3d', 'direct'])]
for mod in modules_to_remove:
    if mod in sys.modules:
        del sys.modules[mod]

# Original script content
{script_content}
'''
    
    with open(script_path, 'w') as f:
        f.write(isolated_content)
        
    return script_path

def run_engine_manager():
    """Interactive engine manager CLI"""
    manager = EngineManager()
    
    print("🚀 COSMIC ENGINE MANAGER 🌌")
    print("=" * 50)
    
    while True:
        print("\nAvailable commands:")
        print("1. List engines")
        print("2. Launch engine") 
        print("3. Stop current engine")
        print("4. Install dependencies")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            engines = manager.list_engines()
            print("\nAvailable Engines:")
            for engine_id, info in engines.items():
                print(f"\n{engine_id}: {info['name']}")
                print(f"  Status: {info['status']}")
                print(f"  Description: {info['description']}")
                print(f"  Performance: {info['performance_level']}")
                print(f"  Features: {', '.join(info['features'])}")
                
        elif choice == '2':
            engine_id = input("Enter engine ID to launch: ").strip()
            if manager.launch_engine(engine_id):
                print(f"Successfully launched {engine_id}")
            else:
                print(f"Failed to launch {engine_id}")
                
        elif choice == '3':
            if manager.stop_current_engine():
                print("Engine stopped successfully")
            else:
                print("No engine running or failed to stop")
                
        elif choice == '4':
            engine_id = input("Enter engine ID to install dependencies for: ").strip()
            if manager.install_engine_dependencies(engine_id):
                print("Dependencies installed successfully")
            else:
                print("Failed to install dependencies")
                
        elif choice == '5':
            print("Goodbye! 🌌")
            break
            
        else:
            print("Invalid choice. Please enter 1-5.")

if __name__ == "__main__":
    run_engine_manager()
