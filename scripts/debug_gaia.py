#!/usr/bin/env python3
"""
Debug script to diagnose Gaia data collection issues
"""
import pandas as pd
from pathlib import Path
import re

RAW_DATA_DIR = Path("/workspace/data/raw")

def debug_gaia_issues():
    """Debug Gaia data collection issues"""
    print("=== Gaia Data Collection Debug ===")
    
    # Check if NASA exoplanet data exists
    nasa_file = RAW_DATA_DIR / "nasa_exoplanets.csv"
    if not nasa_file.exists():
        print("❌ NASA exoplanet data file not found")
        return
    
    print("✅ NASA exoplanet data file found")
    exo_df = pd.read_csv(nasa_file)
    print(f"📊 Loaded {len(exo_df)} exoplanet systems")
    print(f"📋 Available columns: {list(exo_df.columns)}")
    
    # Check for Gaia ID columns
    gaia_columns = [col for col in exo_df.columns if 'gaia' in col.lower() or 'source' in col.lower()]
    print(f"\n🔍 Gaia-related columns found: {gaia_columns}")
    
    for col in gaia_columns:
        non_null = exo_df[col].notna().sum()
        print(f"  - {col}: {non_null}/{len(exo_df)} non-null values")
        if non_null > 0:
            sample_values = exo_df[col].dropna().head(5).tolist()
            print(f"    Sample values: {sample_values}")
    
    # Test Gaia ID extraction
    if 'gaia_id' in exo_df.columns:
        print(f"\n🔧 Testing Gaia ID extraction from 'gaia_id' column:")
        gaia_ids = []
        for idx, gaia_id in enumerate(exo_df['gaia_id'].dropna()):
            try:
                if isinstance(gaia_id, str):
                    match = re.search(r'(\d+)', str(gaia_id))
                    if match:
                        gaia_ids.append(int(match.group(1)))
                        if len(gaia_ids) <= 3:  # Show first few successful extractions
                            print(f"    ✅ '{gaia_id}' -> {int(match.group(1))}")
                    else:
                        print(f"    ❌ '{gaia_id}' -> No numeric match")
                elif isinstance(gaia_id, (int, float)):
                    gaia_ids.append(int(gaia_id))
                    if len(gaia_ids) <= 3:
                        print(f"    ✅ {gaia_id} -> {int(gaia_id)}")
            except Exception as e:
                print(f"    ❌ Error processing '{gaia_id}': {e}")
        
        print(f"📈 Successfully extracted {len(gaia_ids)} valid Gaia IDs")
        if gaia_ids:
            print(f"📝 Sample Gaia IDs: {gaia_ids[:5]}")
    
    # Test Gaia connection
    print(f"\n🌐 Testing Gaia connection:")
    try:
        from astroquery.gaia import Gaia
        print("✅ Astroquery Gaia module imported successfully")
        
        # Test a simple query
        test_query = """
        SELECT TOP 1 source_id, ra, dec, parallax
        FROM gaiadr3.gaia_source
        WHERE parallax > 10
        """
        print("🔍 Testing Gaia query...")
        job = Gaia.launch_job(test_query)
        results = job.get_results()
        print(f"✅ Gaia connection successful, test query returned {len(results)} results")
        
    except Exception as e:
        print(f"❌ Gaia connection failed: {e}")
    
    print(f"\n=== Debug Complete ===")

if __name__ == "__main__":
    debug_gaia_issues() 