#layer_selector.py

from fiona import listlayers
import geopandas as gpd
import os

def get_simplest_layer(gpkg_path: str) -> list[str]:
    """
    Gibt den 'einfachsten' Layer einer Datei zurück.
    - Für GPKG: bevorzugt ADM_ADM_0, sonst Layer mit den wenigsten Geometrien.
    - Für Shapefiles: gibt [] zurück, da es nur einen Layer gibt.
    """
    ext = os.path.splitext(gpkg_path)[1].lower()
    if ext == ".shp":
        # Shapefile → kein Layername nötig
        return []

    layers = listlayers(gpkg_path)
    if "ADM_ADM_0" in layers:
        return ["ADM_ADM_0"]

    # Fallback: Layer mit den wenigsten Geometrien
    min_count = float("inf")
    best = None
    for layer in layers:
        try:
            gdf = gpd.read_file(gpkg_path, layer=layer)
            count = len(gdf)
            if count < min_count:
                min_count = count
                best = layer
        except Exception:
            continue

    return [best] if best else []