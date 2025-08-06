#!/usr/bin/env python3
"""
Enhanced 3D Cosmos World Generator

This script generates immersive 3D worlds from processed cosmic data.
Supports multiple output formats and rendering engines.
"""

import json
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import argparse
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CosmicWorldGenerator:
    """Enhanced 3D world generator for cosmic data visualization"""
    
    def __init__(self, data_dir: Path):
        self.data_dir = Path(data_dir)
        self.cosmic_data = None
        self.stars_df = None
        self.exoplanets_df = None
        self.solar_system_df = None
        self.messier_df = None
        
    def load_data(self):
        """Load all processed cosmic data"""
        logger.info("Loading cosmic data...")
        
        # Load main cosmic world JSON
        cosmic_file = self.data_dir / "cosmic_world.json"
        if cosmic_file.exists():
            with open(cosmic_file, 'r') as f:
                self.cosmic_data = json.load(f)
            logger.info(f"Loaded {len(self.cosmic_data['stars']['catalog'])} stellar objects")
        
        # Load individual dataframes
        data_files = {
            'stars': 'gaia_host_stars_cleaned.parquet',
            'exoplanets': 'exoplanets_cleaned.parquet', 
            'solar_system': 'solar_system_cleaned.parquet',
            'messier': 'messier_catalog_cleaned.parquet'
        }
        
        for name, filename in data_files.items():
            file_path = self.data_dir / filename
            if file_path.exists():
                setattr(self, f"{name}_df", pd.read_parquet(file_path))
                logger.info(f"Loaded {len(getattr(self, f'{name}_df'))} {name} objects")
    
    def calculate_scale_factors(self) -> Dict[str, float]:
        """Calculate appropriate scale factors for different object types"""
        if not self.cosmic_data:
            return {"star": 1.0, "planet": 0.5, "galaxy": 2.0}
            
        stars = self.cosmic_data['stars']['catalog']
        distances = [star.get('distance_ly', 100) for star in stars]
        
        # Scale factors based on distance distribution
        max_distance = max(distances)
        min_distance = min(distances)
        
        return {
            "star": max(0.1, min(2.0, 100 / np.sqrt(max_distance))),
            "planet": 0.3,
            "galaxy": 3.0,
            "nebula": 5.0,
            "solar_system": 0.8
        }
    
    def get_star_color(self, star: Dict) -> Tuple[float, float, float]:
        """Determine star color based on stellar type and temperature"""
        star_type = star.get('star_type', 'Unknown')
        temp = star.get('teff_gspphot', 5500)  # Default to sun-like temperature
        
        # Color mapping based on stellar type and temperature
        type_colors = {
            'O-type': (0.6, 0.7, 1.0),    # Blue
            'B-type': (0.8, 0.9, 1.0),    # Blue-white
            'A-type': (1.0, 1.0, 1.0),    # White
            'F-type': (1.0, 1.0, 0.9),    # Yellow-white
            'G-type': (1.0, 1.0, 0.7),    # Yellow (Sun-like)
            'K-type': (1.0, 0.8, 0.6),    # Orange
            'M-type': (1.0, 0.6, 0.4),    # Red
        }
        
        # Use stellar type if available
        if star_type in type_colors:
            return type_colors[star_type]
        
        # Fall back to temperature-based coloring
        if temp > 7500:
            return (0.8, 0.9, 1.0)  # Blue-white
        elif temp > 6000:
            return (1.0, 1.0, 0.9)  # White-yellow
        elif temp > 5200:
            return (1.0, 1.0, 0.7)  # Yellow
        elif temp > 3700:
            return (1.0, 0.8, 0.6)  # Orange
        else:
            return (1.0, 0.6, 0.4)  # Red
    
    def generate_ursina_world(self, output_file: Path):
        """Generate enhanced Ursina 3D world script"""
        logger.info("Generating enhanced Ursina 3D world...")
        
        scale_factors = self.calculate_scale_factors()
        
        ursina_code = f'''#!/usr/bin/env python3
"""
Enhanced 3D Cosmic Explorer using Ursina
Generated from processed cosmic data
"""

from ursina import *
import json
import pandas as pd
import numpy as np
from pathlib import Path

class EnhancedCosmicExplorer(Entity):
    def __init__(self):
        super().__init__()
        
        # Setup scene
        app = Ursina()
        window.title = "Enhanced Cosmic Explorer"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Load cosmic data
        self.load_cosmic_data()
        
        # Create starfield background
        self.create_starfield()
        
        # Create main cosmic objects
        self.create_stars()
        self.create_planets()
        self.create_galaxies()
        
        # Setup camera and controls
        self.setup_camera()
        self.setup_ui()
        
        # Start exploration
        app.run()
    
    def load_cosmic_data(self):
        """Load processed cosmic data"""
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        
        # Load main cosmic world data
        cosmic_file = data_dir / "cosmic_world.json"
        if cosmic_file.exists():
            with open(cosmic_file, 'r') as f:
                self.cosmic_data = json.load(f)
        else:
            self.cosmic_data = {{"stars": {{"catalog": []}}, "metadata": {{"total_objects": 0}}}}
        
        print(f"Loaded cosmic data with {{len(self.cosmic_data['stars']['catalog'])}} objects")
    
    def create_starfield(self):
        """Create beautiful starfield background"""
        # Create distant background stars
        for i in range(1000):
            star = Entity(
                model='sphere',
                scale=random.uniform(0.01, 0.03),
                position=(
                    random.uniform(-500, 500),
                    random.uniform(-500, 500), 
                    random.uniform(-500, 500)
                ),
                color=color.white * random.uniform(0.7, 1.0)
            )
    
    def create_stars(self):
        """Create main catalog stars with realistic properties"""
        stars = self.cosmic_data.get('stars', {{}}).get('catalog', [])
        
        for i, star_data in enumerate(stars[:200]):  # Limit for performance
            # Get position (already in light years, scaled down)
            pos_x = star_data.get('x', 0) * {scale_factors["star"]}
            pos_y = star_data.get('y', 0) * {scale_factors["star"]}  
            pos_z = star_data.get('z', 0) * {scale_factors["star"]}
            
            # Determine star properties
            distance = star_data.get('distance_ly', 100)
            magnitude = star_data.get('phot_g_mean_mag', 10)
            star_type = star_data.get('star_type', 'Unknown')
            display_name = star_data.get('display_name', f'Star {{i+1}}')
            
            # Calculate star size based on magnitude (brighter = larger)
            star_size = max(0.1, min(2.0, (15 - magnitude) * 0.1))
            
            # Get star color
            star_color = self.get_star_color(star_data)
            
            # Create star entity
            star = Entity(
                model='sphere',
                scale=star_size,
                position=(pos_x, pos_y, pos_z),
                color=color.rgb(*star_color),
                always_on_top=False
            )
            
            # Add glow effect for bright stars
            if magnitude < 8:
                glow = Entity(
                    model='sphere',
                    scale=star_size * 2,
                    position=(pos_x, pos_y, pos_z),
                    color=color.rgb(*star_color) * 0.3,
                    alpha=0.3
                )
            
            # Store metadata for interaction
            star.star_data = star_data
            star.display_name = display_name
    
    def get_star_color(self, star_data):
        """Get star color based on type and temperature"""
        star_type = star_data.get('star_type', 'Unknown')
        temp = star_data.get('teff_gspphot', 5500)
        
        type_colors = {{
            'O-type': (0.6, 0.7, 1.0),
            'B-type': (0.8, 0.9, 1.0), 
            'A-type': (1.0, 1.0, 1.0),
            'F-type': (1.0, 1.0, 0.9),
            'G-type': (1.0, 1.0, 0.7),
            'K-type': (1.0, 0.8, 0.6),
            'M-type': (1.0, 0.6, 0.4),
        }}
        
        return type_colors.get(star_type, (1.0, 1.0, 0.8))
    
    def create_planets(self):
        """Create exoplanets around their host stars"""
        # This would be populated from exoplanet data
        print("Creating exoplanet systems...")
        pass
    
    def create_galaxies(self):
        """Create distant galaxies and nebulae"""
        # This would be populated from Messier catalog
        print("Creating distant galaxies and nebulae...")
        pass
    
    def setup_camera(self):
        """Setup camera controls for exploration"""
        # First-person camera for exploration
        camera.position = (0, 0, -10)
        camera.rotation_x = 0
        
        # Enable WASD movement
        self.speed = 5
        
        def update():
            # Camera movement
            if held_keys['w']:
                camera.position += camera.forward * self.speed * time.dt
            if held_keys['s']:
                camera.position -= camera.forward * self.speed * time.dt
            if held_keys['a']:
                camera.position -= camera.right * self.speed * time.dt
            if held_keys['d']:
                camera.position += camera.right * self.speed * time.dt
            if held_keys['space']:
                camera.position += camera.up * self.speed * time.dt
            if held_keys['shift']:
                camera.position -= camera.up * self.speed * time.dt
                
            # Speed control
            if held_keys['q']:
                self.speed = min(50, self.speed * 1.1)
            if held_keys['e']:
                self.speed = max(0.1, self.speed * 0.9)
        
        self.update = update
    
    def setup_ui(self):
        """Setup user interface"""
        # Instructions
        instructions = Text(
            "Controls: WASD to move, Mouse to look, Space/Shift for up/down\\n"
            "Q/E to change speed, ESC to exit",
            position=(-0.8, 0.4),
            scale=1
        )
        
        # Position indicator
        self.position_text = Text(
            "Position: (0, 0, 0)",
            position=(-0.8, 0.35),
            scale=0.8
        )
        
        def update_ui():
            pos = camera.position
            self.position_text.text = f"Position: ({{pos.x:.1f}}, {{pos.y:.1f}}, {{pos.z:.1f}})"
        
        # Update UI every frame
        invoke(update_ui, delay=0.1, repeats=True)

if __name__ == '__main__':
    explorer = EnhancedCosmicExplorer()
'''
        
        with open(output_file, 'w') as f:
            f.write(ursina_code)
        
        logger.info(f"Generated Ursina world script: {output_file}")
    
    def generate_threejs_world(self, output_file: Path):
        """Generate enhanced Three.js React component"""
        logger.info("Generating enhanced Three.js world...")
        
        # First, create the data file for the web app
        web_data = self.prepare_web_data()
        data_file = output_file.parent / "cosmicData.json"
        with open(data_file, 'w') as f:
            json.dump(web_data, f, indent=2)
        
        threejs_code = '''import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import cosmicData from './cosmicData.json';

export default function EnhancedUniverseViewer() {
  const mountRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const [selectedObject, setSelectedObject] = useState(null);
  const [cameraSpeed, setCameraSpeed] = useState(1);

  useEffect(() => {
    if (!mountRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x000011);
    sceneRef.current = scene;

    // Camera setup
    const camera = new THREE.PerspectiveCamera(
      75,
      window.innerWidth / window.innerHeight,
      0.1,
      10000
    );
    camera.position.set(0, 0, 50);
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    mountRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // Create starfield background
    createStarfield(scene);

    // Create main cosmic objects
    createStars(scene);
    createPlanets(scene);

    // Controls
    const keys = {};
    let mouseX = 0;
    let mouseY = 0;

    // Event listeners
    const handleKeyDown = (event) => {
      keys[event.code] = true;
    };

    const handleKeyUp = (event) => {
      keys[event.code] = false;
    };

    const handleMouseMove = (event) => {
      mouseX = (event.clientX - window.innerWidth / 2) * 0.001;
      mouseY = (event.clientY - window.innerHeight / 2) * 0.001;
    };

    document.addEventListener('keydown', handleKeyDown);
    document.addEventListener('keyup', handleKeyUp);
    document.addEventListener('mousemove', handleMouseMove);

    // Animation loop
    const animate = () => {
      requestAnimationFrame(animate);

      // Camera movement
      const speed = cameraSpeed;
      if (keys['KeyW']) {
        camera.position.add(
          new THREE.Vector3(0, 0, -speed).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyS']) {
        camera.position.add(
          new THREE.Vector3(0, 0, speed).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyA']) {
        camera.position.add(
          new THREE.Vector3(-speed, 0, 0).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['KeyD']) {
        camera.position.add(
          new THREE.Vector3(speed, 0, 0).applyQuaternion(camera.quaternion)
        );
      }
      if (keys['Space']) {
        camera.position.y += speed;
      }
      if (keys['ShiftLeft']) {
        camera.position.y -= speed;
      }

      // Mouse look
      camera.rotation.y = -mouseX;
      camera.rotation.x = -mouseY;

      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      document.removeEventListener('keydown', handleKeyDown);
      document.removeEventListener('keyup', handleKeyUp);
      document.removeEventListener('mousemove', handleMouseMove);
      
      if (mountRef.current && renderer.domElement) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, [cameraSpeed]);

  // Create starfield background
  const createStarfield = (scene) => {
    const starGeometry = new THREE.BufferGeometry();
    const starMaterial = new THREE.PointsMaterial({
      color: 0xffffff,
      size: 0.1,
      sizeAttenuation: false
    });

    const starVertices = [];
    for (let i = 0; i < 10000; i++) {
      const x = (Math.random() - 0.5) * 2000;
      const y = (Math.random() - 0.5) * 2000;
      const z = (Math.random() - 0.5) * 2000;
      starVertices.push(x, y, z);
    }

    starGeometry.setAttribute('position', new THREE.Float32BufferAttribute(starVertices, 3));
    const stars = new THREE.Points(starGeometry, starMaterial);
    scene.add(stars);
  };

  // Create main catalog stars
  const createStars = (scene) => {
    cosmicData.stars.forEach((starData, index) => {
      const geometry = new THREE.SphereGeometry(starData.size, 16, 16);
      const material = new THREE.MeshBasicMaterial({
        color: new THREE.Color(starData.color.r, starData.color.g, starData.color.b)
      });

      const star = new THREE.Mesh(geometry, material);
      star.position.set(starData.position.x, starData.position.y, starData.position.z);

      // Add glow effect for bright stars
      if (starData.magnitude < 8) {
        const glowGeometry = new THREE.SphereGeometry(starData.size * 2, 16, 16);
        const glowMaterial = new THREE.MeshBasicMaterial({
          color: new THREE.Color(starData.color.r, starData.color.g, starData.color.b),
          transparent: true,
          opacity: 0.3
        });
        const glow = new THREE.Mesh(glowGeometry, glowMaterial);
        glow.position.copy(star.position);
        scene.add(glow);
      }

      // Store metadata for interaction
      star.userData = starData;
      scene.add(star);
    });
  };

  // Create exoplanets (placeholder)
  const createPlanets = (scene) => {
    // This would be populated with actual exoplanet data
    console.log('Creating exoplanet systems...');
  };

  return (
    <div style={{ position: 'relative', width: '100vw', height: '100vh' }}>
      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />
      
      {/* UI Overlay */}
      <div style={{
        position: 'absolute',
        top: 20,
        left: 20,
        color: 'white',
        fontFamily: 'monospace',
        background: 'rgba(0,0,0,0.7)',
        padding: '10px',
        borderRadius: '5px'
      }}>
        <div>Controls: WASD to move, Mouse to look</div>
        <div>Space/Shift for up/down</div>
        <div>Speed: 
          <input 
            type="range" 
            min="0.1" 
            max="10" 
            step="0.1"
            value={cameraSpeed}
            onChange={(e) => setCameraSpeed(parseFloat(e.target.value))}
            style={{ marginLeft: '10px' }}
          />
          {cameraSpeed.toFixed(1)}
        </div>
        {selectedObject && (
          <div style={{ marginTop: '10px', borderTop: '1px solid white', paddingTop: '10px' }}>
            <strong>{selectedObject.display_name}</strong><br/>
            Type: {selectedObject.star_type}<br/>
            Distance: {selectedObject.distance_ly?.toFixed(1)} ly
          </div>
        )}
      </div>
    </div>
  );
}'''

        with open(output_file, 'w') as f:
            f.write(threejs_code)
        
        logger.info(f"Generated Three.js component: {output_file}")
        logger.info(f"Generated cosmic data: {data_file}")
    
    def prepare_web_data(self) -> Dict:
        """Prepare cosmic data for web visualization"""
        if not self.cosmic_data:
            return {"stars": [], "planets": [], "metadata": {"total_objects": 0}}
        
        stars = self.cosmic_data.get('stars', {}).get('catalog', [])
        scale_factors = self.calculate_scale_factors()
        
        web_stars = []
        for star_data in stars[:500]:  # Limit for web performance
            # Get star color
            star_color = self.get_star_color(star_data)
            
            # Calculate size based on magnitude
            magnitude = star_data.get('phot_g_mean_mag', 10)
            star_size = max(0.1, min(2.0, (15 - magnitude) * 0.1))
            
            web_star = {
                "position": {
                    "x": star_data.get('x', 0) * scale_factors["star"],
                    "y": star_data.get('y', 0) * scale_factors["star"],
                    "z": star_data.get('z', 0) * scale_factors["star"]
                },
                "color": {
                    "r": star_color[0],
                    "g": star_color[1], 
                    "b": star_color[2]
                },
                "size": star_size,
                "magnitude": magnitude,
                "display_name": star_data.get('display_name', 'Unknown Star'),
                "star_type": star_data.get('star_type', 'Unknown'),
                "distance_ly": star_data.get('distance_ly', 0),
                "temperature": star_data.get('teff_gspphot', 5500)
            }
            web_stars.append(web_star)
        
        return {
            "stars": web_stars,
            "planets": [],  # To be populated with exoplanet data
            "metadata": {
                "total_stars": len(web_stars),
                "total_objects": len(web_stars)
            }
        }
    
    def generate_unity_data(self, output_file: Path):
        """Generate data file for Unity 3D world"""
        logger.info("Generating Unity data file...")
        
        unity_data = {
            "worldSettings": {
                "scale": 1.0,
                "lightYearScale": 0.1,
                "maxRenderDistance": 1000
            },
            "stellarObjects": [],
            "exoplanets": [],
            "galaxies": []
        }
        
        # Process stellar objects
        if self.cosmic_data:
            stars = self.cosmic_data.get('stars', {}).get('catalog', [])
            scale_factors = self.calculate_scale_factors()
            
            for star_data in stars:
                star_color = self.get_star_color(star_data)
                magnitude = star_data.get('phot_g_mean_mag', 10)
                
                unity_star = {
                    "name": star_data.get('display_name', 'Unknown Star'),
                    "position": [
                        star_data.get('x', 0) * scale_factors["star"],
                        star_data.get('y', 0) * scale_factors["star"],
                        star_data.get('z', 0) * scale_factors["star"]
                    ],
                    "color": list(star_color),
                    "magnitude": magnitude,
                    "size": max(0.1, min(2.0, (15 - magnitude) * 0.1)),
                    "temperature": star_data.get('teff_gspphot', 5500),
                    "stellarType": star_data.get('star_type', 'Unknown'),
                    "distance": star_data.get('distance_ly', 0)
                }
                unity_data["stellarObjects"].append(unity_star)
        
        with open(output_file, 'w') as f:
            json.dump(unity_data, f, indent=2)
        
        logger.info(f"Generated Unity data file: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate 3D worlds from cosmic data")
    parser.add_argument("--data-dir", default="data/processed", help="Processed data directory")
    parser.add_argument("--output-dir", default="generated_worlds", help="Output directory")
    parser.add_argument("--format", choices=["ursina", "threejs", "unity", "all"], 
                       default="all", help="Output format")
    
    args = parser.parse_args()
    
    # Setup paths
    data_dir = Path(args.data_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    
    # Initialize generator
    generator = CosmicWorldGenerator(data_dir)
    generator.load_data()
    
    # Generate requested formats
    if args.format in ["ursina", "all"]:
        generator.generate_ursina_world(output_dir / "enhanced_cosmic_explorer.py")
    
    if args.format in ["threejs", "all"]:
        generator.generate_threejs_world(output_dir / "EnhancedUniverseViewer.jsx")
    
    if args.format in ["unity", "all"]:
        generator.generate_unity_data(output_dir / "cosmic_world_unity.json")
    
    logger.info("3D world generation complete!")

if __name__ == "__main__":
    main()
