# data_processing/cache.py

import os
from functools            import lru_cache
from typing               import Tuple
from concurrent.futures   import ProcessPoolExecutor

import geopandas as gpd
import pandas    as pd

# ursprüngliche merge-Funktion entfällt,
# wir machen das gleich hier selbst parallel:
# from .layers import merge_hauptland_layers

def _read_and_reproject(args):
    """
    Liest eine einzelne Layer aus dem GeoPackage
    und reprojiziert sie ins Ziel-CRS.
    """
    gpkg, layer, crs = args
    gdf = gpd.read_file(gpkg, layer=layer)
    return gdf.to_crs(crs)


@lru_cache(maxsize=32)
def cached_merge(
    main_gpkg: str,
    layers_key: Tuple[str, ...],
    crs: str
):
    """
    Liest alle angegebenen Layer parallel, reprojiziert
    sie und merged sie zu einem GeoDataFrame.
    """
    # 1) Vorbereitung der Tasks
    layers = list(layers_key)
    tasks  = [(main_gpkg, lyr, crs) for lyr in layers]

    # 2) Parallel einlesen und reprojizieren
    max_workers = os.cpu_count() or 1
    with ProcessPoolExecutor(max_workers=max_workers) as exe:
        gdfs = list(exe.map(_read_and_reproject, tasks))

    # 3) Zusammenführen
    merged = pd.concat(gdfs, ignore_index=True)
    merged = gpd.GeoDataFrame(merged, crs=crs)

    return merged