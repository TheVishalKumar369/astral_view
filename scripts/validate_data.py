"""
validate_data.py
Data validation script for Cosmic Explorer.
Checks quality, completeness, and validity of collected astronomical data.
"""
import pandas as pd
import numpy as np
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns

# Configure matplotlib for headless operation
import matplotlib
matplotlib.use('Agg')
plt.ioff()

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")

def validate_solar_system():
    """Validate Solar System data"""
    print("\n=== Validating Solar System Data ===")
    
    try:
        df = pd.read_csv(RAW_DATA_DIR / "solar_system.csv")
        print(f"✓ Loaded {len(df)} Solar System bodies")
        
        # Check for invalid data
        issues = []
        
        # Check for zero distances (invalid)
        zero_distances = df[df['distance_from_sun_au'] == 0]
        if len(zero_distances) > 0:
            issues.append(f"❌ {len(zero_distances)} bodies have zero distance from Sun: {list(zero_distances['name'])}")
        
        # Check for zero velocities (invalid)
        zero_velocities = df[df['velocity_km_s'] == 0]
        if len(zero_velocities) > 0:
            issues.append(f"❌ {len(zero_velocities)} bodies have zero velocity: {list(zero_velocities['name'])}")
        
        # Check data ranges
        print("\nData Ranges:")
        if 'distance_from_sun_au' in df.columns:
            valid_dist = df['distance_from_sun_au'].dropna()
            if len(valid_dist) > 0:
                print(f"  Distance from Sun: {valid_dist.min():.3f} to {valid_dist.max():.3f} AU")
        
        if 'velocity_km_s' in df.columns:
            valid_vel = df['velocity_km_s'].dropna()
            if len(valid_vel) > 0:
                print(f"  Velocity: {valid_vel.min():.1f} to {valid_vel.max():.1f} km/s")
        
        # Check position data
        if all(col in df.columns for col in ['x_au', 'y_au', 'z_au']):
            print(f"  Position range: X({df['x_au'].min():.3f} to {df['x_au'].max():.3f}) AU")
            print(f"                Y({df['y_au'].min():.3f} to {df['y_au'].max():.3f}) AU")
            print(f"                Z({df['z_au'].min():.3f} to {df['z_au'].max():.3f}) AU")
        
        if issues:
            print("\nIssues Found:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("✓ All Solar System data appears valid")
            return True
            
    except Exception as e:
        print(f"❌ Error validating Solar System data: {e}")
        return False

def validate_messier_catalog():
    """Validate Messier Catalog data"""
    print("\n=== Validating Messier Catalog Data ===")
    
    try:
        df = pd.read_csv(RAW_DATA_DIR / "messier_catalog.csv")
        print(f"✓ Loaded {len(df)} Messier objects")
        
        # Check key columns
        key_cols = ['M_number', 'name', 'ra', 'dec', 'type', 'distance_ly']
        missing_cols = [col for col in key_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing key columns: {missing_cols}")
            return False
        else:
            print("✓ All key columns present")
        
        # Check data completeness
        print("\nData Completeness:")
        for col in key_cols:
            non_null = df[col].notna().sum()
            completeness = non_null / len(df) * 100
            print(f"  {col}: {completeness:.1f}% ({non_null}/{len(df)})")
        
        # Check data ranges
        print("\nData Ranges:")
        if 'distance_ly' in df.columns:
            valid_dist = df['distance_ly'].dropna()
            if len(valid_dist) > 0:
                print(f"  Distance: {valid_dist.min():.0f} to {valid_dist.max():.0f} LY")
        
        if 'ra' in df.columns and 'dec' in df.columns:
            print(f"  RA: {df['ra'].min():.2f}° to {df['ra'].max():.2f}°")
            print(f"  Dec: {df['dec'].min():.2f}° to {df['dec'].max():.2f}°")
        
        # Check object types
        print("\nObject Types:")
        type_counts = df['type'].value_counts()
        for obj_type, count in type_counts.items():
            print(f"  {obj_type}: {count} objects")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating Messier catalog data: {e}")
        return False

def validate_exoplanets():
    """Validate Exoplanet data"""
    print("\n=== Validating Exoplanet Data ===")
    
    try:
        df = pd.read_csv(RAW_DATA_DIR / "nasa_exoplanets.csv")
        print(f"✓ Loaded {len(df)} exoplanet systems")
        
        # Check key columns
        key_cols = ['pl_name', 'hostname', 'sy_dist', 'ra', 'dec']
        missing_cols = [col for col in key_cols if col not in df.columns]
        
        if missing_cols:
            print(f"❌ Missing key columns: {missing_cols}")
            return False
        else:
            print("✓ All key columns present")
        
        # Check data completeness
        print("\nData Completeness:")
        for col in key_cols:
            non_null = df[col].notna().sum()
            completeness = non_null / len(df) * 100
            print(f"  {col}: {completeness:.1f}% ({non_null}/{len(df)})")
        
        # Check data ranges
        print("\nData Ranges:")
        if 'sy_dist' in df.columns:
            valid_dist = df['sy_dist'].dropna()
            if len(valid_dist) > 0:
                print(f"  Distance: {valid_dist.min():.2f} to {valid_dist.max():.2f} pc")
        
        if 'ra' in df.columns and 'dec' in df.columns:
            print(f"  RA: {df['ra'].min():.2f}° to {df['ra'].max():.2f}°")
            print(f"  Dec: {df['dec'].min():.2f}° to {df['dec'].max():.2f}°")
        
        return True
        
    except Exception as e:
        print(f"❌ Error validating exoplanet data: {e}")
        return False

def create_data_summary():
    """Create a comprehensive data summary"""
    print("\n=== Data Summary Report ===")
    
    summary = {
        'messier_catalog': {'status': 'Unknown', 'count': 0, 'file': 'messier_catalog.csv'},
        'solar_system': {'status': 'Unknown', 'count': 0, 'file': 'solar_system.csv'},
        'exoplanets': {'status': 'Unknown', 'count': 0, 'file': 'nasa_exoplanets.csv'},
        'gaia_host_stars': {'status': 'Unknown', 'count': 0, 'file': 'gaia_host_stars_raw.csv'},
        'gaia_background': {'status': 'Unknown', 'count': 0, 'file': 'gaia_background_stars_raw.csv'},
        'simbad_names': {'status': 'Unknown', 'count': 0, 'file': 'simbad_names.csv'}
    }
    
    for dataset, info in summary.items():
        file_path = RAW_DATA_DIR / info['file']
        if file_path.exists():
            try:
                df = pd.read_csv(file_path)
                info['count'] = len(df)
                info['status'] = 'Available'
                print(f"✓ {dataset}: {len(df)} records")
            except Exception as e:
                info['status'] = f'Error: {e}'
                print(f"❌ {dataset}: Error reading file")
        else:
            info['status'] = 'Missing'
            print(f"⚠ {dataset}: File not found")
    
    return summary

def generate_visualizations():
    """Generate data visualization plots"""
    print("\n=== Generating Visualizations ===")
    
    # Create processed directory if it doesn't exist
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    try:
        # Messier Catalog visualization
        messier_df = pd.read_csv(RAW_DATA_DIR / "messier_catalog.csv")
        
        # Distance distribution
        plt.figure(figsize=(12, 8))
        
        plt.subplot(2, 2, 1)
        plt.hist(messier_df['distance_ly'], bins=20, alpha=0.7, color='skyblue')
        plt.xlabel('Distance (Light Years)')
        plt.ylabel('Number of Objects')
        plt.title('Messier Objects Distance Distribution')
        plt.yscale('log')
        
        # Magnitude distribution
        plt.subplot(2, 2, 2)
        plt.hist(messier_df['apparent_magnitude'], bins=20, alpha=0.7, color='orange')
        plt.xlabel('Apparent Magnitude')
        plt.ylabel('Number of Objects')
        plt.title('Messier Objects Magnitude Distribution')
        
        # Object types
        plt.subplot(2, 2, 3)
        type_counts = messier_df['type'].value_counts()
        plt.pie(type_counts.values, labels=type_counts.index, autopct='%1.1f%%')
        plt.title('Messier Objects by Type')
        
        # RA vs Dec scatter
        plt.subplot(2, 2, 4)
        plt.scatter(messier_df['ra'], messier_df['dec'], alpha=0.6, s=20)
        plt.xlabel('Right Ascension (degrees)')
        plt.ylabel('Declination (degrees)')
        plt.title('Messier Objects Sky Distribution')
        
        plt.tight_layout()
        plt.savefig(PROCESSED_DATA_DIR / "messier_analysis.png", dpi=300, bbox_inches='tight')
        plt.close()
        print("✓ Generated Messier Catalog visualizations")
        
    except Exception as e:
        print(f"❌ Error generating visualizations: {e}")

def main():
    """Main validation function"""
    print("=== Data Validation Report ===")
    
    results = {}
    
    # Check if data directory exists
    if not RAW_DATA_DIR.exists():
        print(f"❌ Data directory not found: {RAW_DATA_DIR}")
        return
    
    # Validate each dataset
    results['Solar System'] = validate_solar_system()
    results['Messier Catalog'] = validate_messier_catalog()
    
    # Check for exoplanet data
    exoplanet_file = RAW_DATA_DIR / "nasa_exoplanets.csv"
    if exoplanet_file.exists():
        results['Exoplanets'] = validate_exoplanets()
    else:
        print("\n=== Exoplanet Data ===")
        print("❌ No exoplanet data file found")
        results['Exoplanets'] = False
    
    # Summary
    print("\n=== Validation Summary ===")
    for dataset, is_valid in results.items():
        status = "✓ PASS" if is_valid else "❌ FAIL"
        print(f"{dataset}: {status}")
    
    if all(results.values()):
        print("\n🎉 All datasets are valid!")
    else:
        print("\n⚠️  Some datasets have issues that need attention.")
        print("Recommendation: Re-run data collection with the fixed scripts.")

if __name__ == "__main__":
    main() 