# data_processing/layers.py

import pandas as pd
import geopandas as gpd

from pathlib import Path
from typing import List, Dict, Any, Optional


def merge_hauptland_layers(
    gpkg_path: str,
    selected_layers: List[str],
    hide_cfg: Optional[Dict[str, Any]] = None,
    hl_cfg: Optional[Dict[str, Any]] = None,
    crs: str = "EPSG:4326"
) -> gpd.GeoDataFrame:
    """
    Lädt die ausgewählten Hauptland-Layer, merged sie in ein GeoDataFrame
    und wendet optional Ausblend- und Hervorhebungs-Config an.

    Parameter:
    - gpkg_path: Pfad zur GPKG-Datei
    - selected_layers: Liste der Layer-Namen
    - hide_cfg: Dict mit {'aktiv': bool, 'bereiche': {layer: [region1, ...]}}
    - hl_cfg: Dict mit {'aktiv': bool, 'layer': str, 'namen': [region1, ...]}
    - crs: Ziel-CRS für alle GeoDataFrames

    Rückgabe:
    - Geopandas GeoDataFrame mit allen Features (ggf. markiert für Hervorhebung)
    """
    path = Path(gpkg_path)
    dfs = []

    for layer in selected_layers:
        gdf = gpd.read_file(str(path), layer=layer)

        if crs:
            gdf = gdf.to_crs(crs)

        # 1) Ausblenden
        if hide_cfg and hide_cfg.get("aktiv", False):
            bereiche = hide_cfg.get("bereiche", {})
            if layer in bereiche:
                to_hide = set(bereiche[layer])
                gdf = gdf[~gdf["NAME_1"].isin(to_hide)]

        # 2) Hervorheben markieren
        if hl_cfg and hl_cfg.get("aktiv", False):
            if hl_cfg.get("layer") == layer:
                names = set(hl_cfg.get("namen", []))
                gdf["highlight"] = gdf["NAME_1"].isin(names)
            else:
                gdf["highlight"] = False
        else:
            gdf["highlight"] = False

        dfs.append(gdf)

    # 3) Alle DataFrames aneinanderhängen
    merged = pd.concat(dfs, ignore_index=True)
    # Sicherstellen, dass merged ein GeoDataFrame bleibt
    merged = gpd.GeoDataFrame(merged, geometry=dfs[0].geometry.name, crs=dfs[0].crs)

    return merged