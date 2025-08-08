#!/usr/bin/env python3
"""
Advanced Material and Texture System for Cosmic Engine
Cyberpunk-themed, photorealistic materials for celestial objects
"""

import numpy as np
from PIL import Image, ImageDraw, ImageFilter
import noise
import cv2
from typing import Dict, Tuple, List
from pathlib import Path
import json

class ProceduralTexture:
    """Generate procedural textures for cosmic objects"""
    
    def __init__(self):
        self.cache = {}
        
    def generate_star_texture(self, size: int, temperature: float, star_type: str) -> Image.Image:
        """Generate realistic star surface texture"""
        cache_key = f"star_{temperature}_{star_type}_{size}"
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # Base color from temperature
        base_color = self.temperature_to_rgb(temperature)
        
        # Create image
        img = Image.new('RGB', (size, size), base_color)
        pixels = img.load()
        
        # Add surface features (granulation, sunspots, flares)
        for y in range(size):
            for x in range(size):
                # Granulation pattern using multiple noise octaves
                granulation = self.multi_octave_noise(x, y, size, 8)
                
                # Sunspots (cooler regions)
                sunspot_noise = noise.pnoise2(x/size*20, y/size*20, octaves=4) * 0.3
                
                # Coronal loops and flares
                flare_noise = noise.pnoise2(x/size*50, y/size*50, octaves=6) * 0.2
                
                # Combine effects
                intensity = 1.0 + granulation*0.3 + sunspot_noise + flare_noise
                intensity = max(0.2, min(1.8, intensity))
                
                # Apply to color
                r = int(base_color[0] * intensity)
                g = int(base_color[1] * intensity) 
                b = int(base_color[2] * intensity)
                
                pixels[x, y] = (min(255, r), min(255, g), min(255, b))
                
        # Add bloom effect for hot stars
        if temperature > 8000:
            img = img.filter(ImageFilter.GaussianBlur(radius=2))
            
        self.cache[cache_key] = img
        return img
        
    def generate_planet_texture(self, size: int, planet_type: str, seed: int = None) -> Dict[str, Image.Image]:
        """Generate complete planet texture set (diffuse, normal, specular)"""
        if seed:
            np.random.seed(seed)
            
        textures = {}
        
        if planet_type == 'rocky':
            textures = self._create_rocky_planet_texture(size)
        elif planet_type == 'gas_giant':
            textures = self._create_gas_giant_texture(size)
        elif planet_type == 'ice':
            textures = self._create_ice_planet_texture(size)
        elif planet_type == 'desert':
            textures = self._create_desert_planet_texture(size)
        elif planet_type == 'ocean':
            textures = self._create_ocean_planet_texture(size)
        else:
            textures = self._create_generic_planet_texture(size)
            
        return textures
        
    def _create_rocky_planet_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create rocky planet texture with continents, mountains, craters"""
        # Diffuse map
        diffuse = Image.new('RGB', (size, size), (70, 60, 50))
        pixels = diffuse.load()
        
        # Normal map for height data
        normal_data = np.zeros((size, size, 3), dtype=np.uint8)
        
        for y in range(size):
            for x in range(size):
                # Continental masses
                continent = noise.pnoise2(x/size*5, y/size*5, octaves=4) > 0.1
                
                # Mountain ranges
                mountains = noise.pnoise2(x/size*20, y/size*20, octaves=6) * 0.5
                
                # Crater patterns
                crater_noise = noise.pnoise2(x/size*100, y/size*100, octaves=3) * 0.3
                
                if continent:
                    # Land color with elevation
                    elevation = (mountains + crater_noise + 1) / 2
                    base_color = (int(100 * elevation), int(80 * elevation), int(60 * elevation))
                else:
                    # Dark lowlands/seas
                    base_color = (40, 35, 30)
                    elevation = 0.2
                    
                pixels[x, y] = base_color
                
                # Normal map (height to normal conversion)
                height = elevation * 255
                normal_data[y, x] = [128, 128, int(height)]
                
        normal_map = Image.fromarray(normal_data)
        
        # Specular map (rocky surfaces have low specularity)
        specular = Image.new('L', (size, size), 30)
        
        return {
            'diffuse': diffuse,
            'normal': normal_map,
            'specular': specular
        }
        
    def _create_gas_giant_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create gas giant with atmospheric bands and storms"""
        diffuse = Image.new('RGB', (size, size))
        pixels = diffuse.load()
        
        # Great Red Spot coordinates
        spot_x, spot_y = size//3, size//2
        
        for y in range(size):
            for x in range(size):
                # Latitude-based banding
                lat = (y / size - 0.5) * 2  # -1 to 1
                
                # Base atmospheric bands
                band_color = self._get_gas_giant_band_color(lat)
                
                # Turbulence and storms
                storm_noise = noise.pnoise2(x/size*30, y/size*15, octaves=4) * 0.3
                
                # Great Red Spot
                dist_to_spot = np.sqrt((x - spot_x)**2 + (y - spot_y)**2)
                if dist_to_spot < size//10:
                    spot_intensity = 1 - (dist_to_spot / (size//10))
                    red_tint = spot_intensity * 0.5
                    band_color = (
                        min(255, int(band_color[0] + red_tint * 255)),
                        int(band_color[1] * (1 - red_tint * 0.3)),
                        int(band_color[2] * (1 - red_tint * 0.5))
                    )
                
                # Apply storm turbulence
                turbulence = 1 + storm_noise
                final_color = tuple(int(c * turbulence) for c in band_color)
                final_color = tuple(min(255, max(0, c)) for c in final_color)
                
                pixels[x, y] = final_color
                
        return {'diffuse': diffuse}
        
    def _create_ice_planet_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create icy planet with frozen seas and ice sheets"""
        diffuse = Image.new('RGB', (size, size), (200, 220, 255))
        pixels = diffuse.load()
        
        for y in range(size):
            for x in range(size):
                # Ice sheet variations
                ice_variation = noise.pnoise2(x/size*10, y/size*10, octaves=5)
                
                # Cracks and crevasses
                cracks = abs(noise.pnoise2(x/size*50, y/size*50, octaves=3)) < 0.05
                
                if cracks:
                    # Dark cracks
                    color = (50, 70, 120)
                else:
                    # Varying ice colors
                    brightness = 0.7 + ice_variation * 0.3
                    color = (
                        int(200 * brightness),
                        int(220 * brightness),
                        int(255 * brightness)
                    )
                    
                pixels[x, y] = color
                
        # High specular for ice
        specular = Image.new('L', (size, size), 200)
        
        return {
            'diffuse': diffuse,
            'specular': specular
        }
        
    def _create_desert_planet_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create desert planet like Mars"""
        diffuse = Image.new('RGB', (size, size), (180, 100, 60))
        pixels = diffuse.load()
        
        for y in range(size):
            for x in range(size):
                # Dune patterns
                dunes = noise.pnoise2(x/size*20, y/size*20, octaves=4) * 0.3
                
                # Rock formations
                rocks = noise.pnoise2(x/size*40, y/size*40, octaves=6) * 0.2
                
                # Dust storms
                dust = noise.pnoise2(x/size*100, y/size*100, octaves=2) * 0.1
                
                brightness = 0.8 + dunes + rocks + dust
                color = (
                    int(180 * brightness),
                    int(100 * brightness),
                    int(60 * brightness)
                )
                
                pixels[x, y] = tuple(min(255, max(0, c)) for c in color)
                
        return {'diffuse': diffuse}
        
    def _create_ocean_planet_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create Earth-like ocean planet"""
        diffuse = Image.new('RGB', (size, size))
        pixels = diffuse.load()
        
        for y in range(size):
            for x in range(size):
                # Continental shelf
                continent = noise.pnoise2(x/size*5, y/size*5, octaves=4) > 0.0
                
                # Ocean depth variations
                ocean_depth = noise.pnoise2(x/size*15, y/size*15, octaves=5)
                
                if continent:
                    # Land with vegetation
                    vegetation = noise.pnoise2(x/size*30, y/size*30, octaves=3)
                    if vegetation > 0.2:
                        color = (60, 120, 40)  # Forest
                    elif vegetation > -0.2:
                        color = (140, 120, 80)  # Plains
                    else:
                        color = (100, 90, 70)  # Desert
                else:
                    # Ocean color based on depth
                    depth_factor = (ocean_depth + 1) / 2
                    blue_intensity = int(30 + depth_factor * 100)
                    color = (0, blue_intensity//2, blue_intensity)
                    
                pixels[x, y] = color
                
        # High specular for water
        specular = Image.new('L', (size, size))
        spec_pixels = specular.load()
        
        for y in range(size):
            for x in range(size):
                continent = noise.pnoise2(x/size*5, y/size*5, octaves=4) > 0.0
                spec_pixels[x, y] = 50 if continent else 200
                
        return {
            'diffuse': diffuse,
            'specular': specular
        }
        
    def _create_generic_planet_texture(self, size: int) -> Dict[str, Image.Image]:
        """Create generic alien planet texture"""
        colors = [
            (120, 80, 200),   # Purple
            (200, 120, 80),   # Orange
            (80, 200, 120),   # Green
            (200, 200, 80)    # Yellow
        ]
        
        base_color = colors[np.random.randint(0, len(colors))]
        diffuse = Image.new('RGB', (size, size), base_color)
        pixels = diffuse.load()
        
        for y in range(size):
            for x in range(size):
                variation = noise.pnoise2(x/size*10, y/size*10, octaves=4) * 0.4
                brightness = 0.8 + variation
                
                color = tuple(int(c * brightness) for c in base_color)
                pixels[x, y] = tuple(min(255, max(0, c)) for c in color)
                
        return {'diffuse': diffuse}
        
    def generate_nebula_texture(self, size: int, nebula_type: str) -> Image.Image:
        """Generate nebula texture with volumetric appearance"""
        if nebula_type == 'emission':
            base_colors = [(255, 100, 100), (100, 255, 100), (100, 100, 255)]
        elif nebula_type == 'reflection':
            base_colors = [(100, 150, 255), (150, 200, 255)]
        else:  # dark nebula
            base_colors = [(50, 30, 30), (30, 50, 30), (30, 30, 50)]
            
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        
        # Multiple layers for depth
        for layer in range(5):
            layer_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
            pixels = layer_img.load()
            
            color = base_colors[layer % len(base_colors)]
            alpha_scale = 1.0 - layer * 0.15
            
            for y in range(size):
                for x in range(size):
                    density = noise.pnoise2(
                        x/size * (5 + layer*2), 
                        y/size * (5 + layer*2), 
                        octaves=4 + layer
                    )
                    
                    if density > 0.1:
                        alpha = int(density * 80 * alpha_scale)
                        pixels[x, y] = (*color, alpha)
                        
            img = Image.alpha_composite(img, layer_img)
            
        return img
        
    def create_star_corona(self, size: int, star_color: Tuple[int, int, int]) -> Image.Image:
        """Create stellar corona effect"""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        pixels = img.load()
        
        center_x, center_y = size // 2, size // 2
        max_radius = size // 2
        
        for y in range(size):
            for x in range(size):
                dist = np.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                if dist < max_radius:
                    # Corona intensity falls off with distance
                    intensity = 1.0 - (dist / max_radius)**2
                    
                    # Add coronal streamers
                    angle = np.arctan2(y - center_y, x - center_x)
                    streamer = abs(noise.pnoise1(angle * 8)) * 0.5
                    
                    final_intensity = intensity * (0.3 + streamer)
                    alpha = int(final_intensity * 100)
                    
                    if alpha > 5:
                        pixels[x, y] = (*star_color, alpha)
                        
        return img
        
    # Helper methods
    def temperature_to_rgb(self, temperature: float) -> Tuple[int, int, int]:
        """Convert stellar temperature to RGB color"""
        # Simplified blackbody radiation
        if temperature < 3700:
            return (255, 100, 50)
        elif temperature < 5200:
            return (255, 180, 100)
        elif temperature < 6000:
            return (255, 255, 200)
        elif temperature < 7500:
            return (255, 255, 255)
        elif temperature < 10000:
            return (200, 220, 255)
        else:
            return (150, 200, 255)
            
    def multi_octave_noise(self, x: int, y: int, size: int, octaves: int) -> float:
        """Generate multi-octave noise for complex patterns"""
        value = 0
        frequency = 1
        amplitude = 1
        max_value = 0
        
        for i in range(octaves):
            value += noise.pnoise2(x/size * frequency, y/size * frequency) * amplitude
            max_value += amplitude
            amplitude *= 0.5
            frequency *= 2
            
        return value / max_value
        
    def _get_gas_giant_band_color(self, latitude: float) -> Tuple[int, int, int]:
        """Get atmospheric band color based on latitude"""
        # Simulate Jupiter-like bands
        abs_lat = abs(latitude)
        
        if abs_lat < 0.2:  # Equatorial
            return (200, 150, 100)
        elif abs_lat < 0.4:  # Tropical
            return (150, 120, 80)
        elif abs_lat < 0.6:  # Temperate
            return (180, 140, 110)
        elif abs_lat < 0.8:  # Polar
            return (120, 100, 80)
        else:  # Polar caps
            return (100, 90, 70)

class MaterialSystem:
    """Advanced material system for Panda3D integration"""
    
    def __init__(self):
        self.texture_generator = ProceduralTexture()
        self.materials = {}
        
    def create_star_material(self, temperature: float, star_type: str) -> Dict:
        """Create complete star material with textures and properties"""
        material_id = f"star_{temperature}_{star_type}"
        
        if material_id in self.materials:
            return self.materials[material_id]
            
        # Generate textures
        diffuse_texture = self.texture_generator.generate_star_texture(512, temperature, star_type)
        corona_texture = self.texture_generator.create_star_corona(512, 
            self.texture_generator.temperature_to_rgb(temperature))
        
        # Material properties
        base_color = self.texture_generator.temperature_to_rgb(temperature)
        material = {
            'type': 'star',
            'diffuse_texture': diffuse_texture,
            'corona_texture': corona_texture,
            'emission_color': tuple(c/255.0 for c in base_color),
            'emission_strength': min(2.0, temperature / 3000.0),
            'temperature': temperature,
            'metallic': 0.0,
            'roughness': 0.8,
            'glow_radius': 2.0 + (temperature / 10000.0) * 3.0
        }
        
        self.materials[material_id] = material
        return material
        
    def create_planet_material(self, planet_type: str, seed: int = None) -> Dict:
        """Create complete planet material"""
        material_id = f"planet_{planet_type}_{seed}"
        
        if material_id in self.materials:
            return self.materials[material_id]
            
        textures = self.texture_generator.generate_planet_texture(512, planet_type, seed)
        
        # Material properties based on planet type
        if planet_type == 'rocky':
            material_props = {'metallic': 0.1, 'roughness': 0.8, 'specular': 0.2}
        elif planet_type == 'gas_giant':
            material_props = {'metallic': 0.0, 'roughness': 0.3, 'specular': 0.1}
        elif planet_type == 'ice':
            material_props = {'metallic': 0.0, 'roughness': 0.1, 'specular': 0.9}
        elif planet_type == 'desert':
            material_props = {'metallic': 0.0, 'roughness': 0.9, 'specular': 0.1}
        elif planet_type == 'ocean':
            material_props = {'metallic': 0.0, 'roughness': 0.2, 'specular': 0.7}
        else:
            material_props = {'metallic': 0.1, 'roughness': 0.5, 'specular': 0.3}
            
        material = {
            'type': 'planet',
            'planet_type': planet_type,
            'textures': textures,
            **material_props,
            'atmosphere': planet_type in ['gas_giant', 'ocean'],
            'atmosphere_color': (0.5, 0.7, 1.0) if planet_type == 'ocean' else (0.8, 0.6, 0.4)
        }
        
        self.materials[material_id] = material
        return material
        
    def create_nebula_material(self, nebula_type: str) -> Dict:
        """Create volumetric nebula material"""
        material_id = f"nebula_{nebula_type}"
        
        if material_id in self.materials:
            return self.materials[material_id]
            
        nebula_texture = self.texture_generator.generate_nebula_texture(512, nebula_type)
        
        material = {
            'type': 'nebula',
            'nebula_type': nebula_type,
            'texture': nebula_texture,
            'transparency': 0.7,
            'emission': True,
            'volumetric': True,
            'density': 0.3
        }
        
        self.materials[material_id] = material
        return material
        
    def save_material_cache(self, cache_path: str):
        """Save generated materials to disk cache"""
        cache_dir = Path(cache_path)
        cache_dir.mkdir(exist_ok=True)
        
        for material_id, material in self.materials.items():
            material_dir = cache_dir / material_id
            material_dir.mkdir(exist_ok=True)
            
            # Save textures
            for texture_name, texture in material.get('textures', {}).items():
                texture.save(material_dir / f"{texture_name}.png")
                
            if 'diffuse_texture' in material:
                material['diffuse_texture'].save(material_dir / "diffuse.png")
            if 'corona_texture' in material:
                material['corona_texture'].save(material_dir / "corona.png")
            if 'texture' in material:
                material['texture'].save(material_dir / "texture.png")
                
            # Save material properties
            props = {k: v for k, v in material.items() 
                    if k not in ['textures', 'diffuse_texture', 'corona_texture', 'texture']}
            
            with open(material_dir / "properties.json", 'w') as f:
                json.dump(props, f, indent=2)

# Testing and example usage
if __name__ == "__main__":
    material_system = MaterialSystem()
    
    # Test star material
    sun_material = material_system.create_star_material(5778, 'G-type')
    print("Created Sun-like star material")
    
    # Test planet materials
    earth_material = material_system.create_planet_material('ocean', seed=42)
    mars_material = material_system.create_planet_material('desert', seed=123)
    jupiter_material = material_system.create_planet_material('gas_giant', seed=456)
    
    # Test nebula material
    nebula_material = material_system.create_nebula_material('emission')
    
    print("All materials created successfully!")
    
    # Save to cache
    material_system.save_material_cache("./material_cache")
    print("Materials cached to disk")
