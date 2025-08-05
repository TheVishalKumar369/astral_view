"""
process_data.py
Processes raw data from data/raw/ and outputs cleaned/merged data to data/processed/ in efficient formats.
Also extracts explorable exoplanets with rich surface/atmosphere data for in-depth gameplay features.
"""
import pandas as pd
from pathlib import Path
import numpy as np
import pyarrow.parquet as pq
import h5py

RAW_DATA_DIR = Path("data/raw")
PROCESSED_DATA_DIR = Path("data/processed")
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- Existing functions for loading and cleaning ---
def load_nasa_exoplanets():
    path = RAW_DATA_DIR / "nasa_exoplanets.csv"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found. Run collect_data.py first.")
    df = pd.read_csv(path)
    return df

def clean_exoplanet_data(df):
    before = len(df)
    critical_fields = ["ra", "dec", "pl_orbper", "pl_rade", "pl_bmasse"]
    df_clean = df.dropna(subset=critical_fields).copy()
    dropped = before - len(df_clean)
    print(f"Dropped {dropped} rows due to missing critical fields.")

    # Ensure all IDs are strings and log any conversion issues
    for col in ['pl_name', 'hostname']:
        try:
            df_clean.loc[:, col] = df_clean[col].astype(str)
        except Exception as e:
            print(f"[SKIP] Could not convert column {col} to string: {e}")

    # No type conversion for Gaia IDs or catalog names
    # All further processing should treat IDs as strings

    parallax_present = 'sy_plx' in df_clean.columns and df_clean['sy_plx'].notna().any()
    dist_present = 'sy_dist' in df_clean.columns and df_clean['sy_dist'].notna().any()

    if parallax_present:
        valid_parallax_mask = df_clean['sy_plx'] > 0
        dist_pc = 1000 / df_clean.loc[valid_parallax_mask, 'sy_plx']
        df_clean.loc[valid_parallax_mask, 'dist_ly'] = dist_pc * 3.26156
    if dist_present:
        df_clean['dist_ly'] = df_clean['dist_ly'].fillna(df_clean['sy_dist'] * 3.26156)

    # Calculate coordinates if we have distance data
    if 'dist_ly' in df_clean.columns:
        try:
            ra_rad = np.radians(df_clean['ra'])
            dec_rad = np.radians(df_clean['dec'])
            dist_ly = df_clean['dist_ly']
            df_clean.loc[:, 'x'] = dist_ly * np.cos(dec_rad) * np.cos(ra_rad)
            df_clean.loc[:, 'y'] = dist_ly * np.cos(dec_rad) * np.sin(ra_rad)
            df_clean.loc[:, 'z'] = dist_ly * np.sin(dec_rad)
        except Exception as e:
            print(f"[SKIP] Could not calculate coordinates for some rows: {e}")
    else:
        print("Warning: No distance data ('sy_plx' or 'sy_dist') found to calculate x,y,z coordinates.")
    return df_clean

def save_parquet(df, name):
    out_path = PROCESSED_DATA_DIR / f"{name}.parquet"
    df.to_parquet(out_path, index=False)
    print(f"Saved: {out_path}")

def save_hdf5(df, name):
    out_path = PROCESSED_DATA_DIR / f"{name}.h5"
    with h5py.File(out_path, "w") as f:
        # Ensure we only try to save if x, y, z are present
        if all(col in df.columns for col in ["x", "y", "z"]):
            f.create_dataset("positions", data=df[["x", "y", "z"]].values)
            print(f"Saved HDF5 positions: {out_path}")
        else:
            print(f"Skipped HDF5 save for '{name}': missing x,y,z columns.")

