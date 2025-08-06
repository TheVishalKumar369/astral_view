"""
collect_data.py
Master data collection script for Cosmic Explorer.
Fetches and saves exoplanet, Gaia, SIMBAD, JPL Horizons, and Messier data with all necessary fields for a realistic, explorable 3D world. Optimized for laptop hardware.
"""
import pandas as pd
from pathlib import Path
import re

# Configure matplotlib for headless operation
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.ioff()

RAW_DATA_DIR = Path("/tmp/data/raw")
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

# --- 1. NASA Exoplanet Archive ---
def fetch_nasa_exoplanets():
    from astroquery.ipac.nexsci.nasa_exoplanet_archive import NasaExoplanetArchive
    from datetime import datetime
    print("Using NASA Exoplanet Archive 'pscomppars' (composite parameters) table for exoplanet data.")
    print(f"Data fetched on: {datetime.utcnow().isoformat()} UTC")
    print("Fetching NASA Exoplanet Archive confirmed planets table...")
    
    # Define all important parameters for realistic gameplay
    # Updated to use only valid fields from the NASA Exoplanet Archive
    important_fields = [
        'pl_name', 'hostname', 'sy_dist', 'ra', 'dec',  # Identification and positioning
        'pl_rade', 'pl_bmasse', 'pl_orbper', 'pl_eqt',  # Planet properties
        'st_teff', 'st_rad', 'discoverymethod', 'disc_year',  # Star and discovery info
        'pl_orbsmax', 'pl_orbeccen', 'pl_insol', 'pl_dens',  # Orbital and physical properties
        'gaia_id', 'sy_vmag', 'sy_kmag', 'sy_umag', 'sy_gmag', 'sy_rmag', 'sy_imag',  # Additional star data
        'pl_massj', 'pl_radj', 'pl_orbincl', 'pl_orblper',  # Additional planet data
        'st_mass', 'st_met', 'st_logg', 'st_age', 'sy_dist', 'sy_plx'  # Use sy_dist and sy_plx for system distance/parallax
    ]
    
    # Query with specific fields to ensure we get all important data
    field_list = ','.join(important_fields)
    exo_table = NasaExoplanetArchive.query_criteria(
        table="pscomppars",  # Use the composite table for the "best" data per planet
        select=field_list,  # specific important columns
        format="csv"
    )
    exo_df = exo_table.to_pandas()
    # Add provenance metadata as a comment row (if writing CSV)
    out_path = RAW_DATA_DIR / "nasa_exoplanets.csv"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# Source: NASA Exoplanet Archive, Table: pscomppars, Downloaded: {datetime.utcnow().isoformat()} UTC\n")
        exo_df.to_csv(f, index=False)
    print(f"Saved: {out_path}")
    print(f"Retrieved {len(exo_df)} exoplanet systems with {len(exo_df.columns)} parameters")
    
    # Check which important fields we successfully retrieved
    retrieved_fields = [f for f in important_fields if f in exo_df.columns]
    missing_fields = [f for f in important_fields if f not in exo_df.columns]
    
    print(f"Successfully retrieved {len(retrieved_fields)} important fields:")
    for field in retrieved_fields:
        non_null_count = exo_df[field].notna().sum()
        print(f"  - {field}: {non_null_count}/{len(exo_df)} values")
    
    if missing_fields:
        print(f"ERROR: The following important fields are missing: {missing_fields}")
        print(f"Available columns: {list(exo_df.columns)}")
        raise ValueError(f"Missing critical fields: {missing_fields}")
    else:
        print("All important fields for gameplay are present in exoplanet data.")
    
    return exo_df

