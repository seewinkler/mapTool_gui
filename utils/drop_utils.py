# mapTool_gui/utils/drop_utils.py

import os
import shutil
import tempfile
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QAbstractItemView

class DropZoneLogic(QListWidget):
    """
    Basisklasse für eine Drop-Zone, die .gpkg-Dateien akzeptiert,
    intern Path und optional Kopie verwaltet.
    """
    dropChanged = Signal()

    def __init__(
        self,
        title: str,
        allow_multiple: bool = True,
        copy_to_temp: bool = False,
        parent=None,
    ):
        super().__init__(parent)
        self.title = title
        self.allow_multiple = allow_multiple
        self.copy_to_temp = copy_to_temp

        if self.copy_to_temp:
            self._temp_dir = tempfile.mkdtemp(prefix="maptool_")

        self._setup_ui()

    def _setup_ui(self):
        """Styling & Drag-&-Drop aktivieren."""
        self.setAcceptDrops(True)
        # Nur als Drop-Area nutzen (kein Drag aus dieser Liste)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.setStyleSheet(
            """
            QListWidget {
                border: 2px dashed #888;
                padding: 12px;
                background-color: #fafafa;
            }
            """
        )

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragEnterEvent(event)

    def dragMoveEvent(self, event):
        # Muss separat akzeptiert werden, sonst gilt nur dragEnter
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            super().dragMoveEvent(event)

    def dragLeaveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        paths = [url.toLocalFile() for url in event.mimeData().urls()]
        gpkg = [p for p in paths if p.lower().endswith(".gpkg")]
        if not gpkg:
            return

        if not self.allow_multiple and len(gpkg) > 1:
            print(f"⚠️ In '{self.title}' sind mehrere Dateien nicht erlaubt.")
            return

        added = False
        for src in gpkg:
            name = os.path.basename(src)

            # Original belassen oder in temp kopieren
            if self.copy_to_temp:
                dst = self._unique_temp_path(name)
                shutil.copy2(src, dst)
                store_path = dst
            else:
                store_path = src

            if not self.findItems(name, Qt.MatchExactly):
                self.addItem(name)
                # Kompletter Pfad im UserRole speichern
                self.item(self.count() - 1).setData(Qt.UserRole, store_path)
                added = True

        if added:
            self.dropChanged.emit()

    def _unique_temp_path(self, filename: str) -> str:
        """Erzeugt einen einzigartigen Pfad im Temp-Ordner."""
        base, ext = os.path.splitext(filename)
        dst = os.path.join(self._temp_dir, filename)
        idx = 1
        while os.path.exists(dst):
            dst = os.path.join(self._temp_dir, f"{base}_{idx}{ext}")
            idx += 1
        return dst

    def get_paths(self) -> list[str]:
        """Alle gespeicherten (originalen oder kopierten) Pfade."""
        return [
            self.item(i).data(Qt.UserRole)
            for i in range(self.count())
        ]