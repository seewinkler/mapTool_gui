import json
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Union
import copy

# Basis-Verzeichnis (Projekt-Root)
BASE_DIR = Path(__file__).parent.parent

# Standard-Pfad zur JSON-Konfigurationsdatei
DEFAULT_CONFIG_PATH = BASE_DIR / "config" / "config.json"


def setup_logging(log_cfg: dict):
    """
    Initialisiert das Logging mit RotatingFileHandler.
    Erwartete Schlüssel in log_cfg:
      - level: INFO, DEBUG, …
      - file: Pfad zur Log-Datei (relativ zu BASE_DIR oder absolut)
      - maxBytes: maximale Dateigröße in Bytes
      - backupCount: Anzahl der Backups
      - suppress_modules: Liste von Modul-Namen, die auf WARNING gesetzt werden
    """
    level = log_cfg.get("level", "INFO").upper()
    log_file = log_cfg.get("file", "app.log")
    max_bytes = log_cfg.get("maxBytes", 5 * 1024 * 1024)
    backup_count = log_cfg.get("backupCount", 3)

    # Pfad auflösen
    log_path = Path(log_file)
    if not log_path.is_absolute():
        log_path = BASE_DIR / log_path

    # Verzeichnis erstellen, falls notwendig
    log_path.parent.mkdir(parents=True, exist_ok=True)

    # Handler und Formatter
    handler = RotatingFileHandler(
        filename=str(log_path),
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding="utf-8",
    )
    handler.setFormatter(
        logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    )

    # Root-Logger konfigurieren
    root = logging.getLogger()
    root.setLevel(getattr(logging, level, logging.INFO))
    root.addHandler(handler)

    # Module unterdrücken
    for module_name in log_cfg.get("suppress_modules", []):
        logging.getLogger(module_name).setLevel(logging.WARNING)


def load_config(path: Union[str, Path] = None) -> dict:
    """
    Lädt die JSON-Konfiguration, richtet Logging ein
    und liest optional die EPSG-Liste (assets/epsg_list.json).
    """
    cfg_path = Path(path) if path else DEFAULT_CONFIG_PATH
    if not cfg_path.is_absolute():
        cfg_path = BASE_DIR / cfg_path
    if not cfg_path.exists():
        raise FileNotFoundError(f"Config nicht gefunden: {cfg_path}")

    config = json.loads(cfg_path.read_text(encoding="utf-8"))

    # Logging initialisieren
    log_cfg = config.setdefault("logging", {})
    setup_logging(log_cfg)

    # EPSG-Liste aus assets/epsg_list.json laden
    assets = config.get("assets", {})
    epsg_rel = assets.get("epsg_list")
    if epsg_rel:
        epsg_path = BASE_DIR / epsg_rel
        if epsg_path.exists():
            config["epsg_list"] = json.loads(
                epsg_path.read_text(encoding="utf-8")
            )
        else:
            logging.getLogger(__name__).warning(
                "epsg_list.json nicht gefunden: %s", epsg_path
            )
    else:
        config["epsg_list"] = []

    return config


class ConfigManager:
    """
    Verwaltet Basis-Config (aus config.json) und Session-Config (Laufzeit).
    - Basis-Config wird nur einmal geladen und nie verändert.
    - Session-Config ist eine Kopie, die alle User-Änderungen enthält.
    """

    def __init__(self, base_config: dict):
        self._base = base_config
        self._session = copy.deepcopy(base_config)

    def get_session(self) -> dict:
        """Gibt die aktuelle Session-Config zurück."""
        return self._session

    def update_session(self, key: str, value):
        """Aktualisiert einen Wert in der Session-Config."""
        self._session[key] = value

    def reset_session(self):
        """Setzt die Session-Config auf die Basis-Config zurück."""
        self._session = copy.deepcopy(self._base)

    def get_base(self) -> dict:
        """Gibt die unveränderte Basis-Config zurück (nur lesen!)."""
        return self._base


# Basis-Config laden
BASE_CONFIG = load_config()

# ConfigManager initialisieren
config_manager = ConfigManager(BASE_CONFIG)

# Shortcut für Scalebar-Settings
SCALER = BASE_CONFIG.get("scalebar", {})
