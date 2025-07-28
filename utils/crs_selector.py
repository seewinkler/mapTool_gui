# utils/crs_selector.py

import json
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional

# Modul­verzeichnis (utils/)
BASE_DIR = Path(__file__).resolve().parent

# Pfade zur Konfiguration und zur EPSG-Liste
CONFIG_PATH     = BASE_DIR.parent / "config" / "config.json"
EPSG_LIST_PATH  = BASE_DIR.parent / "assets" / "epsg_list.json"


def load_config(path: Path = CONFIG_PATH) -> Dict[str, Any]:
    """
    Lädt die Haupt-Konfiguration (config.json) und gibt sie als Dict zurück.
    """
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_regions(config: Dict[str, Any]) -> List[str]:
    """
    Gibt eine Liste der in der Konfiguration definierten Regionen zurück.
    """
    return list(config.get("regionen", {}))


def select_region(
    config: Dict[str, Any], index: int
) -> Tuple[str, List[str]]:
    """
    Wählt eine Region per 0-based Index aus.
    Rückgabe: (regions_name, Sublayer-Keys).
    """
    regions = get_regions(config)
    name = regions[index]
    return name, config["regionen"][name]


def load_epsg_list(path: Path = EPSG_LIST_PATH) -> List[Dict[str, Any]]:
    """
    Lädt die EPSG-Liste (assets/epsg_list.json) und gibt sie als Liste von Dicts zurück.
    Jeder Eintrag enthält:
      - 'land':       Name des Landes
      - 'epsg':       EPSG-Code (Integer)
      - 'projektion': Beschreibung der Projektion
      - 'hinweis':    ggf. zusätzlicher Hinweis
    """
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_country_names(epsg_list: List[Dict[str, Any]]) -> List[str]:
    """
    Extrahiert die Länderbezeichnungen aus der geladenen EPSG-Liste.
    """
    return [entry["land"] for entry in epsg_list]


def select_country_by_index(
    epsg_list: List[Dict[str, Any]], index: int
) -> Dict[str, Any]:
    """
    Wählt ein Land per 0-based Index aus der EPSG-Liste aus.
    Rückgabe-Dict enthält:
      - 'land'       (str)
      - 'epsg'       (str im Format 'EPSG:<code>')
      - 'projektion' (str)
      - 'hinweis'    (str)
    """
    entry = epsg_list[index]
    return {
        "land":       entry["land"],
        "epsg":       f"EPSG:{entry['epsg']}",
        "projektion": entry.get("projektion", ""),
        "hinweis":    entry.get("hinweis", ""),
    }


def select_country_by_name(
    epsg_list: List[Dict[str, Any]], name: str
) -> Optional[Dict[str, Any]]:
    """
    Wählt ein Land anhand seines Namens aus der EPSG-Liste aus.
    Gibt bei Erfolg das Auswahl-Dict (siehe select_country_by_index) zurück,
    sonst None.
    """
    for entry in epsg_list:
        if entry["land"] == name:
            return {
                "land":       entry["land"],
                "epsg":       f"EPSG:{entry['epsg']}",
                "projektion": entry.get("projektion", ""),
                "hinweis":    entry.get("hinweis", ""),
            }
    return None