# --- 2. Gaia DR3 (Host stars + background) ---
def fetch_gaia_data(exo_df, max_background=10000):
    from astroquery.gaia import Gaia
    from datetime import datetime
    print("Using Gaia Data Release 3 (DR3) for all star queries.")
    print(f"Data fetched on: {datetime.utcnow().isoformat()} UTC")
    
    # Extract Gaia IDs more robustly
    gaia_ids = []
    if 'gaia_id' in exo_df.columns:
        print(f"Found 'gaia_id' column with {exo_df['gaia_id'].notna().sum()} non-null values")
        # Show some sample values to understand the format
        sample_values = exo_df['gaia_id'].dropna().head(5)
        print("Sample Gaia ID values:")
        for i, val in enumerate(sample_values):
            print(f"  {i}: '{val}' (type: {type(val)})")

        # More robust Gaia ID parsing to handle various formats and bad data
        for idx, gaia_id_val in enumerate(exo_df['gaia_id'].dropna()):
            try:
                s_id = str(gaia_id_val).strip()
                # Only accept a string of 10 or more digits (no negatives, no 'Gaia-2', etc.)
                match = re.fullmatch(r'\d{10,}', s_id)
                if match:
                    numeric_id = int(match.group(0))
                    gaia_ids.append(numeric_id)
                else:
                    # Try to extract a valid numeric ID from within a string (e.g., 'Gaia DR2 1234567890123')
                    match2 = re.search(r'\d{10,}', s_id)
                    if match2:
                        numeric_id = int(match2.group(0))
                        gaia_ids.append(numeric_id)
                    else:
                        print(f"[SKIP] Not a valid Gaia ID: '{s_id}' at row {idx}")
            except Exception as e:
                print(f"[ERROR] Gaia ID parsing failed for '{gaia_id_val}' at row {idx}: {e}")
    else:
        print("No 'gaia_id' column found in exoplanet data")
        # Try alternative column names
        for col in ['gaia_source_id', 'source_id', 'gaia_dr2_id', 'gaia_dr3_id']:
            if col in exo_df.columns:
                print(f"Found alternative column '{col}' with {exo_df[col].notna().sum()} values")
                valid_ids = []
                for idx, gaia_id in enumerate(exo_df[col].dropna()):
                    try:
                        numeric_id = int(gaia_id)
                        # Gaia IDs are typically 12+ digits, so require at least 10 digits
                        if numeric_id > 1000000000:  # At least 10 digits
                            valid_ids.append(numeric_id)
                        else:
                            print(f"Warning: Invalid Gaia ID '{gaia_id}' (too small: {numeric_id}) at row {idx}")
                    except (ValueError, TypeError) as e:
                        print(f"Error processing Gaia ID '{gaia_id}' at row {idx}: {e}")
                        continue
                gaia_ids = valid_ids
                break
    
    # Remove duplicates and ensure we have valid IDs
    gaia_ids = list(set(gaia_ids))  # Remove duplicates
    gaia_ids = [id for id in gaia_ids if id > 1000000000]  # Ensure all IDs are valid Gaia IDs (10+ digits)
    
    if not gaia_ids:
        print("No valid numeric Gaia IDs found. Skipping Gaia host star fetch.")
        print("Available columns in exoplanet data:", list(exo_df.columns))
        
        # Show some sample data to help debug
        if 'gaia_id' in exo_df.columns:
            print("\nSample Gaia ID values:")
            sample_gaia = exo_df['gaia_id'].dropna().head(10)
            for i, val in enumerate(sample_gaia):
                print(f"  {i}: {val} (type: {type(val)})")
        
        return None, None
    
    print(f"Found {len(gaia_ids)} unique valid Gaia IDs for querying")
    print(f"Sample Gaia IDs: {gaia_ids[:5]}")
    
    host_stars = []
    chunk_size = 1000
    for i in range(0, len(gaia_ids), chunk_size):
        chunk_ids = gaia_ids[i:i+chunk_size]
        id_list = ','.join(map(str, chunk_ids))
        query = f"""
        SELECT source_id, ra, dec, parallax, pmra, pmdec, radial_velocity,
               phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
               ruwe, teff_gspphot, logg_gspphot, mh_gspphot
        FROM gaiadr3.gaia_source
        WHERE source_id IN ({id_list})
        """
        try:
            print(f"Executing Gaia query for chunk {i//chunk_size + 1}/{(len(gaia_ids)//chunk_size)+1}")
            job = Gaia.launch_job(query)
            results = job.get_results()
            if results and len(results) > 0:
                host_stars.append(results.to_pandas())
                print(f"Downloaded chunk {i//chunk_size + 1}: {len(results)} stars")
            else:
                print(f"Warning: No results for chunk {i//chunk_size + 1}")
        except Exception as e:
            print(f"Error downloading chunk {i//chunk_size + 1}: {e}")
            print(f"Query was: {query[:100]}...")
            continue
    
    if not host_stars:
        print("No host star data retrieved from Gaia")
        print("Attempting to fetch some nearby bright stars as fallback...")
        
        # Fallback: Get some nearby bright stars
        try:
            fallback_query = """
            SELECT TOP 1000
              source_id, ra, dec, parallax, pmra, pmdec, radial_velocity,
              phot_g_mean_mag, phot_bp_mean_mag, phot_rp_mean_mag,
              ruwe, teff_gspphot, logg_gspphot, mh_gspphot
            FROM gaiadr3.gaia_source
            WHERE parallax > 5 AND phot_g_mean_mag < 8 AND ruwe < 1.4
            ORDER BY phot_g_mean_mag
            """
            print("Executing fallback Gaia query for nearby bright stars...")
            job = Gaia.launch_job(fallback_query)
            fallback_results = job.get_results()
            if fallback_results and len(fallback_results) > 0:
                host_stars_df = fallback_results.to_pandas()
                out_path = RAW_DATA_DIR / "gaia_host_stars_raw.csv"
                with open(out_path, 'w', encoding='utf-8') as f:
                    f.write(f"# Source: Gaia DR3, Downloaded: {datetime.utcnow().isoformat()} UTC\n")
                    host_stars_df.to_csv(f, index=False)
                print(f"Saved fallback data: {out_path}")
                print(f"Fallback stars retrieved: {len(host_stars_df)}")
                return host_stars_df, None
            else:
                print("No fallback stars retrieved either")
                return None, None
        except Exception as e:
            print(f"Error in fallback Gaia query: {e}")
            return None, None
    
    if host_stars:
        host_stars_df = pd.concat(host_stars, ignore_index=True)
        out_path = RAW_DATA_DIR / "gaia_host_stars_raw.csv"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# Source: Gaia DR3, Downloaded: {datetime.utcnow().isoformat()} UTC\n")
            host_stars_df.to_csv(f, index=False)
        print(f"Saved: {out_path}")
        print(f"Total host stars retrieved: {len(host_stars_df)}")
    
    # Background stars (get a random sample from a larger volume for a more realistic background)
    print("Querying Gaia for a random sample of background stars...")
    try:
        # Use random_index for efficient random sampling from a larger volume
        query = f"""
        SELECT TOP {max_background}
          source_id, ra, dec, parallax, phot_g_mean_mag, ruwe, teff_gspphot
        FROM gaiadr3.gaia_source
        WHERE parallax > 1  -- Select stars up to 1000 pc (3260 ly) away
          AND ruwe < 1.4      -- Ensure high-quality astrometric data
        ORDER BY random_index
        """
        job = Gaia.launch_job(query)
        background_stars_df = job.get_results().to_pandas()
        background_stars_df.to_csv(RAW_DATA_DIR / "gaia_background_stars_raw.csv", index=False)
        print(f"Saved: {RAW_DATA_DIR / 'gaia_background_stars_raw.csv'}")
        print(f"Background stars retrieved: {len(background_stars_df)}")
    except Exception as e:
        print(f"Error fetching background stars: {e}")
        background_stars_df = None
    
    return host_stars_df, background_stars_df

