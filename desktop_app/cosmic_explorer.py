from ursina import Ursina, Entity, camera, color
from data_loader import load_exoplanet_data

class CosmicExplorer(Entity):
    def __init__(self):
        super().__init__()
        # Load exoplanet data
        planets = load_exoplanet_data()
        # Create a simple sphere for each planet (demo)
        for planet in planets:
            Entity(model='sphere', color=color.azure, scale=0.1, position=(planet['x'], planet['y'], planet['z']))

if __name__ == '__main__':
    app = Ursina()
    explorer = CosmicExplorer()
    camera.position = (0, 0, -10)
    app.run() 