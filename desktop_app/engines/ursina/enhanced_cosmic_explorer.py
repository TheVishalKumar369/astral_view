#!/usr/bin/env python3
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
            self.cosmic_data = {"stars": {"catalog": []}, "metadata": {"total_objects": 0}}
        
        print(f"Loaded cosmic data with {len(self.cosmic_data['stars']['catalog'])} objects")
    
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
        stars = self.cosmic_data.get('stars', {}).get('catalog', [])
        
        for i, star_data in enumerate(stars[:200]):  # Limit for performance
            # Get position (already in light years, scaled down)
            pos_x = star_data.get('x', 0) * 0.5078145949479146
            pos_y = star_data.get('y', 0) * 0.5078145949479146  
            pos_z = star_data.get('z', 0) * 0.5078145949479146
            
            # Determine star properties
            distance = star_data.get('distance_ly', 100)
            magnitude = star_data.get('phot_g_mean_mag', 10)
            star_type = star_data.get('star_type', 'Unknown')
            display_name = star_data.get('display_name', f'Star {i+1}')
            
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
        
        type_colors = {
            'O-type': (0.6, 0.7, 1.0),
            'B-type': (0.8, 0.9, 1.0), 
            'A-type': (1.0, 1.0, 1.0),
            'F-type': (1.0, 1.0, 0.9),
            'G-type': (1.0, 1.0, 0.7),
            'K-type': (1.0, 0.8, 0.6),
            'M-type': (1.0, 0.6, 0.4),
        }
        
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
            "Controls: WASD to move, Mouse to look, Space/Shift for up/down\n"
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
            self.position_text.text = f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})"
        
        # Update UI every frame
        invoke(update_ui, delay=0.1, repeats=True)

if __name__ == '__main__':
    explorer = EnhancedCosmicExplorer()