# --- 3. SIMBAD Cross-matching ---
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u
import pandas as pd
import time
from pathlib import Path

def fetch_simbad_names(gaia_ids, ras, decs, max_ids=1000):
    from astroquery.simbad import Simbad
    from astropy.coordinates import SkyCoord
    import astropy.units as u
    import pandas as pd
    import time
    from pathlib import Path

    Simbad.reset_votable_fields()
    Simbad.add_votable_fields('ids', 'main_id', 'otype')
    print("Fetching SIMBAD names for host stars (2025 best practice, using full Gaia ID string, no type conversion)...")
    names = []
    successful_queries = 0
    failed_queries = 0

    for i, (gaia_id, ra, dec) in enumerate(zip(gaia_ids[:max_ids], ras[:max_ids], decs[:max_ids])):
        found = False
        main_id, all_names, object_type, star_names, common_name = '', '', '', '', ''
        gaia_id_str = str(gaia_id).strip()
        if not gaia_id_str:
            print(f"[SKIP] Empty Gaia ID at row {i}")
            continue
        print(f"Querying SIMBAD for Gaia DR3 {gaia_id_str} (row {i})")
        try:
            result = Simbad.query_object(f"id(Gaia DR3 {gaia_id_str})")
            if result is not None and len(result) > 0:
                found = True
                main_id = result['main_id'][0] if 'main_id' in result.colnames else gaia_id_str
                all_names = result['ids'][0] if 'ids' in result.colnames else ''
                object_type = result['otype'][0] if 'otype' in result.colnames else ''
        except Exception as e:
            print(f"SIMBAD query failed for Gaia DR3 {gaia_id_str}: {e}")
        if not found:
            try:
                coord = SkyCoord(ra=float(ra)*u.deg, dec=float(dec)*u.deg, frame='icrs')
                result = Simbad.query_region(coord, radius=5*u.arcsec)
                if result is not None and len(result) > 0:
                    found = True
                    main_id = result['main_id'][0] if 'main_id' in result.colnames else gaia_id_str
                    all_names = result['ids'][0] if 'ids' in result.colnames else ''
                    object_type = result['otype'][0] if 'otype' in result.colnames else ''
            except Exception as e:
                print(f"SIMBAD cone search failed for Gaia DR3 {gaia_id_str}: {e}")
        # Improved name extraction logic
        if isinstance(all_names, str):
            # Prefer 'NAME ' entries
            for part in all_names.split('|'):
                part = part.strip()
                if part.startswith('NAME '):
                    star_names = part.replace('NAME ', '').strip()
                    break
            # Fallback: first non-Gaia, non-numeric name
            if not star_names:
                for part in all_names.split('|'):
                    part = part.strip()
                    if part and not part.lower().startswith('gaia') and not part.isdigit():
                        star_names = part
                        break
            # For compatibility, also set 'common_name' to the same value
            common_name = star_names
        has_common_name = bool(star_names)
        names.append({
            'gaia_id': gaia_id_str,
            'ra': ra,
            'dec': dec,
            'main_id': main_id,
            'simbad_names': all_names,
            'star_names': star_names,
            'common_name': common_name,
            'has_common_name': has_common_name,
            'object_type': object_type
        })
        if found:
            successful_queries += 1
        else:
            failed_queries += 1
        if (i+1) % 100 == 0:
            print(f"Processed {i+1} stars: {successful_queries} successful, {failed_queries} failed")
    print(f"SIMBAD query results: {successful_queries} successful, {failed_queries} failed")
    df = pd.DataFrame(names)
    out_path = Path('/tmp/data/raw/simbad_names.csv')
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df

