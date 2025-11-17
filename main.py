#main.py

import sys
import os

print("▶ Starte GUI-EntryPoint aus", __file__)

# Projekt-Root ins sys.path (damit gui/ und utils/ als Packages erkannt werden)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Logging & Config
from utils.config import config_manager  # Zugriff auf ConfigManager

# Basis-Config für Logging
BASE_CONFIG = config_manager.get_base()
from utils.logging_config import setup_logging
setup_logging(BASE_CONFIG["logging"])  # Logging bleibt auf Basis der Original-Config

# Session-Config abrufen
SESSION_CONFIG = config_manager.get_session()

# Sicherstellen, dass output_dir existiert
DEFAULT_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")
output_dir = SESSION_CONFIG.get("output_dir", DEFAULT_OUTPUT_DIR)

if not os.path.exists(output_dir):
    print(f"⚠ Hinweis: Pfad '{output_dir}' existiert nicht. Fallback wird verwendet: {DEFAULT_OUTPUT_DIR}")
    output_dir = DEFAULT_OUTPUT_DIR
    config_manager.update_session("output_dir", DEFAULT_OUTPUT_DIR)

# Ordner anlegen, falls nicht vorhanden
os.makedirs(output_dir, exist_ok=True)

# Qt-App, Composer, View & Controller koppeln
from PySide6.QtWidgets import QApplication
from gui.map_composer import MapComposer
from gui.main_window import MainWindow
from gui.controllers.main_controller import MainController

def main():
    app = QApplication(sys.argv)

    # Composer bekommt die Session-Config
    composer = MapComposer(SESSION_CONFIG, [])

    # MainWindow bekommt ebenfalls die Session-Config
    window = MainWindow(composer)

    controller = MainController(composer, window)
    sys.exit(controller.run())

if __name__ == "__main__":
    main()