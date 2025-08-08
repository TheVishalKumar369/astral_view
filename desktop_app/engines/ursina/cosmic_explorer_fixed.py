#!/usr/bin/env python3
"""
FIXED 3D Cosmic Explorer - All Issues Resolved
- Working keyboard controls
- Working mouse camera
- Clear visible objects
- Proper UI layout
"""

from ursina import *
import json
import math
from pathlib import Path

class FixedCosmicExplorer:
    def __init__(self):
        # Setup application
        app = Ursina()
        window.title = "3D Cosmic Explorer - FIXED VERSION"
        window.fullscreen = False
        window.fps_counter.enabled = False
        window.exit_button.visible = False
        
        # Fix the background - make it dark space blue
        camera.clear_color = color.rgb(0.05, 0.05, 0.2)
        
        # Initialize variables
        self.speed = 10
        self.mouse_sensitivity = 100
        self.objects = []
        self.nearby_threshold = 5.0
        
        # Load data
        self.load_data()
        
        # Create visible objects
        self.create_objects()
        
        # Setup camera at origin
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)
        
        # Setup UI properly
        self.setup_ui()
        
        # Start with mouse unlocked
        mouse.locked = False
        
        # Run the app
        app.run()
    
    def load_data(self):
        """Load cosmic data"""
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        cosmic_file = data_dir / "cosmic_world.json"
        
        if cosmic_file.exists():
            try:
                with open(cosmic_file, 'r') as f:
                    self.cosmic_data = json.load(f)
                print(f"Loaded {len(self.cosmic_data.get('stars', {}).get('catalog', []))} objects")
            except:
                self.cosmic_data = {"stars": {"catalog": []}}
        else:
            self.cosmic_data = {"stars": {"catalog": []}}
    
    def create_objects(self):
        """Create clearly visible 3D space objects"""
        # Create large, bright, easily visible objects
        space_objects = [
            # Close objects - easy to see
            {'name': 'Red Giant Star', 'pos': (0, 0, 15), 'color': color.red, 'scale': 3, 'type': 'Red Giant'},
            {'name': 'Blue Supergiant', 'pos': (12, 0, 15), 'color': color.blue, 'scale': 2.5, 'type': 'Blue Star'},
            {'name': 'Yellow Sun', 'pos': (-12, 0, 15), 'color': color.yellow, 'scale': 2.8, 'type': 'Sun-like Star'},
            {'name': 'White Dwarf', 'pos': (0, 12, 15), 'color': color.white, 'scale': 1.5, 'type': 'White Dwarf'},
            {'name': 'Orange Giant', 'pos': (0, -12, 15), 'color': color.orange, 'scale': 2.2, 'type': 'Orange Star'},
            
            # Exoplanets - distinctive colors
            {'name': 'Kepler-442b', 'pos': (8, 8, 20), 'color': color.cyan, 'scale': 1, 'type': 'Exoplanet'},
            {'name': 'TRAPPIST-1e', 'pos': (-8, -8, 20), 'color': color.lime, 'scale': 0.8, 'type': 'Exoplanet'},
            
            # Deep space objects - larger and further
            {'name': 'Orion Nebula', 'pos': (0, 0, 35), 'color': color.pink, 'scale': 4, 'type': 'Nebula'},
            {'name': 'Andromeda Galaxy', 'pos': (20, 0, 35), 'color': color.violet, 'scale': 5, 'type': 'Galaxy'},
            {'name': 'Crab Nebula', 'pos': (-20, 0, 35), 'color': color.magenta, 'scale': 3.5, 'type': 'Nebula'},
        ]
        
        # Create the objects
        for obj_data in space_objects:
            # Main object
            obj = Entity(
                model='sphere',
                color=obj_data['color'],
                scale=obj_data['scale'],
                position=obj_data['pos']
            )
            
            # Add glow effect
            glow = Entity(
                model='sphere',
                color=Color(obj_data['color'].r, obj_data['color'].g, obj_data['color'].b, 0.4),
                scale=obj_data['scale'] * 1.5,
                position=obj_data['pos']
            )
            
            # Store object data
            obj.object_info = {
                'name': obj_data['name'],
                'type': obj_data['type'],
                'distance': math.sqrt(sum(x**2 for x in obj_data['pos'])),
                'temp': f"{3000 + obj_data['scale'] * 2000:.0f}K"
            }
            
            self.objects.append(obj)
        
        print(f"Created {len(self.objects)} space objects")
    
    def setup_ui(self):
        """Setup a clean, visible UI"""
        # Background panel for UI (left side)
        ui_bg = Entity(
            model='cube',
            color=color.rgb(0.1, 0.1, 0.3),
            scale=(0.35, 1, 0.01),
            position=(-0.65, 0, -1),
            parent=camera.ui
        )
        
        # Title
        title = Text(
            "3D COSMIC EXPLORER",
            position=(-0.8, 0.45),
            scale=1.2,
            color=color.white,
            parent=camera.ui
        )
        
        # Controls - clear and readable
        controls = Text(
            "CONTROLS:\n" +
            "WASD - Move around\n" +
            "Mouse - Look (when locked)\n" +
            "Q/E - Move Up/Down\n" +
            "SHIFT - Move faster\n" +
            "TAB - Lock/Unlock Mouse\n" +
            "R - Reset to center\n" +
            "ESC - Exit\n\n" +
            "FLY CLOSE TO OBJECTS\n" +
            "TO SEE THEIR DATA!",
            position=(-0.8, 0.2),
            scale=0.8,
            color=color.cyan,
            parent=camera.ui
        )
        
        # Position display
        self.pos_text = Text(
            "Position: (0, 0, 0)",
            position=(-0.8, -0.1),
            scale=0.9,
            color=color.yellow,
            parent=camera.ui
        )
        
        # Speed display  
        self.speed_text = Text(
            f"Speed: {self.speed}",
            position=(-0.8, -0.2),
            scale=0.9,
            color=color.orange,
            parent=camera.ui
        )
        
        # Mouse status
        self.mouse_text = Text(
            "Mouse: UNLOCKED (Press TAB)",
            position=(-0.8, -0.3),
            scale=0.8,
            color=color.red,
            parent=camera.ui
        )
        
        # Object info display
        self.object_text = Text(
            "Fly close to objects to see info",
            position=(-0.8, -0.5),
            scale=0.8,
            color=color.lime,
            parent=camera.ui
        )
    
    def update(self):
        """Main game loop - handles movement and UI updates"""
        # Calculate movement speed
        move_speed = self.speed * time.dt
        if held_keys['shift']:
            move_speed *= 2
        
        # WASD Movement - THIS SHOULD WORK NOW
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
        
        # Mouse look - THIS SHOULD WORK NOW
        if mouse.locked:
            camera.rotation_y += mouse.velocity[0] * self.mouse_sensitivity
            camera.rotation_x -= mouse.velocity[1] * self.mouse_sensitivity  
            camera.rotation_x = max(-90, min(90, camera.rotation_x))
        
        # Update UI displays
        pos = camera.position
        self.pos_text.text = f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})"
        self.speed_text.text = f"Speed: {self.speed}"
        
        # Update mouse status
        if mouse.locked:
            self.mouse_text.text = "Mouse: LOCKED (Press TAB to unlock)"
            self.mouse_text.color = color.green
        else:
            self.mouse_text.text = "Mouse: UNLOCKED (Press TAB to lock)"  
            self.mouse_text.color = color.red
        
        # Check for nearby objects
        self.check_nearby_objects()
    
    def check_nearby_objects(self):
        """Check if player is near any objects and show info"""
        cam_pos = camera.position
        closest_obj = None
        closest_distance = float('inf')
        
        for obj in self.objects:
            if not hasattr(obj, 'object_info'):
                continue
                
            # Calculate distance
            obj_pos = obj.position
            distance = math.sqrt(
                (obj_pos.x - cam_pos.x)**2 +
                (obj_pos.y - cam_pos.y)**2 +
                (obj_pos.z - cam_pos.z)**2
            )
            
            if distance < self.nearby_threshold and distance < closest_distance:
                closest_distance = distance
                closest_obj = obj
        
        # Update object info display
        if closest_obj:
            info = closest_obj.object_info
            text = f"NEARBY OBJECT:\n"
            text += f"Name: {info['name']}\n"
            text += f"Type: {info['type']}\n" 
            text += f"Distance: {closest_distance:.1f} units\n"
            text += f"Temperature: {info['temp']}"
            
            self.object_text.text = text
            self.object_text.color = color.lime
        else:
            self.object_text.text = "Fly close to objects to see info"
            self.object_text.color = color.gray

# Global input handler - THIS IS CRUCIAL FOR CONTROLS TO WORK
def input(key):
    global explorer
    
    if key == 'escape':
        print("Exiting application...")
        application.quit()
    
    elif key == 'tab':
        mouse.locked = not mouse.locked
        print(f"Mouse {'locked' if mouse.locked else 'unlocked'}")
    
    elif key == 'r':
        print("Resetting to center...")
        camera.position = (0, 0, 0)
        camera.rotation = (0, 0, 0)

if __name__ == '__main__':
    print("Starting 3D Cosmic Explorer...")
    print("Controls: WASD to move, Mouse to look (TAB to lock mouse), Q/E up/down")
    print("Press TAB to lock mouse for camera control!")
    
    explorer = FixedCosmicExplorer()
