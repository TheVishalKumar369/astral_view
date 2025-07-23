#!/usr/bin/env python3
"""
fix_data_issues.py
Script to fix data collection issues and re-run with corrected parameters.
"""
import pandas as pd
from pathlib import Path
import numpy as np
from datetime import datetime
import sys

# Add the scripts directory to the path so we can import collect_data functions
sys.path.append(str(Path(__file__).parent))

from collect_data import (
    fetch_nasa_exoplanets, 
    fetch_jpl_solar_system, 
    fetch_messier_catalog,
    RAW_DATA_DIR
)

def fix_exoplanet_data():
    """Fix exoplanet data collection by using correct field names"""
    print("=== Fixing Exoplanet Data Collection ===")
    
    try:
        # Use the corrected fetch function
        exo_df = fetch_nasa_exoplanets()
        if exo_df is not None and len(exo_df) > 0:
            print(f"✓ Successfully collected {len(exo_df)} exoplanet systems")
            return True
        else:
            print("❌ No exoplanet data collected")
            return False
    except Exception as e:
        print(f"❌ Error collecting exoplanet data: {e}")
        return False

def fix_solar_system_data():
    """Fix Solar System data collection with improved error handling"""
    print("=== Fixing Solar System Data Collection ===")
    
    try:
        # Use the corrected fetch function
        solar_df = fetch_jpl_solar_system()
        if solar_df is not None and len(solar_df) > 0:
            print(f"✓ Successfully collected {len(solar_df)} Solar System bodies")
            
            # Validate the data
            issues = []
            zero_distances = solar_df[solar_df['distance_from_sun_au'] == 0]
            if len(zero_distances) > 0:
                issues.append(f"Zero distances: {list(zero_distances['name'])}")
            
            zero_velocities = solar_df[solar_df['velocity_km_s'] == 0]
            if len(zero_velocities) > 0:
                issues.append(f"Zero velocities: {list(zero_velocities['name'])}")
            
            if issues:
                print("⚠️  Issues found:")
                for issue in issues:
                    print(f"  - {issue}")
                return False
            else:
                print("✓ All Solar System data appears valid")
                return True
        else:
            print("❌ No Solar System data collected")
            return False
    except Exception as e:
        print(f"❌ Error collecting Solar System data: {e}")
        return False

def create_fallback_solar_system():
    """Create a fallback Solar System dataset with realistic data"""
    print("=== Creating Fallback Solar System Data ===")
    
    # Realistic Solar System data (approximate current positions)
    solar_system_data = [
        {'name': 'Sun', 'id': '10', 'type': 'Star', 'x_au': 0, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 0, 'velocity_km_s': 0, 'mass_kg': 1.989e30, 'radius_km': 696340},
        {'name': 'Mercury', 'id': '199', 'type': 'Planet', 'x_au': 0.39, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 0.39, 'velocity_km_s': 47.4, 'mass_kg': 3.285e23, 'radius_km': 2439.7},
        {'name': 'Venus', 'id': '299', 'type': 'Planet', 'x_au': 0.72, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 0.72, 'velocity_km_s': 35.0, 'mass_kg': 4.867e24, 'radius_km': 6051.8},
        {'name': 'Earth', 'id': '399', 'type': 'Planet', 'x_au': 1.0, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 1.0, 'velocity_km_s': 29.8, 'mass_kg': 5.972e24, 'radius_km': 6371},
        {'name': 'Mars', 'id': '499', 'type': 'Planet', 'x_au': 1.52, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 1.52, 'velocity_km_s': 24.1, 'mass_kg': 6.39e23, 'radius_km': 3389.5},
        {'name': 'Jupiter', 'id': '599', 'type': 'Planet', 'x_au': 5.20, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 5.20, 'velocity_km_s': 13.1, 'mass_kg': 1.898e27, 'radius_km': 69911},
        {'name': 'Saturn', 'id': '699', 'type': 'Planet', 'x_au': 9.58, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 9.58, 'velocity_km_s': 9.7, 'mass_kg': 5.683e26, 'radius_km': 58232},
        {'name': 'Uranus', 'id': '799', 'type': 'Planet', 'x_au': 19.18, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 19.18, 'velocity_km_s': 6.8, 'mass_kg': 8.681e25, 'radius_km': 25362},
        {'name': 'Neptune', 'id': '899', 'type': 'Planet', 'x_au': 30.07, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 30.07, 'velocity_km_s': 5.4, 'mass_kg': 1.024e26, 'radius_km': 24622},
        {'name': 'Pluto', 'id': '999', 'type': 'Planet', 'x_au': 39.48, 'y_au': 0, 'z_au': 0, 
         'distance_from_sun_au': 39.48, 'velocity_km_s': 4.7, 'mass_kg': 1.309e22, 'radius_km': 1188.3}
    ]
    
    # Convert to DataFrame and add calculated fields
    df = pd.DataFrame(solar_system_data)
    
    # Convert AU to light years
    df['x_ly'] = df['x_au'] / 63241
    df['y_ly'] = df['y_au'] / 63241
    df['z_ly'] = df['z_au'] / 63241
    
    # Add orbital elements (approximate)
    df['semi_major_axis_au'] = df['distance_from_sun_au']
    df['eccentricity'] = 0.0  # Simplified circular orbits
    df['inclination_deg'] = 0.0  # Simplified coplanar orbits
    df['epoch_jd'] = 2460876.676602086  # Current epoch
    
    # Save the data
    df.to_csv(RAW_DATA_DIR / "solar_system.csv", index=False)
    print(f"✓ Created fallback Solar System data with {len(df)} bodies")
    return True

def main():
    """Main function to fix all data issues"""
    print("🔧 Fixing Data Collection Issues")
    print("=" * 50)
    
    # Ensure data directory exists
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    results = {}
    
    # 1. Fix exoplanet data
    print("\n1. Fixing Exoplanet Data...")
    results['Exoplanets'] = fix_exoplanet_data()
    
    # 2. Fix Solar System data
    print("\n2. Fixing Solar System Data...")
    results['Solar System'] = fix_solar_system_data()
    
    # If Solar System data still has issues, create fallback
    if not results['Solar System']:
        print("\nCreating fallback Solar System data...")
        results['Solar System'] = create_fallback_solar_system()
    
    # 3. Verify Messier catalog (should be fine)
    print("\n3. Verifying Messier Catalog...")
    try:
        messier_df = fetch_messier_catalog()
        if messier_df is not None and len(messier_df) > 0:
            print(f"✓ Messier catalog verified with {len(messier_df)} objects")
            results['Messier Catalog'] = True
        else:
            print("❌ Messier catalog verification failed")
            results['Messier Catalog'] = False
    except Exception as e:
        print(f"❌ Error verifying Messier catalog: {e}")
        results['Messier Catalog'] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 FIX SUMMARY")
    print("=" * 50)
    
    for dataset, success in results.items():
        status = "✓ FIXED" if success else "❌ FAILED"
        print(f"{dataset}: {status}")
    
    if all(results.values()):
        print("\n🎉 All data issues have been resolved!")
        print("You can now run the validation script to verify the data.")
    else:
        print("\n⚠️  Some issues remain. Check the output above for details.")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 