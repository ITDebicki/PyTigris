import requests
import os
import tempfile
from tqdm.auto import tqdm
import shutil
import functools
from pathlib import Path
import geopandas as gpd
import functools
import pandas as pd
import importlib
from typing import Optional

CACHE_PATH = Path('~/.pyTigris_cache/').expanduser()

def construct_url(year, query_type, cb, resolution, state = 'us'):
    query_type_abb = query_type[:2].lower()
    query_type = query_type.lower()
    # Query_type is one of: state, county, tract
    url = 'https://www2.census.gov/geo/tiger/'
    if cb:
        if year in {1990, 2000}:
            v = '99'
            if query_type == 'tract':
                v = state
            lastTwoDigits = str(year)[-2:]
            url += f'PREVGENZ/{query_type_abb}/{query_type_abb}{lastTwoDigits}shp/{query_type_abb}{v}_d{lastTwoDigits}_shp.zip'
        elif year == 2010:
            numberDict = {'state': '040', 'county': '050', 'tract': '140'}
            url += f'GENZ2010/gz_2010_{state}_{numberDict[query_type]}_00_{resolution}.zip'
        elif year == 2013:
            url += f'GENZ{year}/cb_{year}_{state}_{query_type}_{resolution}.zip'
        elif year == 2012:
            if query_type in {'cd', 'sldl', 'sldu', 'ua'}:
                url += f'GENZ{year}/shp/cb_rd13_{state}_{query_type}_{resolution}.zip'
            else:
                raise ValueError('Data for 2012 is only defined for queries: cd, sldl, sldu and ua')
        elif year > 2013:
            url += f'GENZ{year}/shp/cb_{year}_{state}_{query_type}_{resolution}.zip'
        else:
            raise ValueError(f'Data for `cb = True` is only available for the years: 1990, 2000, 2010, and 2012 onwards. Year specified: {year}')
    else:
        
        if year == 1990:
            raise ValueError('Please specify `cb = True` to get 1990 data.')
        
        if year in {2000, 2010}:
            lastTwoDigits = str(year)[-2:]
            url += f'TIGER2010/{query_type.upper()}/{year}/tl_2010_{state}_{query_type}{lastTwoDigits}.zip'
        elif year in {2008, 2009}:
            if query_type in {'state', 'county'} and state == 'us':
                url += f'TIGER{year}/tl_{year}_{state}_{query_type}.zip'
            else:
                full_state_name = get_state_name(state).upper().replace(" ", "_")
                query_type = query_type + "00"
                url += f'TIGER{year}/{state}_{full_state_name}/tl_{year}_{state}_{query_type}.zip'
        elif year > 2010:
            url += f'TIGER{year}/{query_type.upper()}/tl_{year}_{state}_{query_type}.zip'
        else:
            raise ValueError(f'Data for `cb = False` is only available for the years: 2000 and, 2008 onwards. Year specified: {year}')
    
    return url

def get_state_name(state_fips):
    table = get_state_fips_table()
    return table[table['fips'] == state_fips].name.iloc[0]


def load_tiger(url, refresh : bool = False, progress_bar: bool = True, use_cache: bool = False) -> gpd.GeoDataFrame:
    if use_cache and not os.path.exists(CACHE_PATH):
        os.makedirs(CACHE_PATH)
    
    tiger_file = url.split("/")[-1]
    filename = None
    df = None
    if use_cache:
        filename = CACHE_PATH / tiger_file
        # Check cache for compressed file
        if filename.exists() and not refresh:
            df = gpd.read_file('zip://' + str(filename.absolute()))
    
    if df is None:
        try:
            r = requests.get(url, stream=True, allow_redirects=True)
        except requests.HTTPError as e:
            raise ValueError(f"No data file exists at expected URL: {url}")
        if r.status_code != 200:
            r.raise_for_status()  # Will only raise for 4xx codes, so...
            raise RuntimeError(f"Request to {url} returned status code {r.status_code}")
        
        file_size = int(r.headers.get('Content-Length', 0))
        desc = "(Unknown total file size)" if file_size == 0 else ""
        r.raw.read = functools.partial(r.raw.read, decode_content=True)  # Decompress if needed
        df = None

        with (tqdm.wrapattr(r.raw, "read", total=file_size, desc=desc) if progress_bar else r.raw) as r_raw:
            if use_cache:
                with open(filename, "wb") as file:
                    shutil.copyfileobj(r_raw, file)
                df = gpd.read_file('zip://' + str(filename.absolute()))
            else:
                with tempfile.NamedTemporaryFile(suffix = '.zip') as file:
                    shutil.copyfileobj(r_raw, file)
                    file.seek(0)
                    df = gpd.read_file('zip://' + file.name)
    
    return standardise_df(df)

