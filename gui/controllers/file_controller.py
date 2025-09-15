# gui/controllers/file_controller.py

import logging
from fiona import listlayers
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

class FileController:
    def __init__(self, composer, view):
        self.composer = composer
        self.view = view

    def handle_files_changed(self):
        mains = self.view.drop_panel.get_main_paths()
        subs  = self.view.drop_panel.get_sub_paths()
        logging.debug("Main dropped: %s", mains)
        logging.debug("Subs  dropped: %s", subs)
        if not mains:
            return

        # Composer mit Dateien versorgen
        self.composer.set_files(mains[0], subs)

        # Layer auslesen
        try:
            layer_names = listlayers(mains[0])
        except Exception as e:
            logging.error("Fehler beim Auslesen der Layer: %s", e)
            return

        # UI-Layer-Liste befüllen
        self.view.lst_layers.clear()
        for name in layer_names:
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.view.lst_layers.addItem(item)

        # Hide- und Highlight-Listen zurücksetzen
        self.view.lst_hide.clear()
        self.view.lst_high.clear()

        # Erste Anzeige nach Dateiladen in voller Qualität
        self.view.map_canvas.refresh(preview=False)