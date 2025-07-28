# io_utils.py

import os
import geopandas as gpd
from typing import Tuple, List


def find_gpkg_files(
    hauptland_dir: str,
    nebenlaender_dir: str,
    nebenlayer_name: str
) -> Tuple[str, List[gpd.GeoDataFrame]]:
    """
    Findet im Verzeichnis hauptland_dir die erste .gpkg-Datei
    und lädt aus nebenlaender_dir alle .gpkg-Dateien als GeoDataFrames
    unter Verwendung des Layers nebenlayer_name.
    Liefert (pfad_haupt_gpkg, [gdf_neben1, gdf_neben2, ...]).
    """
    # Hauptland-GPKG finden
    haupt_files = [f for f in os.listdir(hauptland_dir) if f.endswith(".gpkg")]
    if not haupt_files:
        raise FileNotFoundError(f"Keine .gpkg im Ordner {hauptland_dir}")
    haupt_path = os.path.join(hauptland_dir, haupt_files[0])

    # Nebenländer laden
    neben_gdfs: List[gpd.GeoDataFrame] = []
    for fname in os.listdir(nebenlaender_dir):
        if not fname.endswith(".gpkg"):
            continue
        pfad = os.path.join(nebenlaender_dir, fname)
        gdf = gpd.read_file(pfad, layer=nebenlayer_name)
        neben_gdfs.append(gdf)

    return haupt_path, neben_gdfs