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
    path = Path(gpkg_path)
    dfs = []

    for layer in selected_layers:
        gdf = gpd.read_file(str(path), layer=layer)

        if crs:
            gdf = gdf.to_crs(crs)

        # Dynamisch passende NAME_-Spalte finden
        lvl = layer.split("_")[-1]  # z.B. "1", "2", "3", "4"
        name_col = f"NAME_{lvl}"
        if name_col not in gdf.columns:
            candidates = [c for c in gdf.columns if c.startswith("NAME_")]
            name_col = candidates[0] if candidates else None

        # Falls keine Namensspalte gefunden → Dummy-Spalte
        if name_col is None:
            gdf["__name_col"] = ""
            name_col = "__name_col"

        # 1) Ausblenden
        if hide_cfg and hide_cfg.get("aktiv", False):
            bereiche = hide_cfg.get("bereiche", {})
            if layer in bereiche:
                to_hide = set(bereiche[layer])
                gdf = gdf[~gdf[name_col].isin(to_hide)]

        # 2) Hervorheben markieren
        if hl_cfg and hl_cfg.get("aktiv", False):
            if hl_cfg.get("layer") == layer:
                names = set(hl_cfg.get("namen", []))
                gdf["highlight"] = gdf[name_col].isin(names)
            else:
                gdf["highlight"] = False
        else:
            gdf["highlight"] = False

        dfs.append(gdf)

    merged = pd.concat(dfs, ignore_index=True)
    merged = gpd.GeoDataFrame(merged, geometry=dfs[0].geometry.name, crs=dfs[0].crs)
    return merged