# gui/dropzones.py

from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from utils.drop_utils import DropZoneLogic

class DropZone(DropZoneLogic):
    """Hier könntest Du GUI-Spezifika ergänzen, momentan erbt alles aus DropZoneLogic."""
    pass

class DropPanel(QWidget):
    def __init__(self, copy_to_temp: bool = False):
        super().__init__()
        layout = QVBoxLayout(self)

        self.label_main = QLabel("📁 Hauptland (.gpkg)")
        self.label_main.setAlignment(Qt.AlignCenter)
        self.drop_main = DropZone(
            "Hauptland", allow_multiple=False, copy_to_temp=copy_to_temp
        )

        self.label_sub = QLabel("📁 Nebenländer (.gpkg)")
        self.label_sub.setAlignment(Qt.AlignCenter)
        self.drop_sub = DropZone(
            "Nebenländer", allow_multiple=True, copy_to_temp=copy_to_temp
        )

        layout.addWidget(self.label_main)
        layout.addWidget(self.drop_main)
        layout.addSpacing(15)
        layout.addWidget(self.label_sub)
        layout.addWidget(self.drop_sub)

    def get_main_paths(self) -> list[str]:
        """Alias für drop_main.get_paths() – liefert Liste der Haupt-GPKG-Dateien."""
        return self.drop_main.get_paths()

    def get_sub_paths(self) -> list[str]:
        """Alias für drop_sub.get_paths() – liefert Liste der Neben-GPKG-Dateien."""
        return self.drop_sub.get_paths()