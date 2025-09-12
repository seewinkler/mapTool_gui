# gui/controllers/epsg_controller.py

import logging
from PySide6.QtWidgets import QDialog
from gui.auswahlfenster import AuswahlFenster

class EpsgController:
    def __init__(self, composer, view, config, parent):
        self.composer = composer
        self.view     = view
        self.config   = config
        self.parent   = parent

    def select_epsg(self):
        epsg_list = self.config.get("epsg_list", [])
        dlg = AuswahlFenster(epsg_list, parent=self.parent)
        if dlg.exec() != QDialog.Accepted or not dlg.selected_entry:
            return
        new_crs = dlg.selected_entry.get("epsg")
        if not new_crs:
            return

        self.composer.crs = new_crs
        logging.info("Neues CRS gesetzt: %s", new_crs)

        # Vorschau-Refresh statt voller Qualität
        self.view.map_canvas.refresh(preview=True)