# --- New: Extract explorable exoplanets for immersive gameplay ---
def extract_explorable_planets(df, min_fields=5, max_planets=200):
    
    # Define all desirable fields for a rich experience
    potential_fields = [
        'pl_name', 'pl_eqt', 'pl_rade', 'pl_bmasse', 'pl_dens', 'pl_orbper',
        'pl_orbsmax', 'pl_orbeccen', 'pl_insol', 'pl_albedo', 'pl_atmflag',
        'pl_surf_flag', 'pl_surf_temp', 'pl_surf_grav', 'pl_surf_pres'
    ]
    
    # Filter down to fields that actually exist in the DataFrame
    existing_fields = [field for field in potential_fields if field in df.columns]
    
    if len(existing_fields) < min_fields:
        print("Not enough data fields available to extract explorable planets. Skipping.")
        return None

    # Only keep planets with at least min_fields non-null among the available required_fields
    df_copy = df.copy()
    df_copy['non_null_fields'] = df_copy[existing_fields].notnull().sum(axis=1)
    explorable = df_copy[df_copy['non_null_fields'] >= min_fields].copy()

    # Safely calculate gravity and escape velocity
    def safe_calc(value, earth_equivalent):
        try:
            return float(value) * earth_equivalent
        except (ValueError, TypeError):
            return np.nan

    if 'pl_bmasse' in explorable.columns and 'pl_rade' in explorable.columns:
        G = 6.67430e-11
        M_earth = 5.972e24
        R_earth = 6.371e6

        mass_kg = explorable['pl_bmasse'].apply(safe_calc, earth_equivalent=M_earth)
        radius_m = explorable['pl_rade'].apply(safe_calc, earth_equivalent=R_earth)

        # Avoid division by zero
        radius_m_safe = radius_m.replace(0, np.nan)
        
        explorable['surface_gravity'] = G * mass_kg / (radius_m_safe ** 2)
        explorable['escape_velocity'] = np.sqrt(2 * G * mass_kg / radius_m_safe) / 1000

    # Calculate playability score
    def playability(row):
        gravity_score = 0.5
        if 'surface_gravity' in row and pd.notna(row['surface_gravity']):
            gravity = row['surface_gravity']
            if 2 <= gravity <= 20: gravity_score = 1.0
            elif 0.5 <= gravity < 2 or 20 < gravity <= 50: gravity_score = 0.5
            else: gravity_score = 0.1

        escape_score = 0.5
        if 'escape_velocity' in row and pd.notna(row['escape_velocity']):
            escape_v = row['escape_velocity']
            if 5 <= escape_v <= 30: escape_score = 1.0
            elif 2 <= escape_v < 5 or 30 < escape_v <= 60: escape_score = 0.5
            else: escape_score = 0.1
            
        richness_score = row['non_null_fields'] / len(existing_fields)
        return gravity_score * escape_score * richness_score

    explorable['playability'] = explorable.apply(playability, axis=1)
    
    explorable.sort_values(
        by=['playability', 'non_null_fields', 'pl_eqt'],
        ascending=[False, False, True],
        inplace=True
    )
    
    explorable = explorable.head(max_planets)
    explorable.drop(columns=['non_null_fields'], inplace=True)
    
    out_path = PROCESSED_DATA_DIR / "explorable_exoplanets.parquet"
    explorable.to_parquet(out_path, index=False)
    print(f"Saved: {out_path}")
    return explorable

def load_gaia_host_stars():
    path = RAW_DATA_DIR / "gaia_host_stars_raw.csv"
    if not path.exists():
        print(f"{path} not found. Skipping Gaia host stars.")
        return None
    df = pd.read_csv(path)
    return df

def clean_gaia_data(df):
    before = len(df)
    df_clean = df.dropna(subset=["ra", "dec", "parallax"]).copy()
    dropped = before - len(df_clean)
    print(f"Gaia: Dropped {dropped} rows due to missing ra/dec/parallax")
    
    # Calculate 3D positions using .loc to avoid SettingWithCopyWarning
    dist_pc = 1.0 / df_clean["parallax"].replace(0, np.nan) * 1e3
    dist_ly = dist_pc * 3.26156
    ra_rad = np.radians(df_clean["ra"])
    dec_rad = np.radians(df_clean["dec"])
    
    df_clean.loc[:, "x"] = dist_ly * np.cos(dec_rad) * np.cos(ra_rad)
    df_clean.loc[:, "y"] = dist_ly * np.cos(dec_rad) * np.sin(ra_rad)
    df_clean.loc[:, "z"] = dist_ly * np.sin(dec_rad)
    
    # Ensure gaia_id is of a consistent type (integer)
    if 'gaia_id' in df_clean.columns:
        df_clean.loc[:, 'gaia_id'] = pd.to_numeric(df_clean['gaia_id'], errors='coerce').astype('Int64')

    return df_clean

def load_messier():
    path = RAW_DATA_DIR / "messier_catalog.csv"
    if not path.exists():
        print(f"{path} not found. Skipping Messier catalog.")
        return None
    df = pd.read_csv(path)
    return df

def clean_messier_data(df):
    before = len(df)
    df_clean = df.dropna(subset=["ra", "dec", "distance_ly"]).copy()
    dropped = before - len(df_clean)
    print(f"Messier: Dropped {dropped} rows due to missing ra/dec/distance_ly")
    
    # Calculate coordinates
    ra_rad = np.radians(df_clean["ra"])
    dec_rad = np.radians(df_clean["dec"])
    dist_ly = df_clean["distance_ly"]
    
    df_clean.loc[:, 'x'] = dist_ly * np.cos(dec_rad) * np.cos(ra_rad)
    df_clean.loc[:, 'y'] = dist_ly * np.cos(dec_rad) * np.sin(ra_rad)
    df_clean.loc[:, 'z'] = dist_ly * np.sin(dec_rad)
        
    return df_clean

def load_solar_system():
    path = RAW_DATA_DIR / "solar_system.csv"
    if not path.exists():
        print(f"{path} not found. Skipping Solar System.")
        return None
    df = pd.read_csv(path)
    return df

def clean_solar_system_data(df):
    before = len(df)
    df_clean = df.dropna(subset=["x_ly", "y_ly", "z_ly"]).copy()
    dropped = before - len(df_clean)
    print(f"Solar System: Dropped {dropped} rows due to missing x_ly/y_ly/z_ly")
    # Rename for consistency
    if all(c in df_clean.columns for c in ['x_ly', 'y_ly', 'z_ly']):
        df_clean.rename(columns={'x_ly': 'x', 'y_ly': 'y', 'z_ly': 'z'}, inplace=True)
    # Ensure x, y, z are present and numeric
    for col in ['x', 'y', 'z']:
        if col not in df_clean.columns:
            print(f"[WARN] Missing column '{col}' in Solar System data after renaming.")
            df_clean[col] = np.nan
        else:
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
    return df_clean