# --- 4. JPL Horizons (Solar System) ---
def fetch_jpl_solar_system():
    """Fetch real Solar System data using JPL Horizons"""
    from astroquery.jplhorizons import Horizons
    from datetime import datetime
    from astropy.time import Time
    import numpy as np
    
    print("Fetching Solar System data from JPL Horizons (live ephemeris, always up-to-date).")
    print(f"Data fetched on: {datetime.utcnow().isoformat()} UTC")
    
    # Current date for ephemeris - convert to Julian Day properly
    current_date = datetime.now()
    jd = Time(current_date).jd  # Convert to Julian Day using astropy
    
    # Define all bodies we want to track
    # Updated to use modern, unambiguous IDs. Asteroids must have a semicolon.
    solar_system_bodies = {
        'Sun': '10',
        'Mercury': '199',  # Barycenter is fine
        'Venus': '299',   # Barycenter is fine
        'Earth': '399',
        'Moon': '301',
        'Mars': '499',    # Barycenter is fine
        'Jupiter': '599', # Barycenter
        'Saturn': '699',  # Barycenter
        'Uranus': '799',  # Barycenter
        'Neptune': '899', # Barycenter
        'Pluto': '999',   # Barycenter
        'Ceres': '1;',    # Asteroid (small body)
        'Vesta': '4;',    # Asteroid (small body)
        'Pallas': '2;',   # Asteroid (small body)
        'Eros': '433;',   # Asteroid (small body)
        'Voyager1': '-31',
        'Voyager2': '-32'
    }
    
    solar_system_data = []
    
    for body_name, body_id in solar_system_bodies.items():
        try:
            print(f"Fetching {body_name} (ID: {body_id})...")
            
            # Query JPL Horizons for current position using proper Julian Day
            obj = Horizons(id=body_id, location='500@0', epochs=jd)
            vectors = obj.vectors()
            
            # Extract position data (in AU) - improved data extraction
            if hasattr(vectors, 'columns'):
                # Table format - get the first row
                x_au = float(vectors['x'][0]) if 'x' in vectors.columns else 0
                y_au = float(vectors['y'][0]) if 'y' in vectors.columns else 0
                z_au = float(vectors['z'][0]) if 'z' in vectors.columns else 0
                # Calculate distance from Sun using Pythagorean theorem
                distance_from_sun_au = np.sqrt(x_au**2 + y_au**2 + z_au**2)
                # Get velocity magnitude
                if 'v' in vectors.columns:
                    velocity_km_s = float(vectors['v'][0])
                else:
                    # Calculate velocity from velocity components if available
                    vx = float(vectors['vx'][0]) if 'vx' in vectors.columns else 0
                    vy = float(vectors['vy'][0]) if 'vy' in vectors.columns else 0
                    vz = float(vectors['vz'][0]) if 'vz' in vectors.columns else 0
                    velocity_km_s = np.sqrt(vx**2 + vy**2 + vz**2)
            else:
                # Handle other formats
                x_au = float(vectors.get('x', [0])[0]) if isinstance(vectors.get('x'), (list, np.ndarray)) else 0
                y_au = float(vectors.get('y', [0])[0]) if isinstance(vectors.get('y'), (list, np.ndarray)) else 0
                z_au = float(vectors.get('z', [0])[0]) if isinstance(vectors.get('z'), (list, np.ndarray)) else 0
                distance_from_sun_au = np.sqrt(x_au**2 + y_au**2 + z_au**2)
                velocity_km_s = float(vectors.get('v', [0])[0]) if isinstance(vectors.get('v'), (list, np.ndarray)) else 0
            
            # Convert AU to light years (1 AU = 1/63241 LY)
            x_ly = x_au / 63241
            y_ly = y_au / 63241
            z_ly = z_au / 63241
            
            # Get object properties if available
            try:
                elements = obj.elements()
                if hasattr(elements, 'columns') and 'a' in elements.columns:
                    # Table format
                    semi_major_axis = float(elements['a'][0]) if 'a' in elements.columns else 0
                    eccentricity = float(elements['e'][0]) if 'e' in elements.columns else 0
                    inclination = float(elements['i'][0]) if 'i' in elements.columns else 0
                else:
                    # Dict format
                    semi_major_axis = float(elements.get('a', [0])[0]) if isinstance(elements.get('a'), (list, np.ndarray)) else 0
                    eccentricity = float(elements.get('e', [0])[0]) if isinstance(elements.get('e'), (list, np.ndarray)) else 0
                    inclination = float(elements.get('i', [0])[0]) if isinstance(elements.get('i'), (list, np.ndarray)) else 0
            except Exception as e:
                print(f"    Warning: Could not get orbital elements for {body_name}: {e}")
                semi_major_axis = 0
                eccentricity = 0
                inclination = 0
            
            # Determine object type
            if body_name == 'Sun':
                obj_type = 'Star'
                mass_kg = 1.989e30  # Solar mass
                radius_km = 696340
            elif body_name == 'Moon':
                obj_type = 'Satellite'
                mass_kg = 7.342e22
                radius_km = 1737.4
            elif body_name in ['Mercury', 'Venus', 'Earth', 'Mars', 'Jupiter', 'Saturn', 'Uranus', 'Neptune', 'Pluto']:
                obj_type = 'Planet'
                # Approximate masses in kg
                masses = {
                    'Mercury': 3.285e23, 'Venus': 4.867e24, 'Earth': 5.972e24,
                    'Mars': 6.39e23, 'Jupiter': 1.898e27, 'Saturn': 5.683e26,
                    'Uranus': 8.681e25, 'Neptune': 1.024e26, 'Pluto': 1.309e22
                }
                mass_kg = masses.get(body_name, 0)
                # Approximate radii in km
                radii = {
                    'Mercury': 2439.7, 'Venus': 6051.8, 'Earth': 6371,
                    'Mars': 3389.5, 'Jupiter': 69911, 'Saturn': 58232,
                    'Uranus': 25362, 'Neptune': 24622, 'Pluto': 1188.3
                }
                radius_km = radii.get(body_name, 0)
            else:
                obj_type = 'Asteroid'
                mass_kg = 0  # Unknown for most asteroids
                radius_km = 0  # Unknown for most asteroids
            
            solar_system_data.append({
                'name': body_name,
                'id': body_id,
                'type': obj_type,
                'x_au': x_au,
                'y_au': y_au, 
                'z_au': z_au,
                'x_ly': x_ly,
                'y_ly': y_ly,
                'z_ly': z_ly,
                'distance_from_sun_au': distance_from_sun_au,
                'velocity_km_s': velocity_km_s,
                'semi_major_axis_au': semi_major_axis,
                'eccentricity': eccentricity,
                'inclination_deg': inclination,
                'mass_kg': mass_kg,
                'radius_km': radius_km,
                'epoch_jd': jd
            })
            
            print(f"  ✓ {body_name}: ({x_ly:.6f}, {y_ly:.6f}, {z_ly:.6f}) LY")
            
        except Exception as e:
            print(f"  ✗ Error fetching {body_name}: {e}")
            continue
    
    # Create DataFrame and save
    if solar_system_data:
        df = pd.DataFrame(solar_system_data)
        out_path = RAW_DATA_DIR / "solar_system.csv"
        with open(out_path, 'w', encoding='utf-8') as f:
            f.write(f"# Source: JPL Horizons, Downloaded: {datetime.utcnow().isoformat()} UTC\n")
            df.to_csv(f, index=False)
        print(f"Saved: {out_path}")
        print(f"Retrieved {len(df)} Solar System bodies")
        
        # Print summary
        print("\nSolar System Summary:")
        for _, row in df.iterrows():
            print(f"  {row['name']} ({row['type']}): {row['distance_from_sun_au']:.3f} AU from Sun")
        
        return df
    else:
        print("No Solar System data retrieved")
        return None

