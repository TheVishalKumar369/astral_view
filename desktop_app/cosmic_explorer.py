#!/usr/bin/env python3
"""
Enhanced 3D Cosmic Explorer using Ursina
Generated from processed cosmic data
"""

from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
import json
import pandas as pd
import numpy as np
from pathlib import Path
import math

# Global variables for the app and explorer
app = None
explorer = None

class EnhancedCosmicExplorer:
    def __init__(self):
        global app, explorer
        explorer = self
        
        # Setup scene
        app = Ursina()
        window.title = "Enhanced Cosmic Explorer - 3D Space Navigation"
        window.borderless = False
        window.fullscreen = False
        window.exit_button.visible = False
        
        # Load cosmic data
        self.load_cosmic_data()
        
        # Initialize properties
        self.speed = 5
        self.selected_star = None
        self.star_entities = []
        self.proximity_threshold = 2.0  # Distance to show object details
        self.nearby_objects = []
        
        # Enable 3D rendering (use available shaders)
        # Entity.default_shader = basic_lighting_shader  # Will set this per entity
        
        # Set up lighting for better 3D appearance
        self.setup_lighting()
        
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
        # Set a better background color (dark blue instead of black)
        camera.clear_color = color.rgb(0.05, 0.05, 0.2)
        
        # Create distant background stars - brighter and more visible
        for i in range(500):  # Reduced count for performance
            star = Entity(
                model='sphere',
                scale=random.uniform(0.05, 0.15),  # Larger stars
                position=(
                    random.uniform(-200, 200),
                    random.uniform(-200, 200), 
                    random.uniform(-200, 200)
                ),
                color=color.white * random.uniform(0.8, 1.0),  # Brighter
                always_on_top=True
            )
    
    def create_stars(self):
        """Create main catalog stars with realistic properties"""
        stars = self.cosmic_data.get('stars', {}).get('catalog', [])
        
        for i, star_data in enumerate(stars[:200]):  # Limit for performance
            # Get position (already in light years, scaled down)
            pos_x = star_data.get('x', 0) * 0.32238
            pos_y = star_data.get('y', 0) * 0.32238  
            pos_z = star_data.get('z', 0) * 0.32238
            
            # Determine star properties
            distance = star_data.get('distance_ly', 100)
            magnitude = star_data.get('phot_g_mean_mag', 10)
            star_type = star_data.get('star_type', 'Unknown')
            display_name = star_data.get('display_name', f'Star {i+1}')
            
            # Calculate star size based on magnitude (brighter = larger)
            star_size = max(0.2, min(3.0, (15 - magnitude) * 0.15))
            
            # Get star color
            star_color = self.get_star_color(star_data)
            
            # Create star entity with better 3D appearance
            star = Entity(
                model='sphere',
                scale=star_size,
                position=(pos_x, pos_y, pos_z),
                color=color.rgb(*star_color),
                # shader will use default
            )
            
            # Add glow effect for bright stars
            if magnitude < 8:
                glow = Entity(
                    model='sphere',
                    scale=star_size * 1.5,
                    position=(pos_x, pos_y, pos_z),
                    color=Color(*star_color, 0.4),
                    double_sided=True
                )
                glow.always_on_top = True
            
            # Store metadata for interaction
            star.star_data = star_data
            star.display_name = display_name
            star.object_type = 'star'
            
            # Add to star entities list
            self.star_entities.append(star)
    
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
        stars = self.cosmic_data.get('stars', {}).get('catalog', [])
        exoplanet_count = 0
        
        for star_data in stars[:300]:  # Check more stars for planets
            # Look for exoplanets (object_type = "Pl")
            if star_data.get('object_type') == 'Pl':
                # This is an exoplanet entry
                pos_x = star_data.get('x', 0) * 0.32238
                pos_y = star_data.get('y', 0) * 0.32238  
                pos_z = star_data.get('z', 0) * 0.32238
                
                display_name = star_data.get('display_name', f'Exoplanet {exoplanet_count+1}')
                
                # Create planet entity (smaller than stars)
                planet = Entity(
                    model='sphere',
                    scale=0.3,  # Smaller than stars
                    position=(pos_x, pos_y, pos_z),
                    color=color.rgb(0.3, 0.8, 1.0)  # Distinctive blue color for planets
                )
                
                # Add planet glow
                glow = Entity(
                    model='sphere',
                    scale=0.4,
                    position=(pos_x, pos_y, pos_z),
                    color=Color(0.3, 0.8, 1.0, 0.3)
                )
                
                # Store metadata for interaction
                planet.star_data = star_data
                planet.display_name = display_name
                planet.object_type = 'exoplanet'
                
                self.star_entities.append(planet)
                exoplanet_count += 1
        
        print(f"Created {exoplanet_count} exoplanets")
    
    def create_galaxies(self):
        """Create distant galaxies and nebulae"""
        # Load Messier catalog for deep space objects
        data_dir = Path(__file__).parent.parent / "data" / "processed"
        messier_file = data_dir / "messier_catalog.csv"
        
        galaxy_count = 0
        if messier_file.exists():
            try:
                import pandas as pd
                messier_df = pd.read_csv(messier_file)
                
                for _, obj in messier_df.iterrows():
                    # Place Messier objects at distant locations
                    # Use a scaled position based on their catalog number
                    angle = (obj.get('M', 1) * 2.5) % (2 * 3.14159)
                    distance = 100 + obj.get('M', 1) * 5  # Far away
                    
                    pos_x = distance * math.cos(angle)
                    pos_y = obj.get('M', 1) * 2 - 50  # Vary height
                    pos_z = distance * math.sin(angle)
                    
                    # Different colors for different object types
                    obj_type = str(obj.get('Type', 'Unknown')).lower()
                    if 'galaxy' in obj_type:
                        obj_color = color.violet
                        obj_scale = 3.0
                    elif 'nebula' in obj_type:
                        obj_color = color.pink
                        obj_scale = 4.0
                    elif 'cluster' in obj_type:
                        obj_color = color.orange
                        obj_scale = 2.5
                    else:
                        obj_color = color.lime
                        obj_scale = 2.0
                    
                    # Create distant object
                    deep_space = Entity(
                        model='sphere',
                        scale=obj_scale,
                        position=(pos_x, pos_y, pos_z),
                        color=obj_color
                    )
                    
                    # Add glow effect
                    glow = Entity(
                        model='sphere',
                        scale=obj_scale * 1.5,
                        position=(pos_x, pos_y, pos_z),
                        color=Color(obj_color.r, obj_color.g, obj_color.b, 0.4)
                    )
                    
                    # Store metadata
                    deep_space.star_data = {
                        'object_type': obj_type,
                        'messier_number': obj.get('M', 'Unknown'),
                        'name': obj.get('Name', 'Unknown'),
                        'constellation': obj.get('Con', 'Unknown'),
                        'type': obj.get('Type', 'Unknown'),
                        'distance_ly': obj.get('Distance', 'Unknown')
                    }
                    deep_space.display_name = f"M{obj.get('M', '?')} - {obj.get('Name', 'Deep Space Object')}"
                    deep_space.object_type = 'deep_space'
                    
                    self.star_entities.append(deep_space)
                    galaxy_count += 1
                    
            except Exception as e:
                print(f"Could not load Messier catalog: {e}")
        
        print(f"Created {galaxy_count} deep space objects")
    
    def setup_lighting(self):
        """Set up proper 3D lighting for better object visualization"""
        # Create some basic lighting to improve 3D appearance
        try:
            # Main directional light (like a sun)
            light = DirectionalLight()
            light.color = color.white
            light.direction = (1, -1, -1)
            
            # Ambient light for general illumination
            ambient = AmbientLight()
            ambient.color = color.rgb(0.3, 0.3, 0.4)
            
        except Exception as e:
            print(f"Could not set up advanced lighting: {e}")
            # Fallback - just basic scene lighting
            scene.fog_color = color.black
    
    def setup_camera(self):
        """Setup camera controls for exploration"""
        # Use First Person Controller for better movement
        self.player = FirstPersonController(
            model='cube',
            color=color.clear,  # Invisible player model
            speed=8,  # Faster initial speed
            mouse_sensitivity=Vec2(60, 60),  # More responsive
            position=(0, 0, 5)  # Start closer to objects
        )
        
        # Set camera to follow the player smoothly
        camera.parent = self.player
        camera.position = (0, 0.5, 0)
        camera.rotation = (0, 0, 0)
        
        # Ensure mouse is initially locked for proper movement
        mouse.locked = True
        
        # Movement speed
        self.speed = 5
        
        # Override update to add proximity detection and UI updates
        original_update = self.player.update
        
        def enhanced_update():
            # Call original player update first
            if original_update:
                original_update()
            
            # Speed control
            if held_keys['q']:
                self.speed = min(50, self.speed * 1.02)
                self.player.speed = self.speed
            if held_keys['e']:
                self.speed = max(0.1, self.speed * 0.98)
                self.player.speed = self.speed
                
            # Check for nearby objects
            self.check_nearby_objects()
                
            # Update UI if available
            if hasattr(self, 'update_ui'):
                self.update_ui()
        
        self.player.update = enhanced_update
    
    def setup_ui(self):
        """Setup user interface"""
        # Create UI panel background
        self.ui_panel = Entity(
            model='cube',
            color=color.dark_gray,
            scale=(0.45, 0.8, 0.01),
            position=(0.68, 0, -1),
            parent=camera.ui
        )
        
        # Instructions
        self.instructions = Text(
            "3D COSMIC EXPLORER\n" +
            "WASD: Move | Mouse: Look\n" +
            "Space/C: Up/Down\n" +
            "Q/E: Speed +/-\n" +
            "TAB: Lock/Unlock Mouse\n" +
            "Click Star: Select\n" +
            "R: Reset View\n" +
            "ESC: Exit",
            position=(0.52, 0.45),
            scale=0.4,
            color=color.white,
            parent=camera.ui
        )
        
        # Position indicator
        self.position_text = Text(
            "Position: (0, 0, 0)",
            position=(0.52, 0.25),
            scale=0.5,
            color=color.cyan,
            parent=camera.ui
        )
        
        # Speed indicator
        self.speed_text = Text(
            f"Speed: {self.speed:.1f}",
            position=(0.52, 0.2),
            scale=0.5,
            color=color.yellow,
            parent=camera.ui
        )
        
        # Nearby objects display
        self.nearby_text = Text(
            "Nearby Objects: None",
            position=(0.52, 0.1),
            scale=0.45,
            color=color.lime,
            parent=camera.ui
        )
        
        # Selected star info
        self.star_info_text = Text(
            "Approach objects to see details",
            position=(0.52, -0.05),
            scale=0.4,
            color=color.light_gray,
            parent=camera.ui
        )
        
        # Detailed object info
        self.detail_info_text = Text(
            "",
            position=(0.52, -0.15),
            scale=0.35,
            color=color.orange,
            parent=camera.ui
        )
        
        # Stats
        self.stats_text = Text(
            f"Objects Loaded: {len(self.cosmic_data.get('stars', {}).get('catalog', []))}",
            position=(0.52, -0.4),
            scale=0.4,
            color=color.orange,
            parent=camera.ui
        )
        
        # Store position text for updating in main update function
        def update_ui():
            pos = self.player.position if hasattr(self, 'player') else camera.position
            self.position_text.text = f"Position: ({pos.x:.1f}, {pos.y:.1f}, {pos.z:.1f})"
            self.speed_text.text = f"Speed: {self.speed:.1f}"
            
        def update_nearby_display():
            if self.nearby_objects:
                closest = self.nearby_objects[0]
                self.nearby_text.text = f"Near: {closest['name']} ({closest['distance']:.1f}m)"
                self.nearby_text.color = color.lime
                
                # Show detailed information for closest object
                obj_type = closest['entity'].object_type if hasattr(closest['entity'], 'object_type') else 'unknown'
                data = closest['data']
                
                if obj_type == 'exoplanet':
                    details = f"EXOPLANET\n"
                    details += f"Host: {data.get('main_id', 'Unknown')}\n"
                    details += f"Distance: {data.get('distance_ly', 'Unknown')} ly\n"
                    details += f"Object Type: {data.get('object_type', 'Unknown')}\n"
                    if data.get('simbad_names'):
                        details += f"Also known as: {data.get('simbad_names', '').split('|')[0]}"
                elif obj_type == 'deep_space':
                    details = f"DEEP SPACE OBJECT\n"
                    details += f"Type: {data.get('type', 'Unknown')}\n"
                    details += f"Constellation: {data.get('constellation', 'Unknown')}\n"
                    details += f"Distance: {data.get('distance_ly', 'Unknown')} ly"
                else:
                    # Regular star
                    details = f"STAR\n"
                    details += f"Type: {data.get('star_type', 'Unknown')}\n"
                    details += f"Distance: {data.get('distance_ly', 'Unknown')} ly\n"
                    details += f"Temperature: {data.get('teff_gspphot', 'Unknown')} K\n"
                    if 'coordinates' in data:
                        details += f"Coords: {data['coordinates']}"
                
                self.detail_info_text.text = details
            else:
                self.nearby_text.text = "Nearby Objects: None"
                self.nearby_text.color = color.gray
                self.detail_info_text.text = "Approach objects to see details"
        
        self.update_ui = update_ui
        self.update_nearby_display = update_nearby_display
        
        # Add some test objects to ensure visibility
        self.create_test_objects()
    
    def select_star(self, star_entity):
        """Select a star and display its information"""
        self.selected_star = star_entity
        star_data = star_entity.star_data
        
        # Format star information
        info_text = f"Selected: {star_entity.display_name}\n"
        info_text += f"Type: {star_data.get('star_type', 'Unknown')}\n"
        info_text += f"Distance: {star_data.get('distance_ly', 'Unknown')} ly\n"
        info_text += f"Magnitude: {star_data.get('phot_g_mean_mag', 'Unknown')}\n"
        info_text += f"Temperature: {star_data.get('teff_gspphot', 'Unknown')} K"
        
        self.star_info_text.text = info_text
        
        # Highlight selected star
        star_entity.color = color.white
        
        print(f"Selected star: {star_entity.display_name}")
    
    def create_test_objects(self):
        """Create some test objects to ensure visibility"""
        # Create some large, colorful test objects near the origin - much more visible
        test_objects = [
            {'pos': (0, 0, 15), 'color': color.red, 'scale': 4, 'name': 'Red Giant', 'temp': 3500},
            {'pos': (8, 0, 12), 'color': color.blue, 'scale': 3, 'name': 'Blue Star', 'temp': 15000},
            {'pos': (-8, 0, 12), 'color': color.yellow, 'scale': 3.5, 'name': 'Yellow Sun', 'temp': 5778},
            {'pos': (0, 8, 15), 'color': color.green, 'scale': 2.5, 'name': 'Alien Test Star', 'temp': 6000},
            {'pos': (0, -8, 15), 'color': color.orange, 'scale': 3, 'name': 'Orange Dwarf', 'temp': 4200},
            {'pos': (5, 5, 10), 'color': color.violet, 'scale': 2, 'name': 'Purple Nebula', 'temp': 4000},
            {'pos': (-5, -5, 10), 'color': color.azure, 'scale': 2.5, 'name': 'Cyan Star', 'temp': 7000}
        ]
        
        for obj in test_objects:
            star = Entity(
                model='sphere',
                scale=obj['scale'],
                position=obj['pos'],
                color=obj['color']
            )
            
            # Add glow effect
            glow = Entity(
                model='sphere',
                scale=obj['scale'] * 1.3,
                position=obj['pos'],
                color=Color(obj['color'].r, obj['color'].g, obj['color'].b, 0.5)
            )
            
            # Add fake star data for interaction
            star.star_data = {
                'star_type': 'Test Star',
                'distance_ly': 10,
                'phot_g_mean_mag': 5,
                'teff_gspphot': obj['temp'],
                'mass': 1.2,
                'radius': obj['scale'],
                'coordinates': f"RA: {obj['pos'][0]:.1f}, Dec: {obj['pos'][1]:.1f}"
            }
            star.display_name = obj['name']
            star.object_type = 'star'
            self.star_entities.append(star)
            
        print(f"Created {len(test_objects)} test objects for visibility")
        
    def check_nearby_objects(self):
        """Check for objects near the player and display their information"""
        player_pos = self.player.position
        self.nearby_objects = []
        
        for star in self.star_entities:
            distance = math.sqrt(
                (star.position.x - player_pos.x) ** 2 +
                (star.position.y - player_pos.y) ** 2 +
                (star.position.z - player_pos.z) ** 2
            )
            
            if distance <= self.proximity_threshold:
                self.nearby_objects.append({
                    'entity': star,
                    'distance': distance,
                    'name': star.display_name,
                    'data': star.star_data
                })
        
        # Sort by distance
        self.nearby_objects.sort(key=lambda x: x['distance'])
        
        # Update nearby object display
        if hasattr(self, 'update_nearby_display'):
            self.update_nearby_display()

# Global input functions
def input(key):
    global explorer
    if not explorer:
        return
        
    if key == 'escape':
        application.quit()
    elif key == 'r':
        # Reset player position
        if hasattr(explorer, 'player'):
            explorer.player.position = (0, 0, -10)
            explorer.player.rotation = (0, 0, 0)
        else:
            camera.position = (0, 0, -10)
            camera.rotation = (0, 0, 0)
    elif key == 'left mouse down':
        # Star selection
        if mouse.hovered_entity and hasattr(mouse.hovered_entity, 'star_data'):
            explorer.select_star(mouse.hovered_entity)
    elif key == 'tab':
        # Toggle mouse lock
        mouse.locked = not mouse.locked
        print(f"Mouse locked: {mouse.locked}")

if __name__ == '__main__':
    explorer = EnhancedCosmicExplorer()
