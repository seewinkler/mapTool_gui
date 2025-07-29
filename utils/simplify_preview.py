#utils/simplify_preview.py

from geopandas import GeoDataFrame

def simplify_for_preview(
    gdf: GeoDataFrame, 
    layer_types: list, 
    count: int,
    layer_names: list = None
) -> GeoDataFrame:
    """
    Dynamisch vereinfachen basierend auf Layer-Typ, Anzahl und Layer-Namen
    """
    tolerance = 1.0

    # Feature-Anzahl
    if count > 5:
        tolerance = 3.0
    if count > 10:
        tolerance = 8.0

    # Geometrietypen gewichten
    if "line" in layer_types:
        tolerance *= 1.5
    if "polygon" in layer_types:
        tolerance *= 1.2
    if "point" in layer_types:
        tolerance *= 0.5

    # Spezielle Layer wie adm_adm_0 vereinfachen weniger
    if layer_names:
        if any("adm_adm_0" in name for name in layer_names):
            tolerance *= 0.5  # sehr grobe Verwaltung – weniger Vereinfachung
        if any("adm_adm_4" in name for name in layer_names):
            tolerance *= 1.2  # feinere Verwaltung – ruhig stärker vereinfachen
    print(f"Simplify-Toleranz für {layer_names}: {tolerance}")
    return gdf.simplify(tolerance, preserve_topology=True)