# --- Main ---
def main():
    results = {}
    
    # Helper function for final validation
    def validate_dataframe(df, name, required_cols):
        """Checks that all required columns exist and have no null values."""
        for col in required_cols:
            if col not in df.columns:
                print(f"Available columns in {name}: {list(df.columns)}")
                print(f"Sample data from {name} (first 5 rows):\n{df.head()}\n")
                raise ValueError(f"Missing required column '{col}' in {name} DataFrame.")
            if df[col].isnull().any():
                print(f"Null values found in column '{col}' of {name}.")
                print(f"Available columns: {list(df.columns)}")
                print(f"Sample data (first 5 rows):\n{df.head()}\n")
                raise ValueError(f"Null values found in critical column '{col}' in {name} DataFrame.")
        if df.empty:
            print(f"ERROR: All rows dropped from {name} after cleaning. Columns present: {list(df.columns)}")
            raise ValueError(f"No valid {name} data after cleaning.")
        print(f"✓ Data integrity validated for {name}.")

    # 1. Load exoplanets
    try:
        df = load_nasa_exoplanets()
        results['Load Exoplanets'] = 'Success'
    except Exception as e:
        print(f"ERROR: Failed to load exoplanet data: {e}")
        df = None
        results['Load Exoplanets'] = f'Failed: {e}'
    # 2. Clean data
    try:
        if df is not None:
            df_clean = clean_exoplanet_data(df)
            results['Clean Data'] = 'Success'
        else:
            print("Skipping cleaning due to missing exoplanet data.")
            results['Clean Data'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Failed to clean exoplanet data: {e}")
        df_clean = None
        results['Clean Data'] = f'Failed: {e}'
    # 3. Save cleaned data
    try:
        if df_clean is not None:
            validate_dataframe(df_clean, "Exoplanets", 
                               required_cols=['pl_name', 'hostname', 'ra', 'dec', 'dist_ly', 'x', 'y', 'z'])
            save_parquet(df_clean, "exoplanets_cleaned")
            save_hdf5(df_clean, "exoplanets_positions")
            results['Save Cleaned Data'] = 'Success'
        else:
            print("Skipping save due to missing cleaned data.")
            results['Save Cleaned Data'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Failed to save cleaned data: {e}")
        results['Save Cleaned Data'] = f'Failed: {e}'
    # 4. Extract explorable planets
    try:
        if df_clean is not None:
            explorable_df = extract_explorable_planets(df_clean)
            if explorable_df is not None:
                validate_dataframe(explorable_df, "Explorable Exoplanets",
                                   required_cols=['pl_name', 'pl_eqt', 'pl_rade', 'pl_bmasse'])
            results['Extract Explorable Planets'] = 'Success'
        else:
            print("Skipping extraction due to missing cleaned data.")
            results['Extract Explorable Planets'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Failed to extract explorable planets: {e}")
        results['Extract Explorable Planets'] = f'Failed: {e}'

    # --- Gaia Host Stars ---
    try:
        gaia_df = load_gaia_host_stars()
        if gaia_df is not None:
            gaia_clean = clean_gaia_data(gaia_df)
            validate_dataframe(gaia_clean, "Gaia Host Stars",
                               required_cols=['source_id', 'ra', 'dec', 'parallax', 'x', 'y', 'z'])
            save_parquet(gaia_clean, "gaia_host_stars_cleaned")
            results['Gaia Host Stars'] = 'Success'
        else:
            results['Gaia Host Stars'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Gaia host stars: {e}")
        results['Gaia Host Stars'] = f'Failed: {e}'

    # --- Messier Catalog ---
    try:
        messier_df = load_messier()
        if messier_df is not None:
            messier_clean = clean_messier_data(messier_df)
            validate_dataframe(messier_clean, "Messier Catalog",
                               required_cols=['M_number', 'name', 'ra', 'dec', 'distance_ly', 'x', 'y', 'z'])
            save_parquet(messier_clean, "messier_catalog_cleaned")
            results['Messier Catalog'] = 'Success'
        else:
            results['Messier Catalog'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Messier catalog: {e}")
        results['Messier Catalog'] = f'Failed: {e}'

    # --- Solar System ---
    try:
        solar_df = load_solar_system()
        if solar_df is not None:
            solar_clean = clean_solar_system_data(solar_df)
            validate_dataframe(solar_clean, "Solar System",
                               required_cols=['name', 'id', 'x', 'y', 'z'])
            save_parquet(solar_clean, "solar_system_cleaned")
            results['Solar System'] = 'Success'
        else:
            results['Solar System'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Solar System: {e}")
        results['Solar System'] = f'Failed: {e}'

    print("\n--- Data Processing Summary ---")
    for k, v in results.items():
        print(f"{k}: {v}")
    print("All data processing steps attempted.")

if __name__ == "__main__":
    main() 