def standardise_df(df):
    df.set_crs(epsg = 4269)

    # Standardise columns ending with 00 or 10
    for col in list(df.columns):
        if col[-2:] in {'00', '10'}:
            df.rename(columns = {col: col[:-2]}, inplace = True)
    
    # for col in list(df.columns):
    #     if col[-2:] == 'FP':
    #         df.rename(columns = {col: col[:-2]}, inplace = True)

    if 'COUNTY' in df.columns:
        df.rename(columns = {'COUNTY': 'COUNTYFP'}, inplace = True)

    if 'STATE' in df.columns:
        df.rename(columns = {'STATE': 'STATEFP'}, inplace = True)
    
    if 'CO' in df.columns:
        df.rename(columns = {'CO': 'COUNTYFP'}, inplace = True)
    
    if 'ST' in df.columns:
        df.rename(columns = {'ST': 'STATEFP'}, inplace = True)
    return df

@functools.cache
def get_state_fips_table():
    path =  importlib.resources.files('pytigris')
    return pd.read_csv(path / 'data' / 'state_fips.csv', dtype = str)

@functools.cache
def get_county_fips_table():
    # Downloaded from https://www2.census.gov/geo/docs/reference/codes/files/national_county.txt
    path =  importlib.resources.files('pytigris')
    return pd.read_csv(path / 'data' / 'national_county.csv', dtype = str)

def clear_cache():
    if CACHE_PATH.exists():
        shutil.rmtree(CACHE_PATH)

def validate_state(state: str) -> Optional[str]:
    if not isinstance(state, str):
        raise ValueError("State is not a string")
    
    state_fips_table = get_state_fips_table()
    state = state.lower().strip()

    if state.isnumeric(): # Could be FIPS CODE
        if len(state) == 2 and state in state_fips_table.fips.values:
            return state
        elif len(state) > 2 and state[:2] in state_fips_table.fips.values:
            print(f"Warn: Using first 2 digits ({state[:2]}) from potential county or place FIPS {state}")
            return state[:2]

        raise ValueError(f"{state} is not a valid state FIPS code")
    
    # Could be name or abbreviation
    if state in state_fips_table.name.values:
        return state_fips_table[state_fips_table["name"] == state].fips.iloc[0]
    elif state in state_fips_table.abb.values:
        return state_fips_table[state_fips_table["abb"] == state].fips.iloc[0]


    raise ValueError(f"{state} is not a valid state FIPS code, name or abbreviation")


def validate_county(state: str, county: str) -> str:
    state = validate_state(state)
    if not isinstance(county, str):
        raise ValueError("County is not a string")

    county_table = get_county_fips_table()
    # Filter down to correct state
    county_table = county_table[county_table["ST_FIPS"] == state]

    if county.isnumeric(): # Could be FIPS CODE
        if len(county) == 3 and county in county_table.CT_FIPS.values:
            return county

        raise ValueError(f"{county} is not a valid county FIPS code for state {state}")
    

    # Could be name or abbreviation
    potetntial_counties_mask = county_table.CT_NAME.str.lower().str.contains(county.lower())

    if potetntial_counties_mask.sum() == 0:
        raise ValueError(f"No county by name '{county}' can be found for state {state}")
    elif potetntial_counties_mask.sum() == 1:
        county_record = county_table[potetntial_counties_mask].iloc[0]
        print(f"Found matching county '{county_record.CT_NAME}' for county '{county}' in state '{state}'")
        return county_record.CT_FIPS
    
    raise ValueError(f"Please refine selection. Multiple counties found for name '{county}' for state {state}:\n > " +'\n > '.join(county_table[potetntial_counties_mask].CT_NAME.tolist()))

    



    
