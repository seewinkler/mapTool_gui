# utils/region_filter.py

import geopandas as gpd
import fiona
from pathlib import Path
from typing import List, Set, Dict, Any


def list_layers(gpkg_path: Path) -> List[str]:
    """
    Gibt alle Layer-Namen in einem GeoPackage zurück.
    """
    return fiona.listlayers(str(gpkg_path))


def list_region_names(
    gpkg_path: Path,
    layer: str,
    name_field: str = "NAME_1"
) -> List[str]:
    """
    Liest einen Layer aus und gibt alle eindeutigen Einträge
    aus `name_field` sortiert zurück.
    """
    gdf = gpd.read_file(str(gpkg_path), layer=layer)
    names = gdf[name_field].dropna().unique().tolist()
    return sorted(names)


def filter_regions_by_indices(
    region_names: List[str],
    indices: List[int]
) -> List[str]:
    """
    Wählt Regionen mittels 0-basierter Indizes aus und
    ignoriert ungültige Indizes.
    """
    return [region_names[i] for i in indices if 0 <= i < len(region_names)]


def compute_hide_config(
    gpkg_path: Path,
    used_layers: List[str],
    layer_choice: int,
    region_indices: List[int]
) -> Dict[str, Any]:
    """
    Baut das Dict für `MapComposer.set_ausblenden()`:
      {
        "aktiv": bool,
        "bereiche": { layer_name: [region1, region2, …] }
      }
    """
    if not (0 <= layer_choice < len(used_layers)):
        return {"aktiv": False, "bereiche": {}}

    layer = used_layers[layer_choice]
    names = list_region_names(gpkg_path, layer, name_field="NAME_1")
    to_hide = filter_regions_by_indices(names, region_indices)

    if not to_hide:
        return {"aktiv": False, "bereiche": {}}

    return {"aktiv": True, "bereiche": {layer: to_hide}}


def compute_highlight_config(
    gpkg_path: Path,
    used_layers: List[str],
    layer_choice: int,
    region_indices: List[int],
    forbidden_names: Set[str] = None,
    name_field: str = "NAME_1"
) -> Dict[str, Any]:
    """
    Baut das Dict für Hervorhebung:
      {
        "aktiv": bool,
        "layer": str,
        "namen": [region1, region2, …]
      }
    Regionen in `forbidden_names` werden ausgeschlossen.
    """
    if not (0 <= layer_choice < len(used_layers)):
        return {"aktiv": False, "layer": "", "namen": []}

    layer = used_layers[layer_choice]
    names = list_region_names(gpkg_path, layer, name_field)

    if forbidden_names:
        names = [n for n in names if n not in forbidden_names]

    to_highlight = filter_regions_by_indices(names, region_indices)
    if not to_highlight:
        return {"aktiv": False, "layer": "", "namen": []}

    return {"aktiv": True, "layer": layer, "namen": to_highlight}