# --- 5. Messier Catalog (Nebulae, clusters, etc.) ---
def fetch_messier_catalog():
    """Fetch comprehensive Messier Catalog data programmatically from SIMBAD."""
    from astroquery.simbad import Simbad
    from datetime import datetime
    import numpy as np

    print("Fetching Messier Catalog data from SIMBAD (always up-to-date).")
    print(f"Data fetched on: {datetime.utcnow().isoformat()} UTC")

    try:
        Simbad.add_votable_fields('mesdistance', 'V', 'dim')
        messier_table = Simbad.query_catalog('M')
        if messier_table is None or len(messier_table) == 0:
            print("Error: SIMBAD did not return any Messier objects.")
            return None
        df = messier_table.to_pandas()
        print(f"SIMBAD Messier columns: {list(df.columns)}")
        # Robust renaming: only rename columns that exist
        rename_map = {}
        if 'MAIN_ID' in df.columns: rename_map['MAIN_ID'] = 'name'
        if 'main_id' in df.columns: rename_map['main_id'] = 'name'
        if 'RA' in df.columns: rename_map['RA'] = 'ra'
        if 'ra' in df.columns: rename_map['ra'] = 'ra'
        if 'DEC' in df.columns: rename_map['DEC'] = 'dec'
        if 'dec' in df.columns: rename_map['dec'] = 'dec'
        if 'OTYPE' in df.columns: rename_map['OTYPE'] = 'type'
        if 'otype' in df.columns: rename_map['otype'] = 'type'
        if 'V' in df.columns: rename_map['V'] = 'apparent_magnitude'
        if 'DIM' in df.columns: rename_map['DIM'] = 'size_arcmin'
        if 'mesdistance.dist' in df.columns: rename_map['mesdistance.dist'] = 'distance_pc'
        if 'distance_ly' in df.columns: rename_map['distance_ly'] = 'distance_ly'
        df.rename(columns=rename_map, inplace=True)
        # Add the M_number from the original ID
        if 'name' in df.columns:
            df['M_number'] = df['name'].apply(lambda x: x.replace('M ', 'M'))
        else:
            print("Warning: 'name' column missing from Messier data. Columns are:", list(df.columns))
            df['M_number'] = ''
        # Distance: prefer distance_ly, else convert from distance_pc
        if 'distance_ly' not in df.columns and 'distance_pc' in df.columns:
            df['distance_ly'] = pd.to_numeric(df['distance_pc'], errors='coerce') * 3.26156
        elif 'distance_ly' in df.columns:
            df['distance_ly'] = pd.to_numeric(df['distance_ly'], errors='coerce')
        else:
            print("Warning: No distance column found in Messier data.")
            df['distance_ly'] = np.nan
        # Clean angular size: take the major axis if string, else keep as is
        if 'size_arcmin' in df.columns:
            df['size_arcmin'] = df['size_arcmin'].apply(
                lambda x: float(x.split('x')[0]) if isinstance(x, str) and 'x' in x else pd.to_numeric(x, errors='coerce')
            )
        # Select and reorder columns that exist
        final_cols = ['M_number', 'name', 'ra', 'dec', 'type', 'distance_ly', 'apparent_magnitude', 'size_arcmin']
        available_cols = [col for col in final_cols if col in df.columns]
        missing_cols = [col for col in final_cols if col not in df.columns]
        if missing_cols:
            print(f"[WARN] Messier catalog missing columns: {missing_cols}. Output will use available columns only.")
        df = df[available_cols]
        # Drop rows with missing critical values
        critical = [col for col in ['distance_ly', 'ra', 'dec'] if col in df.columns]
        df.dropna(subset=critical, inplace=True)
        # Strict check: if after dropping, DataFrame is empty, raise error
        if df.empty:
            print(f"ERROR: All rows dropped from Messier catalog due to missing critical values. Columns present: {list(df.columns)}")
            raise ValueError("No valid Messier catalog data after cleaning.")
    except Exception as e:
        print(f"Failed to fetch or process Messier data from SIMBAD: {e}")
        return None
    out_path = RAW_DATA_DIR / "messier_catalog.csv"
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(f"# Source: SIMBAD, Downloaded: {datetime.utcnow().isoformat()} UTC\n")
        df.to_csv(f, index=False)
    print(f"Saved: {out_path}")
    print(f"Retrieved and processed {len(df)} Messier objects from SIMBAD.")
    # Print summary by type
    if 'type' in df.columns:
        print("\nMessier Catalog Summary by Type:")
        type_counts = df['type'].value_counts()
        for obj_type, count in type_counts.items():
            print(f"  {obj_type}: {count} objects")
    return df


