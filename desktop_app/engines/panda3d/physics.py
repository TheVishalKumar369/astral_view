#!/usr/bin/env python3
"""
Advanced Physics Simulation for Cosmic Engine
Real orbital mechanics, gravitational forces, and celestial dynamics
"""

import numpy as np
import pybullet as p
from astropy import units as u
from astropy import constants as const
from typing import List, Tuple, Dict
import math

class GravitationalBody:
    """Represents a celestial body with mass and gravitational influence"""
    
    def __init__(self, name: str, mass: float, position: np.ndarray, velocity: np.ndarray, radius: float):
        self.name = name
        self.mass = mass  # kg
        self.position = position  # meters
        self.velocity = velocity  # m/s
        self.radius = radius  # meters
        self.trajectory = [position.copy()]
        
class OrbitalMechanics:
    """Implements realistic orbital mechanics and n-body simulation"""
    
    def __init__(self):
        self.G = const.G.value  # Gravitational constant
        self.bodies = []
        self.time_step = 86400.0  # 1 day in seconds
        self.time_scale = 1000.0  # Speed up simulation
        
    def add_body(self, body: GravitationalBody):
        """Add celestial body to simulation"""
        self.bodies.append(body)
        
    def calculate_gravitational_force(self, body1: GravitationalBody, body2: GravitationalBody) -> np.ndarray:
        """Calculate gravitational force between two bodies"""
        r_vector = body2.position - body1.position
        r_magnitude = np.linalg.norm(r_vector)
        
        if r_magnitude == 0:
            return np.zeros(3)
            
        # Newton's law of universal gravitation
        force_magnitude = self.G * body1.mass * body2.mass / (r_magnitude ** 2)
        force_direction = r_vector / r_magnitude
        
        return force_magnitude * force_direction
        
    def update_bodies(self, dt: float):
        """Update positions and velocities using gravitational forces"""
        forces = {}
        
        # Calculate all gravitational forces
        for i, body1 in enumerate(self.bodies):
            forces[i] = np.zeros(3)
            
            for j, body2 in enumerate(self.bodies):
                if i != j:
                    force = self.calculate_gravitational_force(body1, body2)
                    forces[i] += force
                    
        # Update velocities and positions
        for i, body in enumerate(self.bodies):
            # F = ma, so a = F/m
            acceleration = forces[i] / body.mass
            
            # Leapfrog integration for stability
            body.velocity += acceleration * dt
            body.position += body.velocity * dt
            
            # Store trajectory
            if len(body.trajectory) > 10000:
                body.trajectory.pop(0)
            body.trajectory.append(body.position.copy())
            
    def get_orbital_elements(self, body: GravitationalBody, central_body: GravitationalBody) -> Dict:
        """Calculate Keplerian orbital elements"""
        r = body.position - central_body.position
        v = body.velocity - central_body.velocity
        mu = self.G * (body.mass + central_body.mass)
        
        h = np.cross(r, v)  # Specific angular momentum
        h_mag = np.linalg.norm(h)
        
        # Semi-major axis
        energy = 0.5 * np.dot(v, v) - mu / np.linalg.norm(r)
        a = -mu / (2 * energy)
        
        # Eccentricity
        e_vec = np.cross(v, h) / mu - r / np.linalg.norm(r)
        e = np.linalg.norm(e_vec)
        
        # Inclination
        i = math.acos(h[2] / h_mag) if h_mag > 0 else 0
        
        return {
            'semi_major_axis': a,
            'eccentricity': e,
            'inclination': i,
            'period': 2 * math.pi * math.sqrt(a**3 / mu) if a > 0 else 0
        }

