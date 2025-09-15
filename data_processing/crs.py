# data_processing/crs.py

import json
from pathlib import Path
import geopandas as gpd
from typing import Tuple

# ---- Config laden ----
# Annahme: config/config.json im Projekt-Root
_CONFIG_PATH = (
    Path(__file__).resolve().parent.parent
    / "config"
    / "config.json"
)
try:
    with _CONFIG_PATH.open(encoding="utf-8") as _f:
        _CONFIG    = json.load(_f)
        _KARTE_CFG = _CONFIG.get("karte", {})
except Exception:
    _KARTE_CFG = {}

# Padding-Werte aus Config (Default 5%)
PADDING_X = _KARTE_CFG.get("padding_x", 0.05)
PADDING_Y = _KARTE_CFG.get("padding_y", 0.05)


def reproject(gdf: gpd.GeoDataFrame, target_crs: str) -> gpd.GeoDataFrame:
    """
    Reprojiziert das GeoDataFrame ins target_crs.
    """
    return gdf.to_crs(target_crs)


def compute_bbox(
    gdf: gpd.GeoDataFrame,
    aspect_ratio: float
) -> Tuple[float, float, float, float]:
    """
    Berechnet ein Bounding-Box-Tuple (xmin, xmax, ymin, ymax),
    das das gegebene GeoDataFrame mit dem gewünschten Seitenverhältnis
    umschließt und dabei PADDING_X / PADDING_Y aus der Config anwendet.
    """
    minx, miny, maxx, maxy = gdf.total_bounds
    width, height = maxx - minx, maxy - miny
    center_x, center_y = (minx + maxx) / 2, (miny + maxy) / 2

    current_ratio = width / height
    if current_ratio > aspect_ratio:
        new_width = width
        new_height = width / aspect_ratio
    else:
        new_height = height
        new_width = height * aspect_ratio

    # Padding aus config.json
    new_width *= (1 + PADDING_X)
    new_height *= (1 + PADDING_Y)

    xmin = center_x - new_width / 2
    xmax = center_x + new_width / 2
    ymin = center_y - new_height / 2
    ymax = center_y + new_height / 2

    return xmin, xmax, ymin, ymax