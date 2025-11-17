# data_processing/layers.py

import pandas as pd
import geopandas as gpd
from pathlib import Path
from typing import List, Dict, Any, Optional

def merge_hauptland_layers(
    gpkg_path: str,
    selected_layers: Optional[List[str]] = None,
    hide_cfg: Optional[Dict[str, Any]] = None,
    hl_cfg: Optional[Dict[str, Any]] = None,
    crs: str = "EPSG:4326"
) -> gpd.GeoDataFrame:
    path = Path(gpkg_path)
    dfs = []

    # --- Shapefile- oder "kein Layer"-Fall ---
    if not selected_layers:
        gdf = gpd.read_file(str(path))
        if crs:
            gdf = gdf.to_crs(crs)

        # NAME_-Spalte suchen oder Dummy anlegen
        name_col = next((c for c in gdf.columns if c.startswith("NAME_")), None)
        if name_col is None:
            gdf["__name_col"] = ""
            name_col = "__name_col"

        # Spalte für den Ursprungslayer hinzufügen (Shapefile → kein Layername)
        gdf["source_layer"] = "shapefile"

        # Hide nur anwenden, wenn Spalte existiert und Werte Strings sind
        if hide_cfg and hide_cfg.get("aktiv", False):
            bereiche = hide_cfg.get("bereiche", {})
            if (
                name_col in gdf.columns
                and name_col in bereiche
                and isinstance(bereiche[name_col], (list, set, tuple))
            ):
                to_hide = {v for v in bereiche[name_col] if isinstance(v, str)}
                if to_hide:
                    gdf = gdf[~gdf[name_col].isin(to_hide)]

        # Highlight nur anwenden, wenn Spalte existiert und Werte Strings sind
        if hl_cfg and hl_cfg.get("aktiv", False):
            hl_layer = hl_cfg.get("layer")
            if hl_layer in gdf.columns:
                names = {v for v in hl_cfg.get("namen", []) if isinstance(v, str)}
                gdf["highlight"] = gdf[hl_layer].isin(names)
            else:
                gdf["highlight"] = False
        else:
            gdf["highlight"] = False

        dfs.append(gdf)

    else:
        # --- GPKG mit Layernamen ---
        for layer in selected_layers:
            gdf = gpd.read_file(str(path), layer=layer)
            if crs:
                gdf = gdf.to_crs(crs)

            # Dynamisch passende NAME_-Spalte finden
            lvl = layer.split("_")[-1]
            name_col = f"NAME_{lvl}"
            if name_col not in gdf.columns:
                candidates = [c for c in gdf.columns if c.startswith("NAME_")]
                name_col = candidates[0] if candidates else None

            if name_col is None:
                gdf["__name_col"] = ""
                name_col = "__name_col"

            # Spalte für den Ursprungslayer hinzufügen
            gdf["source_layer"] = layer

            # Hide nur anwenden, wenn Spalte existiert
            if hide_cfg and hide_cfg.get("aktiv", False):
                bereiche = hide_cfg.get("bereiche", {})
                if (
                    name_col in gdf.columns
                    and layer in bereiche
                    and isinstance(bereiche[layer], (list, set, tuple))
                ):
                    to_hide = {v for v in bereiche[layer] if isinstance(v, str)}
                    if to_hide:
                        gdf = gdf[~gdf[name_col].isin(to_hide)]

            # Highlight nur anwenden, wenn Spalte existiert
            if hl_cfg and hl_cfg.get("aktiv", False):
                if hl_cfg.get("layer") == layer and name_col in gdf.columns:
                    names = {v for v in hl_cfg.get("namen", []) if isinstance(v, str)}
                    gdf["highlight"] = gdf[name_col].isin(names)
                else:
                    gdf["highlight"] = False
            else:
                gdf["highlight"] = False

            dfs.append(gdf)

    merged = pd.concat(dfs, ignore_index=True)
    return gpd.GeoDataFrame(merged, geometry=dfs[0].geometry.name, crs=dfs[0].crs)