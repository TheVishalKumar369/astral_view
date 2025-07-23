#!/usr/bin/env python3
"""
collect_data_simple.py
Simplified data collection script that focuses on core data without problematic Gaia/SIMBAD queries.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
from datetime import datetime
import time

# Add the scripts directory to the path
sys.path.append(str(Path(__file__).parent))

RAW_DATA_DIR = Path("/workspace/data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

def fetch_nasa_exoplanets_simple():
    """Fetch NASA Exoplanet Archive data with simplified approach"""
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    
    print("=== Fetching NASA Exoplanet Archive (Simplified) ===")
    
    # Use only essential fields that are guaranteed to exist
    essential_fields = [
        'pl_name', 'hostname', 'sy_dist', 'ra', 'dec',  # Basic info
        'pl_rade', 'pl_bmasse', 'pl_orbper', 'pl_eqt',  # Planet properties
        'st_teff', 'st_rad', 'discoverymethod', 'disc_year',  # Star and discovery
        'pl_orbsmax', 'pl_orbeccen', 'pl_insol', 'pl_dens'  # Orbital properties
    ]
    
    try:
        # Query confirmed planets only
        query = NasaExoplanetArchive.query_criteria(
            table='pscomppars',
            select=','.join(essential_fields),
            where="pl_controv_flag=0"  # Only confirmed planets
        )
        
        print(f"✓ Retrieved {len(query)} exoplanet systems")
        
        # Clean and process the data
        df = query.to_pandas()
        
        # Fill missing values with reasonable defaults
        df['pl_rade'] = df['pl_rade'].fillna(0)
        df['pl_bmasse'] = df['pl_bmasse'].fillna(0)
        df['pl_orbper'] = df['pl_orbper'].fillna(0)
        df['pl_eqt'] = df['pl_eqt'].fillna(0)
        df['st_teff'] = df['st_teff'].fillna(0)
        df['st_rad'] = df['st_rad'].fillna(0)
        df['pl_orbsmax'] = df['pl_orbsmax'].fillna(0)
        df['pl_orbeccen'] = df['pl_orbeccen'].fillna(0)
        df['pl_insol'] = df['pl_insol'].fillna(0)
        df['pl_dens'] = df['pl_dens'].fillna(0)
        
        # Add computed fields for gameplay
        df['distance_ly'] = df['sy_dist'] * 3.26156  # Convert parsecs to light years
        df['object_type'] = 'Exoplanet'
        df['mass_earth'] = df['pl_bmasse']
        df['radius_earth'] = df['pl_rade']
        df['temperature_k'] = df['pl_eqt']
        df['orbital_period_days'] = df['pl_orbper']
        df['semi_major_axis_au'] = df['pl_orbsmax']
        df['eccentricity'] = df['pl_orbeccen']
        df['insolation_flux'] = df['pl_insol']
        df['density_g_cm3'] = df['pl_dens']
        
        # Save the data
        output_file = RAW_DATA_DIR / "nasa_exoplanets_simple.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Saved {len(df)} exoplanet systems to {output_file}")
        
        return df
        
    except Exception as e:
        print(f"❌ Error fetching exoplanet data: {e}")
        return None

def fetch_jpl_solar_system_simple():
    """Fetch Solar System data with simplified approach"""
    from astroquery.jplhorizons import Horizons
    from datetime import datetime
    from astropy.time import Time
    
    print("=== Fetching Solar System Data (Simplified) ===")
    
    # Current date
    current_date = datetime.now()
    jd = Time(current_date).jd
    
    # Define Solar System bodies with their JPL IDs
    solar_system_bodies = {
        'Sun': '10',
        'Mercury': '199', 
        'Venus': '299',
        'Earth': '399',
        'Moon': '301',
        'Mars': '499',
        'Jupiter': '599',
        'Saturn': '699',
        'Uranus': '799',
        'Neptune': '899',
        'Pluto': '999',
        'Ceres': '1',
        'Vesta': '4',
        'Pallas': '2',
        'Eros': '433'
    }
    
    data_list = []
    
    for name, jpl_id in solar_system_bodies.items():
        try:
            print(f"Fetching {name} (ID: {jpl_id})...")
            
            # Query JPL Horizons
            obj = Horizons(id=jpl_id, location='@sun', epochs=jd)
            vectors = obj.vectors()
            
            if len(vectors) > 0:
                # Extract position (convert to light years)
                x = vectors['x'][0] / 63241.1  # AU to light years
                y = vectors['y'][0] / 63241.1
                z = vectors['z'][0] / 63241.1
                
                # Calculate distance from Sun
                distance_au = np.sqrt(x**2 + y**2 + z**2) * 63241.1
                
                # Determine object type
                if name == 'Sun':
                    obj_type = 'Star'
                elif name in ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                    obj_type = 'Planet'
                elif name == 'Moon':
                    obj_type = 'Satellite'
                else:
                    obj_type = 'Asteroid'
                
                data_list.append({
                    'name': name,
                    'object_type': obj_type,
                    'distance_from_sun_au': distance_au,
                    'x_ly': x,
                    'y_ly': y,
                    'z_ly': z,
                    'ra': 0,  # Placeholder
                    'dec': 0,  # Placeholder
                    'distance_ly': 0,  # Placeholder
                    'mass_earth': 0,  # Placeholder
                    'radius_earth': 0,  # Placeholder
                    'temperature_k': 0,  # Placeholder
                    'orbital_period_days': 0,  # Placeholder
                    'semi_major_axis_au': distance_au,
                    'eccentricity': 0,  # Placeholder
                    'insolation_flux': 0,  # Placeholder
                    'density_g_cm3': 0  # Placeholder
                })
                
                print(f"  ✓ {name}: ({x:.6f}, {y:.6f}, {z:.6f}) LY")
                
            else:
                print(f"  ❌ No data for {name}")
                
        except Exception as e:
            print(f"  ❌ Error fetching {name}: {e}")
    
    if data_list:
        df = pd.DataFrame(data_list)
        output_file = RAW_DATA_DIR / "solar_system_simple.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Saved {len(df)} Solar System bodies to {output_file}")
        return df
    else:
        print("❌ No Solar System data retrieved")
        return None

def fetch_messier_catalog_simple():
    """Fetch Messier Catalog data with simplified approach"""
    from astroquery.simbad import Simbad
    
    print("=== Fetching Messier Catalog (Simplified) ===")
    
    # Define Messier objects with their coordinates and types
    messier_objects = {
        'M1': {'name': 'Crab Nebula', 'type': 'Supernova Remnant', 'ra': 83.633, 'dec': 22.014, 'distance_ly': 6500},
        'M2': {'name': 'NGC 7089', 'type': 'Globular Cluster', 'ra': 323.362, 'dec': -0.823, 'distance_ly': 37500},
        'M3': {'name': 'NGC 5272', 'type': 'Globular Cluster', 'ra': 205.548, 'dec': 28.377, 'distance_ly': 33900},
        'M4': {'name': 'NGC 6121', 'type': 'Globular Cluster', 'ra': 245.897, 'dec': -26.526, 'distance_ly': 7200},
        'M5': {'name': 'NGC 5904', 'type': 'Globular Cluster', 'ra': 229.638, 'dec': 2.081, 'distance_ly': 24500},
        'M6': {'name': 'Butterfly Cluster', 'type': 'Open Cluster', 'ra': 265.087, 'dec': -32.251, 'distance_ly': 1600},
        'M7': {'name': 'Ptolemy Cluster', 'type': 'Open Cluster', 'ra': 268.472, 'dec': -34.793, 'distance_ly': 980},
        'M8': {'name': 'Lagoon Nebula', 'type': 'Emission Nebula', 'ra': 271.042, 'dec': -24.383, 'distance_ly': 5200},
        'M9': {'name': 'NGC 6333', 'type': 'Globular Cluster', 'ra': 259.799, 'dec': -18.516, 'distance_ly': 25800},
        'M10': {'name': 'NGC 6254', 'type': 'Globular Cluster', 'ra': 254.287, 'dec': -4.099, 'distance_ly': 14300},
        'M11': {'name': 'Wild Duck Cluster', 'type': 'Open Cluster', 'ra': 282.768, 'dec': -6.269, 'distance_ly': 6200},
        'M12': {'name': 'NGC 6218', 'type': 'Globular Cluster', 'ra': 251.809, 'dec': -1.949, 'distance_ly': 15800},
        'M13': {'name': 'Great Hercules Cluster', 'type': 'Globular Cluster', 'ra': 250.423, 'dec': 36.461, 'distance_ly': 22200},
        'M14': {'name': 'NGC 6402', 'type': 'Globular Cluster', 'ra': 264.071, 'dec': -3.246, 'distance_ly': 30300},
        'M15': {'name': 'NGC 7078', 'type': 'Globular Cluster', 'ra': 322.493, 'dec': 12.167, 'distance_ly': 33600},
        'M16': {'name': 'Eagle Nebula', 'type': 'Emission Nebula', 'ra': 274.700, 'dec': -13.807, 'distance_ly': 7000},
        'M17': {'name': 'Omega Nebula', 'type': 'Emission Nebula', 'ra': 275.200, 'dec': -16.183, 'distance_ly': 5500},
        'M18': {'name': 'NGC 6613', 'type': 'Open Cluster', 'ra': 274.900, 'dec': -17.133, 'distance_ly': 4900},
        'M19': {'name': 'NGC 6273', 'type': 'Globular Cluster', 'ra': 255.657, 'dec': -26.267, 'distance_ly': 28700},
        'M20': {'name': 'Trifid Nebula', 'type': 'Emission Nebula', 'ra': 270.667, 'dec': -23.017, 'distance_ly': 5200},
        'M21': {'name': 'NGC 6531', 'type': 'Open Cluster', 'ra': 271.200, 'dec': -22.500, 'distance_ly': 4200},
        'M22': {'name': 'NGC 6656', 'type': 'Globular Cluster', 'ra': 279.100, 'dec': -23.904, 'distance_ly': 10400},
        'M23': {'name': 'NGC 6494', 'type': 'Open Cluster', 'ra': 269.200, 'dec': -19.017, 'distance_ly': 2150},
        'M24': {'name': 'Sagittarius Star Cloud', 'type': 'Star Cloud', 'ra': 274.200, 'dec': -18.500, 'distance_ly': 10000},
        'M25': {'name': 'IC 4725', 'type': 'Open Cluster', 'ra': 277.600, 'dec': -19.250, 'distance_ly': 2000},
        'M26': {'name': 'NGC 6694', 'type': 'Open Cluster', 'ra': 281.300, 'dec': -9.383, 'distance_ly': 5000},
        'M27': {'name': 'Dumbbell Nebula', 'type': 'Planetary Nebula', 'ra': 299.903, 'dec': 22.721, 'distance_ly': 1360},
        'M28': {'name': 'NGC 6626', 'type': 'Globular Cluster', 'ra': 276.525, 'dec': -24.870, 'distance_ly': 18000},
        'M29': {'name': 'NGC 6913', 'type': 'Open Cluster', 'ra': 305.983, 'dec': 38.533, 'distance_ly': 4000},
        'M30': {'name': 'NGC 7099', 'type': 'Globular Cluster', 'ra': 325.092, 'dec': -23.180, 'distance_ly': 26100},
        'M31': {'name': 'Andromeda Galaxy', 'type': 'Galaxy', 'ra': 10.684, 'dec': 41.269, 'distance_ly': 2530000},
        'M32': {'name': 'NGC 221', 'type': 'Galaxy', 'ra': 10.674, 'dec': 40.865, 'distance_ly': 2540000},
        'M33': {'name': 'Triangulum Galaxy', 'type': 'Galaxy', 'ra': 23.462, 'dec': 30.660, 'distance_ly': 3000000},
        'M34': {'name': 'NGC 1039', 'type': 'Open Cluster', 'ra': 40.500, 'dec': 42.783, 'distance_ly': 1400},
        'M35': {'name': 'NGC 2168', 'type': 'Open Cluster', 'ra': 92.250, 'dec': 24.333, 'distance_ly': 2800},
        'M36': {'name': 'NGC 1960', 'type': 'Open Cluster', 'ra': 84.083, 'dec': 34.133, 'distance_ly': 4100},
        'M37': {'name': 'NGC 2099', 'type': 'Open Cluster', 'ra': 88.083, 'dec': 32.550, 'distance_ly': 4400},
        'M38': {'name': 'NGC 1912', 'type': 'Open Cluster', 'ra': 82.083, 'dec': 35.850, 'distance_ly': 4200},
        'M39': {'name': 'NGC 7092', 'type': 'Open Cluster', 'ra': 323.050, 'dec': 48.433, 'distance_ly': 825},
        'M40': {'name': 'Winnecke 4', 'type': 'Double Star', 'ra': 185.617, 'dec': 58.083, 'distance_ly': 510},
        'M41': {'name': 'NGC 2287', 'type': 'Open Cluster', 'ra': 101.500, 'dec': -20.717, 'distance_ly': 2300},
        'M42': {'name': 'Orion Nebula', 'type': 'Emission Nebula', 'ra': 83.822, 'dec': -5.391, 'distance_ly': 1344},
        'M43': {'name': 'De Mairan Nebula', 'type': 'Emission Nebula', 'ra': 83.867, 'dec': -5.267, 'distance_ly': 1600},
        'M44': {'name': 'Beehive Cluster', 'type': 'Open Cluster', 'ra': 130.100, 'dec': 19.667, 'distance_ly': 577},
        'M45': {'name': 'Pleiades', 'type': 'Open Cluster', 'ra': 56.750, 'dec': 24.117, 'distance_ly': 444},
        'M46': {'name': 'NGC 2437', 'type': 'Open Cluster', 'ra': 115.433, 'dec': -14.800, 'distance_ly': 5400},
        'M47': {'name': 'NGC 2422', 'type': 'Open Cluster', 'ra': 114.150, 'dec': -14.500, 'distance_ly': 1600},
        'M48': {'name': 'NGC 2548', 'type': 'Open Cluster', 'ra': 123.433, 'dec': -5.800, 'distance_ly': 1500},
        'M49': {'name': 'NGC 4472', 'type': 'Galaxy', 'ra': 187.444, 'dec': 8.000, 'distance_ly': 60000000},
        'M50': {'name': 'NGC 2323', 'type': 'Open Cluster', 'ra': 105.833, 'dec': -8.333, 'distance_ly': 3200},
        'M51': {'name': 'Whirlpool Galaxy', 'type': 'Galaxy', 'ra': 202.470, 'dec': 47.195, 'distance_ly': 31000000},
        'M52': {'name': 'NGC 7654', 'type': 'Open Cluster', 'ra': 351.200, 'dec': 61.593, 'distance_ly': 5000},
        'M53': {'name': 'NGC 5024', 'type': 'Globular Cluster', 'ra': 198.230, 'dec': 18.168, 'distance_ly': 58400},
        'M54': {'name': 'NGC 6715', 'type': 'Globular Cluster', 'ra': 283.764, 'dec': -30.480, 'distance_ly': 87400},
        'M55': {'name': 'NGC 6809', 'type': 'Globular Cluster', 'ra': 294.999, 'dec': -30.964, 'distance_ly': 17300},
        'M56': {'name': 'NGC 6779', 'type': 'Globular Cluster', 'ra': 289.148, 'dec': 30.184, 'distance_ly': 32900},
        'M57': {'name': 'Ring Nebula', 'type': 'Planetary Nebula', 'ra': 283.396, 'dec': 33.029, 'distance_ly': 2300},
        'M58': {'name': 'NGC 4579', 'type': 'Galaxy', 'ra': 189.431, 'dec': 11.819, 'distance_ly': 68000000},
        'M59': {'name': 'NGC 4621', 'type': 'Galaxy', 'ra': 190.510, 'dec': 11.647, 'distance_ly': 60000000},
        'M60': {'name': 'NGC 4649', 'type': 'Galaxy', 'ra': 190.916, 'dec': 11.552, 'distance_ly': 55000000},
        'M61': {'name': 'NGC 4303', 'type': 'Galaxy', 'ra': 185.479, 'dec': 4.472, 'distance_ly': 52000000},
        'M62': {'name': 'NGC 6266', 'type': 'Globular Cluster', 'ra': 255.303, 'dec': -30.113, 'distance_ly': 22500},
        'M63': {'name': 'Sunflower Galaxy', 'type': 'Galaxy', 'ra': 198.955, 'dec': 42.029, 'distance_ly': 37000000},
        'M64': {'name': 'Black Eye Galaxy', 'type': 'Galaxy', 'ra': 194.183, 'dec': 21.683, 'distance_ly': 24000000},
        'M65': {'name': 'NGC 3623', 'type': 'Galaxy', 'ra': 169.733, 'dec': 13.092, 'distance_ly': 35000000},
        'M66': {'name': 'NGC 3627', 'type': 'Galaxy', 'ra': 170.063, 'dec': 12.992, 'distance_ly': 35000000},
        'M67': {'name': 'NGC 2682', 'type': 'Open Cluster', 'ra': 132.833, 'dec': 11.800, 'distance_ly': 2700},
        'M68': {'name': 'NGC 4590', 'type': 'Globular Cluster', 'ra': 189.867, 'dec': -26.744, 'distance_ly': 33600},
        'M69': {'name': 'NGC 6637', 'type': 'Globular Cluster', 'ra': 277.847, 'dec': -32.348, 'distance_ly': 29700},
        'M70': {'name': 'NGC 6681', 'type': 'Globular Cluster', 'ra': 280.803, 'dec': -32.292, 'distance_ly': 29300},
        'M71': {'name': 'NGC 6838', 'type': 'Globular Cluster', 'ra': 298.443, 'dec': 18.778, 'distance_ly': 13000},
        'M72': {'name': 'NGC 6981', 'type': 'Globular Cluster', 'ra': 313.365, 'dec': -12.537, 'distance_ly': 55400},
        'M73': {'name': 'NGC 6994', 'type': 'Asterism', 'ra': 314.742, 'dec': -12.633, 'distance_ly': 2500},
        'M74': {'name': 'NGC 628', 'type': 'Galaxy', 'ra': 24.174, 'dec': 15.783, 'distance_ly': 32000000},
        'M75': {'name': 'NGC 6864', 'type': 'Globular Cluster', 'ra': 301.520, 'dec': -21.922, 'distance_ly': 67500},
        'M76': {'name': 'Little Dumbbell Nebula', 'type': 'Planetary Nebula', 'ra': 25.575, 'dec': 51.576, 'distance_ly': 3400},
        'M77': {'name': 'NGC 1068', 'type': 'Galaxy', 'ra': 40.670, 'dec': -0.013, 'distance_ly': 47000000},
        'M78': {'name': 'NGC 2068', 'type': 'Reflection Nebula', 'ra': 86.694, 'dec': 0.053, 'distance_ly': 1600},
        'M79': {'name': 'NGC 1904', 'type': 'Globular Cluster', 'ra': 81.044, 'dec': -24.524, 'distance_ly': 42000},
        'M80': {'name': 'NGC 6093', 'type': 'Globular Cluster', 'ra': 244.260, 'dec': -22.976, 'distance_ly': 32600},
        'M81': {'name': 'Bode Galaxy', 'type': 'Galaxy', 'ra': 148.888, 'dec': 69.065, 'distance_ly': 12000000},
        'M82': {'name': 'Cigar Galaxy', 'type': 'Galaxy', 'ra': 148.968, 'dec': 69.680, 'distance_ly': 12000000},
        'M83': {'name': 'Southern Pinwheel', 'type': 'Galaxy', 'ra': 204.254, 'dec': -29.865, 'distance_ly': 15000000},
        'M84': {'name': 'NGC 4374', 'type': 'Galaxy', 'ra': 186.266, 'dec': 12.887, 'distance_ly': 60000000},
        'M85': {'name': 'NGC 4382', 'type': 'Galaxy', 'ra': 186.350, 'dec': 18.191, 'distance_ly': 60000000},
        'M86': {'name': 'NGC 4406', 'type': 'Galaxy', 'ra': 186.548, 'dec': 12.946, 'distance_ly': 52000000},
        'M87': {'name': 'NGC 4486', 'type': 'Galaxy', 'ra': 187.706, 'dec': 12.391, 'distance_ly': 53500000},
        'M88': {'name': 'NGC 4501', 'type': 'Galaxy', 'ra': 188.000, 'dec': 14.420, 'distance_ly': 47000000},
        'M89': {'name': 'NGC 4552', 'type': 'Galaxy', 'ra': 188.916, 'dec': 12.556, 'distance_ly': 50000000},
        'M90': {'name': 'NGC 4569', 'type': 'Galaxy', 'ra': 189.208, 'dec': 13.163, 'distance_ly': 60000000},
        'M91': {'name': 'NGC 4548', 'type': 'Galaxy', 'ra': 188.860, 'dec': 14.496, 'distance_ly': 63000000},
        'M92': {'name': 'NGC 6341', 'type': 'Globular Cluster', 'ra': 259.281, 'dec': 43.136, 'distance_ly': 26700},
        'M93': {'name': 'NGC 2447', 'type': 'Open Cluster', 'ra': 116.167, 'dec': -23.883, 'distance_ly': 3600},
        'M94': {'name': 'NGC 4736', 'type': 'Galaxy', 'ra': 192.721, 'dec': 41.120, 'distance_ly': 14500000},
        'M95': {'name': 'NGC 3351', 'type': 'Galaxy', 'ra': 160.991, 'dec': 11.703, 'distance_ly': 38000000},
        'M96': {'name': 'NGC 3368', 'type': 'Galaxy', 'ra': 161.690, 'dec': 11.820, 'distance_ly': 38000000},
        'M97': {'name': 'Owl Nebula', 'type': 'Planetary Nebula', 'ra': 168.698, 'dec': 55.019, 'distance_ly': 2600},
        'M98': {'name': 'NGC 4192', 'type': 'Galaxy', 'ra': 183.454, 'dec': 14.900, 'distance_ly': 44000000},
        'M99': {'name': 'NGC 4254', 'type': 'Galaxy', 'ra': 184.706, 'dec': 14.417, 'distance_ly': 50000000},
        'M100': {'name': 'NGC 4321', 'type': 'Galaxy', 'ra': 185.729, 'dec': 15.822, 'distance_ly': 55000000},
        'M101': {'name': 'Pinwheel Galaxy', 'type': 'Galaxy', 'ra': 210.802, 'dec': 54.349, 'distance_ly': 27000000},
        'M102': {'name': 'NGC 5866', 'type': 'Galaxy', 'ra': 226.623, 'dec': 55.763, 'distance_ly': 50000000},
        'M103': {'name': 'NGC 581', 'type': 'Open Cluster', 'ra': 23.350, 'dec': 60.717, 'distance_ly': 8000},
        'M104': {'name': 'Sombrero Galaxy', 'type': 'Galaxy', 'ra': 189.998, 'dec': -11.623, 'distance_ly': 28000000},
        'M105': {'name': 'NGC 3379', 'type': 'Galaxy', 'ra': 161.957, 'dec': 12.582, 'distance_ly': 38000000},
        'M106': {'name': 'NGC 4258', 'type': 'Galaxy', 'ra': 184.743, 'dec': 47.304, 'distance_ly': 23800000},
        'M107': {'name': 'NGC 6171', 'type': 'Globular Cluster', 'ra': 248.133, 'dec': -34.987, 'distance_ly': 20900},
        'M108': {'name': 'NGC 3556', 'type': 'Galaxy', 'ra': 168.723, 'dec': 55.674, 'distance_ly': 46000000},
        'M109': {'name': 'NGC 3992', 'type': 'Galaxy', 'ra': 179.400, 'dec': 53.375, 'distance_ly': 83000000},
        'M110': {'name': 'NGC 205', 'type': 'Galaxy', 'ra': 10.092, 'dec': 41.685, 'distance_ly': 2540000}
    }
    
    data_list = []
    
    for messier_id, info in messier_objects.items():
        # Convert RA/Dec to approximate x,y,z coordinates
        ra_rad = np.radians(info['ra'])
        dec_rad = np.radians(info['dec'])
        
        # Convert to light years (approximate)
        distance_ly = info['distance_ly']
        
        # Convert spherical to Cartesian coordinates
        x = distance_ly * np.cos(dec_rad) * np.cos(ra_rad)
        y = distance_ly * np.cos(dec_rad) * np.sin(ra_rad)
        z = distance_ly * np.sin(dec_rad)
        
        data_list.append({
            'name': f"{messier_id} ({info['name']})",
            'object_type': info['type'],
            'distance_from_sun_au': 0,  # Not applicable for deep sky objects
            'x_ly': x,
            'y_ly': y,
            'z_ly': z,
            'ra': info['ra'],
            'dec': info['dec'],
            'distance_ly': distance_ly,
            'mass_earth': 0,  # Not applicable
            'radius_earth': 0,  # Not applicable
            'temperature_k': 0,  # Not applicable
            'orbital_period_days': 0,  # Not applicable
            'semi_major_axis_au': 0,  # Not applicable
            'eccentricity': 0,  # Not applicable
            'insolation_flux': 0,  # Not applicable
            'density_g_cm3': 0  # Not applicable
        })
    
    if data_list:
        df = pd.DataFrame(data_list)
        output_file = RAW_DATA_DIR / "messier_catalog_simple.csv"
        df.to_csv(output_file, index=False)
        print(f"✓ Saved {len(df)} Messier objects to {output_file}")
        return df
    else:
        print("❌ No Messier data retrieved")
        return None

def main():
    """Main data collection function"""
    print("=== Simplified Data Collection ===")
    print("Focusing on core data without problematic Gaia/SIMBAD queries")
    
    # Collect all data
    exoplanets_df = fetch_nasa_exoplanets_simple()
    solar_system_df = fetch_jpl_solar_system_simple()
    messier_df = fetch_messier_catalog_simple()
    
    # Summary
    print("\n=== Data Collection Summary ===")
    print(f"Exoplanets: {'✓ Success' if exoplanets_df is not None else '❌ Failed'}")
    print(f"Solar System: {'✓ Success' if solar_system_df is not None else '❌ Failed'}")
    print(f"Messier Catalog: {'✓ Success' if messier_df is not None else '❌ Failed'}")
    
    if exoplanets_df is not None:
        print(f"  - {len(exoplanets_df)} exoplanet systems")
    if solar_system_df is not None:
        print(f"  - {len(solar_system_df)} Solar System bodies")
    if messier_df is not None:
        print(f"  - {len(messier_df)} Messier objects")
    
    print("\n✓ Simplified data collection completed!")

if __name__ == "__main__":
    main() 