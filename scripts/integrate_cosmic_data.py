"""
integrate_cosmic_data.py
Integrates all collected data sources into a unified cosmic world for exploration.
Combines exoplanets, Gaia stars, SIMBAD names, Solar System, and Messier objects.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import json
from datetime import datetime

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

def load_all_processed_data():
    """Load all available processed data sources"""
    data_sources = {}
    
    # 1. Exoplanets (cleaned)
    try:
        exoplanets_path = PROCESSED_DATA_DIR / "exoplanets_cleaned.parquet"
        if exoplanets_path.exists():
            data_sources['exoplanets'] = pd.read_parquet(exoplanets_path)
            print(f"✓ Loaded {len(data_sources['exoplanets'])} cleaned exoplanets")
        else:
            print("⚠ Cleaned exoplanets data not found")
    except Exception as e:
        print(f"✗ Failed to load cleaned exoplanets: {e}")
    
    # 2. Gaia Host Stars (cleaned)
    try:
        gaia_path = PROCESSED_DATA_DIR / "gaia_host_stars_cleaned.parquet"
        if gaia_path.exists():
            data_sources['gaia_stars'] = pd.read_parquet(gaia_path)
            print(f"✓ Loaded {len(data_sources['gaia_stars'])} cleaned Gaia stars")
        else:
            print("⚠ Cleaned Gaia stars data not found")
    except Exception as e:
        print(f"✗ Failed to load cleaned Gaia stars: {e}")
    
    # 3. SIMBAD Names (from raw, as it's not processed)
    try:
        simbad_path = RAW_DATA_DIR / "simbad_names.csv"
        if simbad_path.exists():
            simbad_df = pd.read_csv(simbad_path)
            if len(simbad_df) > 0:
                data_sources['simbad_names'] = simbad_df
                print(f"✓ Loaded {len(simbad_df)} SIMBAD names")
                if 'star_names' in simbad_df.columns:
                    examples = simbad_df[simbad_df['has_common_name'] == True].head(3)
                    for _, row in examples.iterrows():
                        print(f"  Example: Gaia {row['gaia_id']} -> {row['star_names']}")
            else:
                print("⚠ SIMBAD names file is empty")
        else:
            print("⚠ SIMBAD names data not found")
    except Exception as e:
        print(f"✗ Failed to load SIMBAD names: {e}")
    
    # 4. Solar System (cleaned)
    try:
        solar_path = PROCESSED_DATA_DIR / "solar_system_cleaned.parquet"
        if solar_path.exists():
            data_sources['solar_system'] = pd.read_parquet(solar_path)
            print(f"✓ Loaded {len(data_sources['solar_system'])} cleaned Solar System objects")
        else:
            print("⚠ Cleaned Solar System data not found")
    except Exception as e:
        print(f"✗ Failed to load cleaned Solar System: {e}")
    
    # 5. Messier Catalog (cleaned)
    try:
        messier_path = PROCESSED_DATA_DIR / "messier_catalog_cleaned.parquet"
        if messier_path.exists():
            data_sources['messier'] = pd.read_parquet(messier_path)
            print(f"✓ Loaded {len(data_sources['messier'])} cleaned Messier objects")
        else:
            print("⚠ Cleaned Messier catalog not found")
    except Exception as e:
        print(f"✗ Failed to load cleaned Messier catalog: {e}")
    
    return data_sources

def create_star_catalog(gaia_stars, simbad_names=None):
    """Create a comprehensive star catalog with names"""
    print("\n🔭 Creating comprehensive star catalog...")
    
    # Start with Gaia stars
    star_catalog = gaia_stars.copy()
    
    # Add SIMBAD names if available
    if simbad_names is not None and len(simbad_names) > 0:
        try:
            # Ensure merge keys are the same data type to prevent merge failures
            star_catalog['source_id'] = pd.to_numeric(star_catalog['source_id'], errors='coerce')
            simbad_names['gaia_id'] = pd.to_numeric(simbad_names['gaia_id'], errors='coerce')
    
            # Merge with SIMBAD data (robust to missing columns)
            simbad_cols = ['gaia_id', 'star_names', 'simbad_names', 'main_id', 'object_type', 'has_common_name']
            available_cols = [col for col in simbad_cols if col in simbad_names.columns]
            missing_cols = [col for col in simbad_cols if col not in simbad_names.columns]
            if missing_cols:
                print(f"[WARN] SIMBAD data missing columns: {missing_cols}. Merge will use available columns only.")
            star_catalog = star_catalog.merge(
                simbad_names[available_cols],
                left_on='source_id',
                right_on='gaia_id',
                how='left'
            )
            
            # Fill missing values for stars that didn't have a SIMBAD match
            star_catalog['object_type'] = star_catalog['object_type'].fillna('Star')
            star_catalog['has_common_name'] = star_catalog['has_common_name'].fillna(False)
            # Use a more modern approach for filling multiple columns that avoids future warnings
            fill_values = {'star_names': '', 'simbad_names': '', 'main_id': ''}
            star_catalog = star_catalog.fillna(value=fill_values)
        except Exception as e:
            print(f"✗ CRITICAL: Failed to merge Gaia and SIMBAD data: {e}")
            print("  Falling back to using Gaia IDs as names.")
            star_catalog['display_name'] = star_catalog['source_id'].astype(str)
            star_catalog['star_names'] = ''
            star_catalog['simbad_names'] = ''
            star_catalog['main_id'] = ''
            star_catalog['object_type'] = 'Star'
            star_catalog['has_common_name'] = False

        # Create display names
        def create_display_name(row):
            if pd.notna(row.get('star_names')) and row['star_names']:
                return row['star_names']
            elif pd.notna(row.get('main_id')) and row['main_id'] != str(row['source_id']):
                return row['main_id']
            else:
                return f"Gaia {row['source_id']}"
        
        star_catalog['display_name'] = star_catalog.apply(create_display_name, axis=1)
        
        # Count stars with common names
        named_stars = star_catalog[star_catalog['has_common_name'] == True]
        print(f"  Found {len(named_stars)} stars with common names")
        
        # Show some examples
        print("  Examples of named stars:")
        for _, star in named_stars.head(5).iterrows():
            print(f"    {star['display_name']} (Gaia {star['source_id']})")
    else:
        # Fallback: use Gaia IDs as names
        star_catalog['display_name'] = star_catalog['source_id'].astype(str)
        star_catalog['star_names'] = ''
        star_catalog['simbad_names'] = ''
        star_catalog['main_id'] = ''
        star_catalog['object_type'] = 'Star'
        star_catalog['has_common_name'] = False
    
    # Add star type classification
    def classify_star(row):
        if pd.notna(row.get('teff_gspphot')):
            teff = row['teff_gspphot']
            if teff >= 30000:
                return 'O-type'
            elif teff >= 10000:
                return 'B-type'
            elif teff >= 7500:
                return 'A-type'
            elif teff >= 6000:
                return 'F-type'
            elif teff >= 5200:
                return 'G-type'
            elif teff >= 3700:
                return 'K-type'
            else:
                return 'M-type'
        else:
            return 'Unknown'
    
    star_catalog['star_type'] = star_catalog.apply(classify_star, axis=1)
    
    # Add distance in light years (if parallax available)
    def calculate_distance_ly(row):
        if pd.notna(row.get('parallax')) and row['parallax'] > 0:
            # Correct formula: dist(ly) = (1000 / parallax_mas) * 3.26156
            dist_pc = 1000 / row['parallax']
            return dist_pc * 3.26156
        else:
            return np.nan
    
    star_catalog['distance_ly'] = star_catalog.apply(calculate_distance_ly, axis=1)
    
    print(f"  Created catalog with {len(star_catalog)} stars")
    return star_catalog

def create_exoplanet_catalog(exoplanets, star_catalog):
    """Create exoplanet catalog with host star information"""
    print("\n🪐 Creating exoplanet catalog...")
    
    # Clean exoplanet data
    exoplanet_catalog = exoplanets.copy()
    
    # Ensure gaia_id in exoplanet data is a consistent integer type for merging
    if 'gaia_id' in exoplanet_catalog.columns:
        exoplanet_catalog['gaia_id'] = pd.to_numeric(exoplanet_catalog['gaia_id'], errors='coerce').astype('Int64')

    # Add host star information
    if 'gaia_id' in exoplanet_catalog.columns and 'source_id' in star_catalog.columns:
        # Prepare star_catalog for merging by ensuring its key is also the correct type
        star_catalog_for_merge = star_catalog.copy()
        star_catalog_for_merge['source_id'] = pd.to_numeric(star_catalog_for_merge['source_id'], errors='coerce').astype('Int64')

        # Drop rows with NaN gaia_id from exoplanets as they cannot be merged
        exoplanet_catalog.dropna(subset=['gaia_id'], inplace=True)

        # Merge with star catalog using Gaia ID
        exoplanet_catalog = exoplanet_catalog.merge(
            star_catalog_for_merge[['source_id', 'display_name', 'star_names', 'star_type', 'distance_ly', 'teff_gspphot']],
            left_on='gaia_id',
            right_on='source_id',
            how='left',
            suffixes=('', '_host')
        )
        
        # Create planet display names
        def create_planet_name(row):
            host_name = row.get('display_name')
            if pd.isna(host_name):
                host_name = f"Gaia ID {row.get('gaia_id', 'Unknown')}" # Fallback if no star match found
            
            planet_name = row.get('pl_name', 'Unknown Planet')
            return f"{planet_name}"
        
        exoplanet_catalog['planet_display_name'] = exoplanet_catalog.apply(create_planet_name, axis=1)
        
        # Report on merge success
        unmatched_planets = exoplanet_catalog['source_id'].isna().sum()
        if unmatched_planets > 0:
            print(f"  Warning: {unmatched_planets} exoplanets could not be matched with a Gaia host star.")

    else:
        print("  Skipping host star merge: 'gaia_id' not in exoplanet data or 'source_id' not in star catalog.")
        exoplanet_catalog['planet_display_name'] = exoplanet_catalog.get('pl_name', 'Unknown Planet')

    # Add planet classification
    def classify_planet(row):
        if pd.notna(row.get('pl_rade')):
            radius = row['pl_rade']
            if radius < 1.25:
                return 'Terrestrial'
            elif radius < 2.0:
                return 'Super-Earth'
            elif radius < 6.0:
                return 'Neptune-like'
            else:
                return 'Gas Giant'
        else:
            return 'Unknown'
    
    exoplanet_catalog['planet_type'] = exoplanet_catalog.apply(classify_planet, axis=1)
    
    # Add habitability indicators
    def calculate_habitability(row):
        if pd.notna(row.get('pl_eqt')):
            temp = row['pl_eqt']
            if 200 <= temp <= 400:  # Roughly habitable temperature range
                return 'Potentially Habitable'
            elif temp < 200:
                return 'Too Cold'
            else:
                return 'Too Hot'
        else:
            return 'Unknown'
    
    exoplanet_catalog['habitability'] = exoplanet_catalog.apply(calculate_habitability, axis=1)
    
    print(f"  Created catalog with {len(exoplanet_catalog)} exoplanets")
    return exoplanet_catalog

def create_solar_system_catalog(solar_system):
    """Create Solar System catalog with enhanced information"""
    print("\n☀️ Creating Solar System catalog...")
    
    solar_catalog = solar_system.copy()
    
    # Add display names
    solar_catalog['display_name'] = solar_catalog['name']
    
    # Add interesting facts
    solar_facts = {
        'Sun': 'Our star, provides light and energy to all planets',
        'Mercury': 'Closest planet to the Sun, extreme temperature variations',
        'Venus': 'Hottest planet, thick atmosphere of carbon dioxide',
        'Earth': 'Our home planet, only known world with life',
        'Mars': 'Red planet, target for human exploration',
        'Jupiter': 'Largest planet, gas giant with many moons',
        'Saturn': 'Ringed planet, beautiful ring system',
        'Uranus': 'Ice giant, rotates on its side',
        'Neptune': 'Windiest planet, deep blue color',
        'Pluto': 'Dwarf planet, former ninth planet'
    }
    
    solar_catalog['description'] = solar_catalog['name'].map(solar_facts)
    
    print(f"  Created catalog with {len(solar_catalog)} Solar System objects")
    return solar_catalog

def create_messier_catalog(messier):
    """Create Messier catalog with enhanced information"""
    print("\n🌌 Creating Messier catalog...")
    
    messier_catalog = messier.copy()
    
    # Add display names
    messier_catalog['display_name'] = messier_catalog['name']
    
    # Add object descriptions
    def get_messier_description(row):
        obj_type = row.get('type', '').lower()
        if 'galaxy' in obj_type:
            return 'Distant galaxy with billions of stars'
        elif 'nebula' in obj_type:
            return 'Cloud of gas and dust, stellar nursery'
        elif 'cluster' in obj_type:
            return 'Group of stars bound by gravity'
        else:
            return 'Deep sky object'
    
    messier_catalog['description'] = messier_catalog.apply(get_messier_description, axis=1)
    
    print(f"  Created catalog with {len(messier_catalog)} Messier objects")
    return messier_catalog

def create_unified_cosmic_world(data_sources):
    """Create a unified cosmic world combining all data sources"""
    print("\n🌌 Creating unified cosmic world...")
    
    cosmic_world = {
        'metadata': {
            'created_at': datetime.now().isoformat(),
            'data_sources': list(data_sources.keys()),
            'total_objects': 0
        },
        'stars': {},
        'exoplanets': {},
        'solar_system': {},
        'deep_sky_objects': {}
    }
    
    # Process stars
    if 'gaia_stars' in data_sources:
        star_catalog = create_star_catalog(
            data_sources['gaia_stars'], 
            data_sources.get('simbad_names')
        )
        cosmic_world['stars'] = {
            'catalog': star_catalog.to_dict('records'),
            'count': len(star_catalog),
            'named_stars': len(star_catalog[star_catalog['has_common_name'] == True]) if 'has_common_name' in star_catalog.columns else 0
        }
        cosmic_world['metadata']['total_objects'] += len(star_catalog)
    
    # Process exoplanets
    if 'exoplanets' in data_sources and 'gaia_stars' in data_sources:
        exoplanet_catalog = create_exoplanet_catalog(
            data_sources['exoplanets'], 
            star_catalog
        )
        cosmic_world['exoplanets'] = {
            'catalog': exoplanet_catalog.to_dict('records'),
            'count': len(exoplanet_catalog),
            'habitable': len(exoplanet_catalog[exoplanet_catalog['habitability'] == 'Potentially Habitable'])
        }
        cosmic_world['metadata']['total_objects'] += len(exoplanet_catalog)
    
    # Process Solar System
    if 'solar_system' in data_sources:
        solar_catalog = create_solar_system_catalog(data_sources['solar_system'])
        cosmic_world['solar_system'] = {
            'catalog': solar_catalog.to_dict('records'),
            'count': len(solar_catalog)
        }
        cosmic_world['metadata']['total_objects'] += len(solar_catalog)
    
    # Process Messier objects
    if 'messier' in data_sources:
        messier_catalog = create_messier_catalog(data_sources['messier'])
        cosmic_world['deep_sky_objects'] = {
            'catalog': messier_catalog.to_dict('records'),
            'count': len(messier_catalog)
        }
        cosmic_world['metadata']['total_objects'] += len(messier_catalog)
    
    return cosmic_world

def save_cosmic_world(cosmic_world):
    """Save the unified cosmic world to various formats"""
    print("\n💾 Saving cosmic world...")

    # Save as JSON for easy access
    json_path = PROCESSED_DATA_DIR / "cosmic_world.json"
    with open(json_path, 'w') as f:
        json.dump(cosmic_world, f, indent=2, default=str)
    print(f"  Saved: {json_path}")

    # Save individual catalogs as CSV for analysis
    if 'stars' in cosmic_world and 'catalog' in cosmic_world['stars'] and cosmic_world['stars']['catalog']:
        stars_df = pd.DataFrame(cosmic_world['stars']['catalog'])
        stars_df.to_csv(PROCESSED_DATA_DIR / "stars_catalog.csv", index=False)
        print(f"  Saved: {PROCESSED_DATA_DIR / 'stars_catalog.csv'}")

    if 'exoplanets' in cosmic_world and 'catalog' in cosmic_world['exoplanets'] and cosmic_world['exoplanets']['catalog']:
        exoplanets_df = pd.DataFrame(cosmic_world['exoplanets']['catalog'])
        exoplanets_df.to_csv(PROCESSED_DATA_DIR / "exoplanets_catalog.csv", index=False)
        print(f"  Saved: {PROCESSED_DATA_DIR / 'exoplanets_catalog.csv'}")

    if 'solar_system' in cosmic_world and 'catalog' in cosmic_world['solar_system'] and cosmic_world['solar_system']['catalog']:
        solar_df = pd.DataFrame(cosmic_world['solar_system']['catalog'])
        solar_df.to_csv(PROCESSED_DATA_DIR / "solar_system_catalog.csv", index=False)
        print(f"  Saved: {PROCESSED_DATA_DIR / 'solar_system_catalog.csv'}")

    if 'deep_sky_objects' in cosmic_world and 'catalog' in cosmic_world['deep_sky_objects'] and cosmic_world['deep_sky_objects']['catalog']:
        messier_df = pd.DataFrame(cosmic_world['deep_sky_objects']['catalog'])
        messier_df.to_csv(PROCESSED_DATA_DIR / "messier_catalog.csv", index=False)
        print(f"  Saved: {PROCESSED_DATA_DIR / 'messier_catalog.csv'}")

def main():
    """Main function to integrate all cosmic data"""
    print("🌌 Cosmic Data Integration")
    print("=" * 50)
    
    # Load all data sources
    data_sources = load_all_processed_data()
    
    if not data_sources:
        print("❌ No data sources found. Please run collect_data.py first.")
        return
    
    # Create unified cosmic world
    cosmic_world = create_unified_cosmic_world(data_sources)
    
    # Save the cosmic world
    save_cosmic_world(cosmic_world)
    
    # Print summary
    print("\n🎉 Cosmic World Creation Complete!")
    print("=" * 50)
    print(f"Total objects: {cosmic_world['metadata']['total_objects']}")
    
    if cosmic_world['stars']['catalog']:
        print(f"Stars: {cosmic_world['stars']['count']} (including {cosmic_world['stars']['named_stars']} with common names)")
    
    if cosmic_world['exoplanets']['catalog']:
        print(f"Exoplanets: {cosmic_world['exoplanets']['count']} (including {cosmic_world['exoplanets']['habitable']} potentially habitable)")
    
    if cosmic_world['solar_system']['catalog']:
        print(f"Solar System objects: {cosmic_world['solar_system']['count']}")
    
    if cosmic_world['deep_sky_objects']['catalog']:
        print(f"Deep sky objects: {cosmic_world['deep_sky_objects']['count']}")
    
    print(f"\nData saved to: {PROCESSED_DATA_DIR}")
    print("Ready for cosmic exploration! 🚀")

if __name__ == "__main__":
    main() 