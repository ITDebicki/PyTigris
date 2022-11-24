import datetime
from .util import *
import geopandas as gpd
from typing import Optional, Union, Iterable


def get_states(cb: bool = False, resolution: str = '500k', year: Optional[int] = None, refresh : bool = False, progress_bar: bool = True, use_cache: bool = False) -> gpd.GeoDataFrame:
    """Download shapefile for all states.
    
    States and Equivalent Entities are the primary governmental divisions of the
    United States.  In addition to the 50 states, the Census Bureau treats the
    District of Columbia, Puerto Rico, American Samoa, the Commonwealth of the
    Northern Mariana Islands, Guam, and the U.S. Virgin Islands as the statistical
    equivalents of states for the purpose of data presentation.

    Args:
        cb (bool, optional): If cb (cartographic boundaries) is set to True, download a generalized (1:500k) states file. Defaults to False.
        resolution (str, optional): The resolution of the cartographic boundary file (if cb == True). Options are: '500k', '5m', '20m'. Defaults to '500k'.
        year (Optional[int], optional): The year for which to fetch the boundaries. Pre 2010, only 1990, 2000 and 2010 are available. Defaults to None (year before current).
        refresh (bool, optional): If to refresh the cached file (if use_cache = True). Defaults to False.
        progress_bar (bool, optional): If to display the progress bar for download. Defaults to True.
        use_cache (bool, optional): If to utilise the cache for the downloaded zip file. Defaults to False.

    Raises:
        ValueError: If invalid resolution is specified
        ValueError: If cb (cartographic boundaries) is False and year is 1990

    Returns:
        gpd.GeoDataFrame: GeoDataFrame of state boundaries from the given year
    """
    if resolution not in {'500k', '5m', '20m'}:
        raise ValueError(f"Invalid resolution value: '{resolution}'. Should be one of: '500k', '5m', '20m'")
    
    if year is None:
        # Be safe and use previous year (use leap year num days)
        year = (datetime.date.today() - datetime.timedelta(days = 366)).year
        # Log retrieving date if not specified
        if progress_bar:
            print(f"Retrieving data for the year: {year}")
    
    url = construct_url(year, 'state', cb, resolution)

    df = load_tiger(url, refresh = refresh, progress_bar = progress_bar, use_cache = use_cache)

    if cb and year in {1990, 2000}:
        df = df.dissolve('STATEFP', aggfunc = {"AREA": sum, "PERIMETER": sum}).join(
            df.loc[:, ~df.columns.isin({'geometry', 'AREA', 'PERIMETER'})].groupby('STATEFP').first()
        ).reset_index()

    return df

def get_counties(states: Optional[Union[str, Iterable[str]]] = None, cb: bool = False, resolution: str = '500k', year: Optional[int] = None, refresh : bool = False, progress_bar: bool = True, use_cache: bool = False) -> gpd.GeoDataFrame:
    """Download a US Counties shapefile, and optionally subset by state

Description from the US Census Bureau (see link for source):
    The primary legal divisions of most states are termed counties. In Louisiana,
    these divisions are known as parishes.  In Alaska, which has no counties,
    the equivalent entities are the organized boroughs, city and boroughs,
    municipalities, and census areas; the latter of which are delineated
    cooperatively for statistical purposes by the state of Alaska and the
    Census Bureau.  In four states (Maryland, Missouri, Nevada, and Virginia),
    there are one or more incorporated places that are independent of any county
    organization and thus constitute primary divisions of their states.  These
    incorporated places are known as independent cities and are treated as
    equivalent entities for purposes of data presentation.  The District of
    Columbia and Guam have no primary divisions, and each area is considered
    an equivalent entity for purposes of data presentation.  All of the counties
    in Connecticut and Rhode Island and nine counties in Massachusetts were
    dissolved as functioning governmental entities; however, the Census Bureau
    continues to present data for these historical entities in order to provide
    comparable geographic units at the county level of the geographic hierarchy
    for these states and represents them as nonfunctioning legal entities in
    data products.  The Census Bureau treats the following entities as
    equivalents of counties for purposes of data presentation: municipios in
    Puerto Rico, districts and islands in American Samoa, municipalities in the
    Commonwealth of the Northern Mariana Islands, and islands in the U.S.
    Virgin Islands.  Each county or statistically equivalent entity is assigned
    a three-character numeric Federal Information Processing Series (FIPS) code
    based on alphabetical sequence that is unique within state and an
    eight-digit National Standard feature identifier.

    Args:
        states (Optional[Union[str, Iterable[str]]], optional): The two-digit FIPS code (string) of the state you want, or a list of codes if you want multiple states. Can also be state name or state abbreviation. Defaults to None (All states).
        cb (bool, optional): If cb (cartographic boundaries) is set to True, download a generalized (1:500k) counties file. Defaults to False.
        resolution (str, optional): The resolution of the cartographic boundary file (if cb == True). Options are: '500k', '5m', '20m'. Defaults to '500k'.
        year (Optional[int], optional): The year for which to fetch the boundaries. Pre 2010, only 1990, 2000 and 2010 are available. Defaults to None (year before current).
        refresh (bool, optional): If to refresh the cached file (if use_cache = True). Defaults to False.
        progress_bar (bool, optional): If to display the progress bar for download. Defaults to True.
        use_cache (bool, optional): If to utilise the cache for the downloaded zip file. Defaults to False.

    Raises:
        ValueError: If invalid resolution is specified
        ValueError: If cb (cartographic boundaries) is False and year is 1990

    Returns:
        gpd.GeoDataFrame: GeoDataFrame of county boundaries from the given year for the given state(s).
    """
    if resolution not in {'500k', '5m', '20m'}:
        raise ValueError(f"Invalid resolution value: '{resolution}'. Should be one of: '500k', '5m', '20m'")
    
    if states:
        if isinstance(states, str):
            states = [states]
        states = [validate_state(state) for state in states]
    
    if year is None:
        year = (datetime.date.today() - datetime.timedelta(days = 366)).year
        # Log retrieving date if not specified
        if progress_bar:
            print(f"Retrieving data for the year: {year}")
    
    url = construct_url(year, 'county', cb, resolution)
    
    df = load_tiger(url, refresh = refresh, progress_bar = progress_bar, use_cache = use_cache)

    if cb and year in {1990, 2000}:
        df = df.dissolve(['STATEFP', "COUNTYFP"], aggfunc = {"AREA": sum, "PERIMETER": sum}).join(
            df.loc[:, ~df.columns.isin({'geometry', 'AREA', 'PERIMETER'})].groupby(['STATEFP', "COUNTYFP"]).first()
        ).reset_index()

    
    if states and len(states) > 0:
        return df[df["STATEFP"].isin(states)]
    else:
        return df

    
