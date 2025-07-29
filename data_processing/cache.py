from functools import lru_cache
from typing import Tuple
from .layers import merge_hauptland_layers

@lru_cache(maxsize=32)
def cached_merge(
    main_gpkg: str,
    layers_key: Tuple[str, ...],
    crs: str
):
    """
    Caches das Ergebnis von merge_hauptland_layers für bestimmte Layer-Kombis.
    """
    hide_cfg = {"aktiv": False, "bereiche": {}}
    hl_cfg   = {"aktiv": False, "layer": "", "namen": []}
    layers   = list(layers_key)

    return merge_hauptland_layers(
        main_gpkg, layers, hide_cfg, hl_cfg, crs
    )