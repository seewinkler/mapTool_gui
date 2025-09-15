# mapTool_gui/utils/drop_utils.py

import os
import shutil
import tempfile
from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget, QAbstractItemView, QWidget, QVBoxLayout, QLabel


class DropZoneLogic(QListWidget):
    """
    Basisklasse für eine Drop-Zone, die .gpkg-Dateien akzeptiert,
    intern Pfade und optional Kopien verwaltet.
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

        self._temp_dir = None
        if self.copy_to_temp:
            self._temp_dir = tempfile.mkdtemp(prefix="maptool_")

        self._setup_ui()
        # Platzhaltertext initial setzen
        self.addItem(f"Datei hier ablegen ({self.title})")

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

            # Platzhalter entfernen, falls vorhanden
            if self.count() == 1 and not self.item(0).data(Qt.UserRole):
                super().clear()

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
            if self.item(i).data(Qt.UserRole)
        ]

    def clear(self):
        """
        Leert die Drop-Zone vollständig:
        - Entfernt alle Einträge aus der Anzeige
        - Setzt Platzhaltertext zurück
        - Löscht ggf. temporäre Dateien
        - Erstellt bei Bedarf einen neuen Temp-Ordner
        """
        super().clear()

        # Platzhaltertext wieder anzeigen
        self.addItem(f"Datei hier ablegen ({self.title})")

        # Temporäre Dateien löschen, falls vorhanden
        if self.copy_to_temp and self._temp_dir and os.path.exists(self._temp_dir):
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass
            # Neuen Temp-Ordner anlegen
            self._temp_dir = tempfile.mkdtemp(prefix="maptool_")


class DropPanel(QWidget):
    """
    Container für zwei Drop-Zonen: Main und Sub.
    """
    def __init__(self, copy_to_temp=False, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(6)

        # Main Drop-Zone
        self.drop_main = DropZoneLogic("Main", allow_multiple=False, copy_to_temp=copy_to_temp)
        layout.addWidget(QLabel("Hauptdatei (.gpkg):"))
        layout.addWidget(self.drop_main)

        # Sub Drop-Zone
        self.drop_sub = DropZoneLogic("Sub", allow_multiple=True, copy_to_temp=copy_to_temp)
        layout.addWidget(QLabel("Zusatzdateien (.gpkg):"))
        layout.addWidget(self.drop_sub)

    def get_main_paths(self) -> list[str]:
        return self.drop_main.get_paths()

    def get_sub_paths(self) -> list[str]:
        return self.drop_sub.get_paths()

    def clear(self):
        """Leert beide Drop-Zonen."""
        self.drop_main.clear()
        self.drop_sub.clear()