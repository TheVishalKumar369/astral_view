#!/usr/bin/env python3
"""
Simple 3D Cosmic Explorer - Stable Version
Fixed visibility and control issues
"""

from ursina import *
import json
import math
from pathlib import Path

# Global variables
app = None
explorer = None

class SimpleCosmicExplorer:
    def __init__(self):
        global app, explorer
        explorer = self
        
        # Setup scene
        app = Ursina()
        window.title = "3D Cosmic Explorer - Navigate Space"
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Set better background color (dark blue instead of black)
        camera.clear_color = color.rgb(0.02, 0.02, 0.15)
        
        # Initialize properties
        self.speed = 8
        self.selected_object = None
        self.objects = []
        self.proximity_threshold = 3.0
        self.nearby_objects = []
        
        # Camera setup
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        
        # Load data and create objects
        self.load_data()
        self.create_visible_objects()
        self.setup_ui()
        
        # Movement variables
        self.mouse_sensitivity = 50
        
        # Start app
        app.run()
    
    def load_data(self):
        """Load cosmic data"""
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        cosmic_file = data_dir / "cosmic_world.json"
        
        if cosmic_file.exists():
            with open(cosmic_file, 'r') as f:
                self.cosmic_data = json.load(f)
        else:
            self.cosmic_data = {"stars": {"catalog": []}, "metadata": {"total_objects": 0}}
        
        print(f"Loaded {len(self.cosmic_data['stars']['catalog'])} cosmic objects")
    
    def create_visible_objects(self):
        """Create clearly visible 3D objects"""
        # First create large, colorful test objects near origin
        test_objects = [
            {'pos': (0, 0, 20), 'color': color.red, 'scale': 5, 'name': 'Red Giant Star', 'type': 'star'},
            {'pos': (15, 0, 15), 'color': color.blue, 'scale': 4, 'name': 'Blue Supergiant', 'type': 'star'},
            {'pos': (-15, 0, 15), 'color': color.yellow, 'scale': 4.5, 'name': 'Yellow Sun-like Star', 'type': 'star'},
            {'pos': (0, 15, 20), 'color': color.green, 'scale': 3, 'name': 'Green Alien Star', 'type': 'star'},
            {'pos': (0, -15, 20), 'color': color.orange, 'scale': 4, 'name': 'Orange Giant', 'type': 'star'},
            {'pos': (10, 10, 12), 'color': color.white, 'scale': 2.5, 'name': 'White Dwarf', 'type': 'star'},
            {'pos': (-10, -10, 12), 'color': color.cyan, 'scale': 3.5, 'name': 'Cyan Hot Star', 'type': 'star'},
            {'pos': (8, 0, 25), 'color': color.rgb(0.3, 0.7, 1.0), 'scale': 1.5, 'name': 'Kepler-442b (Exoplanet)', 'type': 'exoplanet'},
            {'pos': (-8, 0, 25), 'color': color.rgb(0.4, 0.9, 0.8), 'scale': 1.2, 'name': 'TRAPPIST-1e (Exoplanet)', 'type': 'exoplanet'},
            {'pos': (0, 8, 30), 'color': color.violet, 'scale': 6, 'name': 'Andromeda Galaxy (M31)', 'type': 'galaxy'},
            {'pos': (0, -8, 30), 'color': color.pink, 'scale': 5, 'name': 'Orion Nebula (M42)', 'type': 'nebula'}
        ]
        
        # Create test objects
        for obj in test_objects:
            entity = Entity(
                model='sphere',
                scale=obj['scale'],
                position=obj['pos'],
                color=obj['color']
            )
            
            # Add bright glow effect
            glow = Entity(
                model='sphere',
                scale=obj['scale'] * 1.4,
                position=obj['pos'],
                color=Color(obj['color'].r, obj['color'].g, obj['color'].b, 0.3)
            )
            
            entity.object_data = {
                'name': obj['name'],
                'type': obj['type'],
                'distance': math.sqrt(obj['pos'][0]**2 + obj['pos'][1]**2 + obj['pos'][2]**2),
                'temperature': 5000 + obj['scale'] * 1000,
                'classification': obj['type'].upper()
            }
            
            self.objects.append(entity)
        
        # Add some real data objects (smaller, further away)
        stars = self.cosmic_data.get('stars', {}).get('catalog', [])
        for i, star_data in enumerate(stars[:50]):  # Limited number
            pos_x = star_data.get('x', 0) * 0.1  # Scaled for visibility
            pos_y = star_data.get('y', 0) * 0.1  
            pos_z = star_data.get('z', 0) * 0.1 + 50  # Push further away
            
            star = Entity(
                model='sphere',
                scale=max(0.5, min(2.0, random.uniform(0.8, 2.0))),
                position=(pos_x, pos_y, pos_z),
                color=self.get_star_color(star_data.get('star_type', 'Unknown'))
            )
            
            star.object_data = {
                'name': star_data.get('display_name', f'Distant Star {i+1}'),
                'type': 'star',
                'distance': star_data.get('distance_ly', 1000),
                'temperature': star_data.get('teff_gspphot', 5000),
                'classification': star_data.get('star_type', 'Unknown')
            }
            
            self.objects.append(star)
        
        print(f"Created {len(self.objects)} visible objects")
    
    def get_star_color(self, star_type):
        """Get color based on star type"""
        colors = {
            'O-type': color.blue,
            'B-type': color.cyan,
            'A-type': color.white,
            'F-type': color.yellow,
            'G-type': color.orange,
            'K-type': color.red,
            'M-type': color.dark_gray
        }
        return colors.get(star_type, color.white)
    
    def setup_ui(self):
        """Setup user interface"""
        # Control instructions
        self.instructions = Text(
            "3D COSMIC EXPLORER\\n" +
            "\\nCONTROLS:\\n" +
            "WASD: Move around\\n" +
            "Mouse: Look around\\n" +
            "Q/E: Move Up/Down\\n" +
            "Shift: Move faster\\n" +
            "R: Reset to origin\\n" +
            "TAB: Toggle mouse lock\\n" +
            "ESC: Exit\\n" +
            "\\nApproach objects to see info!",
            position=(-0.8, 0.4),
            scale=0.6,
            color=color.white,
            parent=camera.ui
        )
        
        # Position display
        self.position_text = Text(
            "Position: (0, 0, 0)",
            position=(-0.8, -0.2),
            scale=0.7,
            color=color.cyan,
            parent=camera.ui
        )
        
        # Speed display
        self.speed_text = Text(
            f"Speed: {self.speed}",
            position=(-0.8, -0.3),
            scale=0.7,
            color=color.yellow,
            parent=camera.ui
        )
        
        # Object info display
        self.object_info = Text(
            "Move close to objects to see details",
            position=(-0.8, -0.5),
            scale=0.6,
            color=color.lime,
            parent=camera.ui
        )
    
    def update(self):
        """Main update loop"""
        # Movement controls
        move_speed = self.speed * time.dt
        if held_keys['shift']:
            move_speed *= 3
        
        if held_keys['w']:
            camera.position += camera.forward * move_speed
        if held_keys['s']:
            camera.position -= camera.forward * move_speed
        if held_keys['a']:
            camera.position -= camera.right * move_speed
        if held_keys['d']:
            camera.position += camera.right * move_speed
        if held_keys['q']:
            camera.position += camera.up * move_speed
        if held_keys['e']:
            camera.position -= camera.up * move_speed
        
        # Mouse look
        if mouse.locked:
            camera.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
            camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity
            camera.rotation_x = max(-90, min(90, camera.rotation_x))
        
        # Update UI
        pos = camera.position
        self.position_text.text = f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})"
        self.speed_text.text = f"Speed: {self.speed}"
        
        # Check for nearby objects
        self.check_nearby_objects()
    
    def check_nearby_objects(self):
        """Check for objects near camera"""
        cam_pos = camera.position
        self.nearby_objects = []
        
        for obj in self.objects:
            if not hasattr(obj, 'object_data'):
                continue
                
            distance = math.sqrt(
                (obj.position.x - cam_pos.x) ** 2 +
                (obj.position.y - cam_pos.y) ** 2 +
                (obj.position.z - cam_pos.z) ** 2
            )
            
            if distance <= self.proximity_threshold:
                self.nearby_objects.append({
                    'entity': obj,
                    'distance': distance,
                    'data': obj.object_data
                })
        
        # Sort by distance
        self.nearby_objects.sort(key=lambda x: x['distance'])
        
        # Update display
        if self.nearby_objects:
            closest = self.nearby_objects[0]
            data = closest['data']
            
            info = f"NEARBY OBJECT:\\n"
            info += f"Name: {data['name']}\\n"
            info += f"Type: {data['classification']}\\n"
            info += f"Distance: {closest['distance']:.1f} units\\n"
            
            if 'temperature' in data:
                info += f"Temperature: {data['temperature']:.0f}K\\n"
            if 'distance' in data and data['distance'] != closest['distance']:
                info += f"Real Distance: {data['distance']} ly"
            
            self.object_info.text = info
            self.object_info.color = color.lime
        else:
            self.object_info.text = "Move close to objects to see details"
            self.object_info.color = color.gray

# Global input function
def input(key):
    global explorer
    if not explorer:
        return
    
    if key == 'escape':
        application.quit()
    elif key == 'r':
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
    elif key == 'tab':
        mouse.locked = not mouse.locked
        print(f"Mouse {'locked' if mouse.locked else 'unlocked'}")

if __name__ == '__main__':
    # Start with mouse unlocked so you can see cursor initially
    mouse.locked = False
    explorer = SimpleCosmicExplorer()
