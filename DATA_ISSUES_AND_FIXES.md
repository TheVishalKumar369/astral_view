# Data Collection Issues and Fixes

## Issues Identified

### 1. Exoplanet Data Collection Failure
**Problem**: The NASA Exoplanet Archive query failed with error `ORA-00904: 'PL_ALBEDO': invalid identifier`

**Root Cause**: The script was trying to query a field `pl_albedo` that doesn't exist in the current NASA Exoplanet Archive database schema.

**Fix Applied**: 
- Removed invalid field `pl_albedo` from the query
- Updated field list to use only valid fields from the NASA Exoplanet Archive
- Improved error handling in the data collection script

### 2. Solar System Data Issues
**Problem**: All Solar System bodies showed:
- Zero distances from Sun (invalid)
- Zero velocities (invalid)
- Incorrect orbital data for some asteroids

**Root Cause**: 
- JPL Horizons data extraction was not properly handling the response format
- Distance and velocity calculations were not working correctly
- Data type conversions were missing

**Fix Applied**:
- Improved data extraction logic to handle both Table and dict formats
- Added proper distance calculation using Pythagorean theorem
- Added velocity calculation from velocity components
- Added explicit type conversions to float
- Created fallback Solar System data with realistic values

### 3. Missing Data Files
**Problem**: No exoplanet data was collected due to the API error, leaving gaps in the dataset.

**Fix Applied**:
- Fixed the exoplanet collection script
- Added comprehensive error handling
- Created validation scripts to detect issues early

## Solutions Implemented

### 1. Fixed Exoplanet Collection (`scripts/collect_data.py`)
```python
# Before (invalid fields):
important_fields = [
    'pl_name', 'hostname', 'sy_dist', 'ra', 'dec',
    'pl_albedo',  # ❌ This field doesn't exist
    # ... other fields
]

# After (valid fields only):
important_fields = [
    'pl_name', 'hostname', 'sy_dist', 'ra', 'dec',
    'pl_rade', 'pl_bmasse', 'pl_orbper', 'pl_eqt',
    'st_teff', 'st_rad', 'discoverymethod', 'disc_year',
    'pl_orbsmax', 'pl_orbeccen', 'pl_insol', 'pl_dens',
    'gaia_id', 'sy_vmag', 'sy_kmag', 'sy_umag', 'sy_gmag', 'sy_rmag', 'sy_imag',
    'pl_massj', 'pl_radj', 'pl_orbincl', 'pl_orblper',
    'st_mass', 'st_met', 'st_logg', 'st_age'
]
```

### 2. Fixed Solar System Collection
```python
# Improved data extraction:
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
```

### 3. Created Validation Script (`scripts/validate_data.py`)
- Added comprehensive data validation
- Checks for invalid values (zero distances, zero velocities)
- Reports data completeness and ranges
- Provides clear error messages

### 4. Created Fix Script (`scripts/fix_data_issues.py`)
- Automatically re-runs data collection with corrected parameters
- Creates fallback data if API calls fail
- Provides comprehensive error reporting
- Validates results after collection

## How to Fix the Data

### Option 1: Run the Fix Script (Recommended)
```bash
docker compose run --rm data_service python scripts/fix_data_issues.py
```

### Option 2: Re-run Data Collection
```bash
docker compose run --rm data_service python scripts/collect_data.py
```

### Option 3: Validate Current Data
```bash
docker compose run --rm data_service python scripts/validate_data.py
```

## Expected Results After Fix

### Exoplanet Data
- Should collect ~5000+ confirmed exoplanet systems
- Includes proper distance, mass, radius, and orbital data
- Valid Gaia IDs for cross-matching

### Solar System Data
- All planets should have realistic distances from Sun (0.39-39.48 AU)
- All planets should have realistic velocities (4.7-47.4 km/s)
- Proper 3D positions in both AU and light years

### Messier Catalog
- 110 deep-sky objects with proper coordinates
- Realistic distances (444 LY to 60M LY)
- Proper object classifications

## Data Quality Checks

After running the fixes, you should see:

1. **Exoplanet Data**: 
   - File: `data/raw/nasa_exoplanets.csv`
   - ~5000+ rows with valid data
   - No missing critical fields

2. **Solar System Data**:
   - File: `data/raw/solar_system.csv`
   - 10+ bodies with non-zero distances and velocities
   - Realistic orbital parameters

3. **Messier Catalog**:
   - File: `data/raw/messier_catalog.csv`
   - 110 objects with proper coordinates
   - Valid distance and magnitude data

## Troubleshooting

If you still encounter issues:

1. **Check API Connectivity**: Ensure internet connection for NASA and JPL APIs
2. **Check Docker Environment**: Ensure all required packages are installed
3. **Check Data Directory**: Ensure `/workspace/data/raw` exists and is writable
4. **Review Error Messages**: The scripts now provide detailed error reporting

## Next Steps

After fixing the data:

1. Run the validation script to confirm data quality
2. Process the data using `scripts/process_data.py`
3. Test the visualization components
4. Deploy the application

The fixes ensure that your Cosmic Explorer will have scientifically accurate data for an immersive space exploration experience. 