#!/usr/bin/env python3
"""
Test SIMBAD Query for Known Star (Sirius)
This script tests the SIMBAD query and name extraction logic for a well-known star using its Gaia DR3 ID and coordinates.
"""
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

# Reset and add votable fields
Simbad.reset_votable_fields()
Simbad.add_votable_fields('ids', 'main_id', 'otype')

# Gaia DR3 ID and coordinates for Sirius
GAIA_ID_SIRIUS = '2943418782382636032'
RA_SIRIUS = 101.28715533  # degrees
DEC_SIRIUS = -16.71611586  # degrees

print(f"Querying SIMBAD for Gaia DR3 {GAIA_ID_SIRIUS} (Sirius) by Gaia ID...")
result = Simbad.query_object(f'id(Gaia DR3 {GAIA_ID_SIRIUS})')

if result is not None and len(result) > 0:
    print("Result found by Gaia DR3 ID!")
    main_id = result['main_id'][0] if 'main_id' in result.colnames else GAIA_ID_SIRIUS
    all_names = result['ids'][0] if 'ids' in result.colnames else ''
    object_type = result['otype'][0] if 'otype' in result.colnames else ''
    print('main_id:', main_id)
    print('ids:', all_names)
    print('otype:', object_type)
    # Extraction logic
    common_name = ''
    if isinstance(all_names, str):
        for part in all_names.split('|'):
            part = part.strip()
            if part and not part.lower().startswith('gaia') and not part.isdigit():
                common_name = part
                break
    print('Extracted common name:', common_name)
else:
    print('No result found for Gaia DR3 ID. Trying cone search by coordinates...')
    coord = SkyCoord(ra=RA_SIRIUS * u.deg, dec=DEC_SIRIUS * u.deg, frame='icrs')
    result = Simbad.query_region(coord, radius=5 * u.arcsec)
    if result is not None and len(result) > 0:
        print("Result found by cone search!")
        print("Result table:")
        print(result)
        print("Column names:", result.colnames)
        main_id = result['main_id'][0] if 'main_id' in result.colnames else ''
        all_names = result['ids'][0] if 'ids' in result.colnames else ''
        object_type = result['otype'][0] if 'otype' in result.colnames else ''
        print('main_id:', main_id)
        print('ids:', all_names)
        print('otype:', object_type)
        # Extraction logic
        common_name = ''
        if isinstance(all_names, str):
            for part in all_names.split('|'):
                part = part.strip()
                if part and not part.lower().startswith('gaia') and not part.isdigit():
                    common_name = part
                    break
        print('Extracted common name:', common_name)
    else:
        print('No result found for Sirius by Gaia ID or coordinates.') 