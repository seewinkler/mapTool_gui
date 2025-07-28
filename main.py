import sys
import os

print("▶ Starte GUI-EntryPoint aus", __file__)

# Projekt-Root ins sys.path (damit gui/ und utils/ als Packages erkannt werden)
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

# Logging & Config
from utils.logging_config import setup_logging
from utils.config         import CONFIG

setup_logging(CONFIG["logging"])

# Qt-App, Composer, View & Controller koppeln
from PySide6.QtWidgets                import QApplication
from gui.map_composer                 import MapComposer
from gui.main_window                  import MainWindow
from gui.controllers.main_controller  import MainController

def main():
    app      = QApplication(sys.argv)
    composer = MapComposer(CONFIG, [])
    window   = MainWindow(composer, CONFIG)
    controller = MainController(composer, window)
    sys.exit(controller.run())

if __name__ == "__main__":
    main()