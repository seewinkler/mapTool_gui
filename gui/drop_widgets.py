# gui/drop_widgets.py
import os
from typing import List
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel


class DropZone(QWidget):
    dropChanged = Signal()

    def __init__(self, title: str, allow_multiple: bool = True, copy_to_temp: bool = False, parent=None):
        super().__init__(parent)
        self.title = title
        self.allow_multiple = allow_multiple
        self.copy_to_temp = copy_to_temp
        self.paths: List[str] = []

        # UI
        self.label = QLabel(title, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed gray; padding: 10px;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        files = [url.toLocalFile() for url in urls]
        if not self.allow_multiple:
            files = files[:1]
        self.paths = files

        # Anzeige aktualisieren
        names = [os.path.basename(p) for p in self.paths]
        self.label.setText("\n".join(names) if names else "Keine Dateien")
        self.dropChanged.emit()

    def get_paths(self) -> List[str]:
        return self.paths

    def clear(self):
        """Leert die Drop-Zone vollständig."""
        self.paths.clear()
        self.label.setText("Keine Dateien")


class DropPanel(QWidget):
    def __init__(
        self,
        copy_to_temp: bool = False,
        layout_orientation: str = "vertical",  # "vertical" oder "horizontal"
        show_labels: bool = True,
        parent=None
    ):
        super().__init__(parent)

        # Layout wählen
        if layout_orientation == "vertical":
            layout = QVBoxLayout(self)
        else:
            layout = QHBoxLayout(self)

        # Hauptland
        if show_labels:
            label_main = QLabel("📁 Hauptland (.gpkg)")
            label_main.setAlignment(Qt.AlignCenter)
            layout.addWidget(label_main)

        self.drop_main = DropZone("Hauptland", allow_multiple=False, copy_to_temp=copy_to_temp)
        layout.addWidget(self.drop_main)

        # Nebenländer
        if show_labels:
            label_sub = QLabel("📁 Nebenländer (.gpkg)")
            label_sub.setAlignment(Qt.AlignCenter)
            layout.addWidget(label_sub)

        self.drop_sub = DropZone("Nebenländer", allow_multiple=True, copy_to_temp=copy_to_temp)
        layout.addWidget(self.drop_sub)

        # Overlay
        if show_labels:
            label_overlay = QLabel("📁 Overlay (Shapefile/GeoPackage)")
            label_overlay.setAlignment(Qt.AlignCenter)
            layout.addWidget(label_overlay)

        self.drop_overlay = DropZone("Overlay", allow_multiple=False, copy_to_temp=copy_to_temp)
        layout.addWidget(self.drop_overlay)

    def get_main_paths(self) -> List[str]:
        return self.drop_main.get_paths()

    def get_sub_paths(self) -> List[str]:
        return self.drop_sub.get_paths()

    def get_overlay_paths(self) -> List[str]:
        return self.drop_overlay.get_paths()

    def clear(self):
        """Leert alle Drop-Zonen."""
        self.drop_main.clear()
        self.drop_sub.clear()
        self.drop_overlay.clear()