# --- 6. Main Pipeline ---
def main():
    results = {}
    host_stars_df = None  # Initialize variable at function scope
    
    # 1. Exoplanets
    try:
        exo_df = fetch_nasa_exoplanets()
        results['Exoplanets'] = 'Success'
    except Exception as e:
        print(f"ERROR: Failed to fetch exoplanet data: {e}")
        exo_df = None
        results['Exoplanets'] = f'Failed: {e}'
    
    # 2. Gaia
    try:
        if exo_df is not None:
            host_stars_df, background_stars_df = fetch_gaia_data(exo_df)
            if host_stars_df is not None:
                results['Gaia'] = 'Success'
            else:
                results['Gaia'] = 'No data retrieved'
        else:
            print("Skipping Gaia fetch due to missing exoplanet data.")
            results['Gaia'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Failed to fetch Gaia data: {e}")
        results['Gaia'] = f'Failed: {e}'
    
    # 3. SIMBAD
    try:
        if host_stars_df is not None and not host_stars_df.empty:
            simbad_df = fetch_simbad_names(host_stars_df['source_id'].tolist(), host_stars_df['ra'].tolist(), host_stars_df['dec'].tolist())
            results['SIMBAD'] = 'Success'
        else:
            print("Skipping SIMBAD fetch due to missing Gaia host star data.")
            results['SIMBAD'] = 'Skipped'
    except Exception as e:
        print(f"ERROR: Failed to fetch SIMBAD data: {e}")
        results['SIMBAD'] = f'Failed: {e}'
    
    # 4. JPL Horizons
    try:
        solar_system_df = fetch_jpl_solar_system()
        results['JPL Horizons'] = 'Success'
    except Exception as e:
        print(f"ERROR: Failed to fetch JPL Horizons data: {e}")
        results['JPL Horizons'] = f'Failed: {e}'
    
    # 5. Messier Catalog
    try:
        messier_df = fetch_messier_catalog()
        results['Messier'] = 'Success'
    except Exception as e:
        print(f"ERROR: Failed to fetch Messier catalog: {e}")
        results['Messier'] = f'Failed: {e}'
    
    print("\n--- Data Collection Summary ---")
    for k, v in results.items():
        print(f"{k}: {v}")
    print("All data collection steps attempted.")

if __name__ == "__main__":
    main() 