class RealisticSolarSystem:
    """Generate realistic solar systems based on astronomical data"""
    
    def __init__(self):
        self.orbital_mechanics = OrbitalMechanics()
        
    def create_star_system(self, star_data: Dict) -> List[GravitationalBody]:
        """Create a realistic star system from astronomical data"""
        bodies = []
        
        # Central star
        star_mass = self.estimate_star_mass(star_data)
        star = GravitationalBody(
            name=star_data.get('display_name', 'Star'),
            mass=star_mass,
            position=np.zeros(3),
            velocity=np.zeros(3),
            radius=self.estimate_star_radius(star_data)
        )
        bodies.append(star)
        
        # Generate planets using empirical relationships
        num_planets = self.estimate_planet_count(star_mass)
        
        for i in range(num_planets):
            planet = self.generate_planet(star, i)
            bodies.append(planet)
            
        return bodies
        
    def estimate_star_mass(self, star_data: Dict) -> float:
        """Estimate stellar mass from temperature and luminosity"""
        # Default to solar mass
        solar_mass = const.M_sun.value
        
        temp = star_data.get('teff_gspphot', 5778)  # K
        
        # Mass-temperature relationship (simplified)
        if temp < 3700:      # M-class
            return solar_mass * 0.3
        elif temp < 5200:    # K-class  
            return solar_mass * 0.7
        elif temp < 6000:    # G-class (Sun-like)
            return solar_mass * 1.0
        elif temp < 7500:    # F-class
            return solar_mass * 1.3
        elif temp < 10000:   # A-class
            return solar_mass * 2.0
        else:                # B/O-class
            return solar_mass * 10.0
            
    def estimate_star_radius(self, star_data: Dict) -> float:
        """Estimate stellar radius"""
        solar_radius = const.R_sun.value
        temp = star_data.get('teff_gspphot', 5778)
        
        # Simplified radius estimation
        if temp < 3700:      # M-class
            return solar_radius * 0.4
        elif temp < 5200:    # K-class
            return solar_radius * 0.8
        elif temp < 6000:    # G-class
            return solar_radius * 1.0
        elif temp < 7500:    # F-class
            return solar_radius * 1.2
        elif temp < 10000:   # A-class
            return solar_radius * 1.8
        else:                # B/O-class
            return solar_radius * 5.0
            
    def estimate_planet_count(self, star_mass: float) -> int:
        """Estimate number of planets based on stellar mass"""
        solar_mass = const.M_sun.value
        mass_ratio = star_mass / solar_mass
        
        # Empirical relationship: more massive stars tend to have fewer planets
        if mass_ratio > 3.0:
            return np.random.randint(0, 3)
        elif mass_ratio > 1.5:
            return np.random.randint(1, 5)
        else:
            return np.random.randint(2, 8)
            
    def generate_planet(self, star: GravitationalBody, planet_index: int) -> GravitationalBody:
        """Generate realistic planet with proper orbital mechanics"""
        # Orbital distance (Titius-Bode law approximation)
        au = const.au.value
        orbital_distance = au * (0.4 + 0.3 * (2 ** planet_index))
        
        # Planet mass (Earth masses to kg)
        earth_mass = const.M_earth.value
        if planet_index < 4:  # Inner planets (rocky)
            planet_mass = earth_mass * np.random.uniform(0.1, 2.0)
            planet_radius = const.R_earth.value * (planet_mass / earth_mass) ** 0.27
        else:  # Outer planets (gas giants)
            planet_mass = earth_mass * np.random.uniform(10, 300)
            planet_radius = const.R_earth.value * (planet_mass / earth_mass) ** 0.5
            
        # Circular orbital velocity
        mu = self.orbital_mechanics.G * star.mass
        orbital_velocity = math.sqrt(mu / orbital_distance)
        
        # Random orbital position
        angle = np.random.uniform(0, 2 * math.pi)
        position = np.array([
            orbital_distance * math.cos(angle),
            0,
            orbital_distance * math.sin(angle)
        ])
        
        velocity = np.array([
            -orbital_velocity * math.sin(angle),
            0,
            orbital_velocity * math.cos(angle)
        ])
        
        planet_types = ['rocky', 'gas_giant', 'ice_giant', 'super_earth']
        planet_type = planet_types[min(planet_index // 2, len(planet_types) - 1)]
        
        planet = GravitationalBody(
            name=f"Planet_{planet_index + 1}_{planet_type}",
            mass=planet_mass,
            position=position,
            velocity=velocity,
            radius=planet_radius
        )
        
        return planet

class PhysicsEngine:
    """Main physics engine integrating all systems"""
    
    def __init__(self):
        self.orbital_mechanics = OrbitalMechanics()
        self.solar_system_generator = RealisticSolarSystem()
        self.bullet_world = None
        self.simulation_time = 0.0
        
    def initialize_bullet_physics(self):
        """Initialize Bullet Physics for collision detection"""
        self.bullet_world = p.connect(p.DIRECT)
        p.setGravity(0, 0, 0)  # No global gravity - we handle it manually
        
    def create_cosmic_simulation(self, stellar_data: List[Dict]) -> Dict:
        """Create full cosmic simulation from stellar database"""
        all_systems = {}
        
        for i, star_data in enumerate(stellar_data[:10]):  # Limit for performance
            system_bodies = self.solar_system_generator.create_star_system(star_data)
            
            # Add to orbital mechanics
            for body in system_bodies:
                self.orbital_mechanics.add_body(body)
                
            all_systems[f"system_{i}"] = system_bodies
            
        return all_systems
        
    def update_physics(self, dt: float):
        """Update all physics systems"""
        scaled_dt = dt * self.orbital_mechanics.time_scale
        self.orbital_mechanics.update_bodies(scaled_dt)
        self.simulation_time += scaled_dt
        
    def get_body_positions(self) -> Dict:
        """Get current positions of all bodies for rendering"""
        positions = {}
        
        for i, body in enumerate(self.orbital_mechanics.bodies):
            positions[body.name] = {
                'position': body.position / const.au.value,  # Convert to AU for rendering
                'mass': body.mass,
                'radius': body.radius,
                'velocity': np.linalg.norm(body.velocity) / 1000,  # km/s
                'trajectory': [pos / const.au.value for pos in body.trajectory[-100:]]  # Last 100 positions
            }
            
        return positions

# Example usage and testing
if __name__ == "__main__":
    # Test the physics engine
    physics = PhysicsEngine()
    
    # Create a simple solar system
    stellar_data = [{
        'display_name': 'Test Star',
        'teff_gspphot': 5778,  # Sun-like temperature
        'x': 0, 'y': 0, 'z': 0
    }]
    
    systems = physics.create_cosmic_simulation(stellar_data)
    
    # Simulate for a few steps
    for step in range(1000):
        physics.update_physics(0.1)  # 0.1 second time steps
        
    positions = physics.get_body_positions()
    
    print("=== Cosmic Simulation Results ===")
    for name, data in positions.items():
        print(f"{name}: Position={data['position'][:2]} AU, Velocity={data['velocity']:.2f} km/s")
