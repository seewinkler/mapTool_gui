from fiona import listlayers
import geopandas as gpd

def get_simplest_layer(gpkg_path: str) -> list[str]:
    layers = listlayers(gpkg_path)
    if "ADM_ADM_0" in layers:
        return ["ADM_ADM_0"]
    
    # Fallback: Layer mit wenigsten Geometrien
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