def get_tracts(state:Optional[str] = None, counties:Optional[Union[str, Iterable[str]]] = None, year: Optional[int] = None, cb: bool = False, refresh : bool = False, progress_bar: bool = True, use_cache: bool = False) -> gpd.GeoDataFrame:
    """Download a Census tracts shapefile, and optionally subset by county

Description from the US Census Bureau (see link for source):
        Census Tracts are small, relatively permanent statistical subdivisions of
        a county or equivalent entity that are updated by local participants prior
        to each decennial census as part of the Census Bureau's Participant
        Statistical Areas Program. The Census Bureau delineates census tracts in
        situations where no local participant existed or where state, local, or
        tribal governments declined to participate. The primary purpose of census
        tracts is to provide a stable set of geographic units for the presentation
        of statistical data.

        Census tracts generally have a population size between 1,200 and 8,000 people,
        with an optimum size of 4,000 people. A census tract usually covers a
        contiguous area; however, the spatial size of census tracts varies widely
        depending on the density of settlement.  Census tract boundaries are
        delineated with the intention of being maintained over a long time so that
        statistical comparisons can be made from census to census. Census tracts
        occasionally are split due to population growth or merged as a result of
        substantial population decline.

        Census tract boundaries generally follow visible and identifiable features.
        They may follow nonvisible legal boundaries, such as minor civil division
        (MCD) or incorporated place boundaries in some states and situations, to
        allow for census-tract-to-governmental-unit relationships where the
        governmental boundaries tend to remain unchanged between censuses.  State and
        county boundaries always are census tract boundaries in the standard census
        geographic hierarchy.

    Args:
        state (Optional[str], optional): The two-digit FIPS code (string) of the state you want.
                                        Can also be state name or state abbreviation.
                                        When None and combined with cb = True, a national dataset of Census tracts will be
                                        returned for years 2019 and later.
                                        Defaults to None.
        counties (Optional[Union[str, Iterable[str]]], optional): The three-digit FIPS code (string) of the county you'd like to subset for,
                                                                    or an iterable of FIPS codes if you desire multiple counties.
                                                                    Can also be a county name or iterable of names. Defaults to None.
        year (Optional[int], optional): The year for which to fetch the boundaries.
                                        Pre 2010, only 1990, 2000 and 2010 are available. Defaults to None (year before current).
        cb (bool, optional): If cb (cartographic boundaries) is set to True,
                             download a generalized (1:500k) tracts file. Defaults to False.
        refresh (bool, optional): If to refresh the cached file (if use_cache = True). Defaults to False.
        progress_bar (bool, optional): If to display the progress bar for download. Defaults to True.
        use_cache (bool, optional): If to utilise the cache for the downloaded zip file. Defaults to False.

    Raises:
        ValueError: If invalid year combination, or state or county is invalid.

    Returns:
        gpd.GeoDataFrame: GeoDataFrame of tract boundaries from the given year for the given state(s) and counties.
    """
    if year is None:
        year = (datetime.date.today() - datetime.timedelta(days = 366)).year
        # Log retrieving date if not specified
        if progress_bar:
            print(f"Retrieving data for the year: {year}")

    if state is None:
        if year > 2018 and cb:
            state = 'us'
        else:
            raise ValueError("Must set year > 2018 and cb = True to retrieve tracts for entire US.")
    else:
        state = validate_state(state)

    url = construct_url(year, 'tract', cb, '500k', state)

    df = load_tiger(url, refresh, progress_bar, use_cache)

    if counties is not None:
        if isinstance(counties, str):
            counties = [counties]
        counties = {validate_county(state, county) for county in counties}

        df = df[df["COUNTYFP"].isin(counties)]

    if cb and year in {1990, 2000}:
        if year == 1990:
            df["TRACTSUF"].fillna('00', inplace = True)
            df["TRACT"] = df["TRACTBASE"].astype('str') + df["TRACTSUF"].astype('str')
        else:
            df["TRACT"] = df["TRACT"].str.pad(6, fillchar='0')
        df = df.dissolve(['STATEFP', "COUNTYFP", "TRACT"], aggfunc = {"AREA": sum, "PERIMETER": sum}).join(
            df.loc[:, ~df.columns.isin({'geometry', 'AREA', 'PERIMETER'})].groupby(['STATEFP', "COUNTYFP", "TRACT"]).first()
        ).reset_index()

    return df
    
    






    

