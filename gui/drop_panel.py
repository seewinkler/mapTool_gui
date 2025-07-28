# gui/drop_panel.py

import os
from PySide6.QtCore    import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel
)

class DropZone(QWidget):
    """
    Einfacher Drop‐Bereich für Dateien. Signalisiert über dropChanged,
    wenn neue Pfade hereingezogen wurden.
    """
    dropChanged = Signal()

    def __init__(self, title: str, copy_to_temp: bool = False, parent=None):
        super().__init__(parent)
        self.copy_to_temp = copy_to_temp
        self.paths = []

        # UI
        self.label = QLabel(title, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("border: 2px dashed gray;")
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)

        self.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        urls = event.mimeData().urls()
        self.paths = [url.toLocalFile() for url in urls]

        # Anzeige aktualisieren
        names = [os.path.basename(p) for p in self.paths]
        self.label.setText("\n".join(names) if names else "Keine Dateien")
        self.dropChanged.emit()

class DropPanel(QWidget):
    """
    Container mit zwei DropZones: Haupt- und Sub-Dateien.
    """
    def __init__(self, copy_to_temp: bool = False, parent=None):
        super().__init__(parent)

        self.drop_main = DropZone("Hauptdatei hierherziehen", copy_to_temp)
        self.drop_sub  = DropZone("Subdateien hierherziehen", copy_to_temp)

        layout = QHBoxLayout(self)
        layout.addWidget(self.drop_main, 1)
        layout.addWidget(self.drop_sub, 1)

    def get_main_paths(self) -> list[str]:
        return self.drop_main.paths

    def get_sub_paths(self) -> list[str]:
        return self.drop_sub.paths