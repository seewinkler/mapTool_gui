# gui/controllers/epsg_controller.py

import logging
from PySide6.QtWidgets import QDialog
from gui.auswahlfenster import AuswahlFenster

class EpsgController:
    def __init__(self, composer, view, config, parent, main_ctrl=None):
        """
        :param composer: MapComposer-Instanz
        :param view: MainWindow-Instanz
        :param config: Config-Dict
        :param parent: Parent-Widget für Dialoge
        :param main_ctrl: Optionaler Verweis auf MainController, um Preview als 'dirty' zu markieren
        """
        self.composer = composer
        self.view     = view
        self.config   = config
        self.parent   = parent
        self.main_ctrl = main_ctrl

    def select_epsg(self):
        epsg_list = self.config.get("epsg_list", [])
        dlg = AuswahlFenster(epsg_list, parent=self.parent)
        if dlg.exec() != QDialog.Accepted or not dlg.selected_entry:
            return

        new_crs = dlg.selected_entry.get("epsg")
        if not new_crs:
            return

        # Composer-CRS setzen
        self.composer.crs = new_crs
        logging.info("Neues CRS gesetzt: %s", new_crs)

        # Kein sofortiger Refresh mehr – nur als 'dirty' markieren
        if self.main_ctrl and hasattr(self.main_ctrl, "mark_preview_dirty"):
            self.main_ctrl.mark_preview_dirty()