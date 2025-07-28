# cli.py

import logging
from typing import Tuple, List, Set, Dict, Optional

from rich.logging import RichHandler

logger = logging.getLogger("mymaptool.cli")
logger.setLevel(logging.INFO)
handler = RichHandler(rich_tracebacks=True)
logger.addHandler(handler)


def parse_mode(ans: str) -> bool:
    """
    Parse user input for mode selection.
    Returns:
      False = normal mode
      True  = special mode
    Raises ValueError on invalid input.
    """
    val = ans.strip().lower()
    if val.startswith("n"):
        return False
    if val.startswith("s"):
        return True
    raise ValueError("Ungültige Eingabe für Modus. Erwartet 'n' oder 's'.")


BACKGROUND_OPTIONS: List[Tuple[str, Tuple[Optional[str], bool]]] = [
    ("Meeresblau   (#2896BA)", ("#2896BA", False)),
    ("Transparent (PNG-Hintergrund)", (None, True)),
]


def get_background_labels() -> List[str]:
    """
    Return labels for background options in display order.
    """
    return [label for label, _ in BACKGROUND_OPTIONS]


def parse_background_option(choice: int) -> Dict[str, object]:
    """
    Parse background option by 1-based index.
    Returns a dict with keys 'color' and 'transparent'.
    Raises IndexError on invalid index.
    """
    label, (color, transp) = BACKGROUND_OPTIONS[choice - 1]
    return {"color": color or "none", "transparent": transp}


def compute_dimensions(
    is_special: bool,
    config: Dict,
    custom_dimensions: Optional[Tuple[int, int]] = None
) -> Tuple[int, int]:
    """
    Compute map dimensions in pixels.
    - Normal mode: values from config['karte'].
    - Special mode: values from custom_dimensions.
    Raises ValueError if custom_dimensions are invalid.
    """
    if not is_special:
        w = config["karte"]["breite"]
        h = config["karte"]["hoehe"]
        logger.info(f"Normalmodus: Verwende {w}×{h} px aus config.json.")
        return w, h

    if not custom_dimensions or len(custom_dimensions) != 2:
        raise ValueError("Für Spezialmodus müssen Breite und Höhe angegeben werden.")
    w, h = custom_dimensions
    if w <= 0 or h <= 0:
        raise ValueError("Spezialmodus: Breite und Höhe müssen größer als 0 sein.")
    logger.info(f"Spezialmodus: Verwende benutzerdefinierte Größe {w}×{h} px.")
    return w, h


def get_regions(config: Dict[str, List[str]]) -> List[str]:
    """
    Return a list of region names from config.
    """
    regions = list(config.get("regionen", {}))
    if not regions:
        logger.error("Keine Regionen in der Konfiguration gefunden.")
        raise ValueError("Keine Regionen in der Konfiguration gefunden.")
    return regions


def parse_region(
    choice: int,
    config: Dict[str, List[str]]
) -> Tuple[str, List[str]]:
    """
    Select region by 1-based index.
    Returns (region_name, sublayers_list).
    Raises IndexError on invalid index.
    """
    regions = get_regions(config)
    region_name = regions[choice - 1]
    return region_name, config["regionen"][region_name]


SCALebAR_OPTIONS: List[Tuple[str, Tuple[Optional[str], bool]]] = [
    ("links unten", ("bottom-left", True)),
    ("rechts unten", ("bottom-right", True)),
    ("mitte unten", ("bottom-center", True)),
    ("keine Scalebar", (None, False)),
]


def get_scalebar_labels() -> List[str]:
    """
    Return labels for scalebar options in display order.
    """
    return [label for label, _ in SCALebAR_OPTIONS]


def parse_scalebar_option(choice: int) -> Dict[str, object]:
    """
    Parse scalebar option by 1-based index.
    Returns a dict with keys 'show' and 'position'.
    Raises IndexError on invalid index.
    """
    _, (pos, show) = SCALebAR_OPTIONS[choice - 1]
    return {"show": show, "position": pos or "bottom-left"}


EXPORT_FORMAT_OPTIONS: Dict[int, Set[str]] = {
    1: {"png"},
    2: {"svg"},
    3: {"png", "svg"}
}


def parse_export_formats(choice: int) -> Set[str]:
    """
    Select export formats by 1-based index.
    Returns a set of formats. Defaults to {'png'} on invalid choice.
    """
    return EXPORT_FORMAT_OPTIONS.get(choice, {"png"})