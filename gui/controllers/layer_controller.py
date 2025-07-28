# gui/controllers/layer_controller.py

import logging
from typing import List, Dict
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem
from data_processing.layers import merge_hauptland_layers

class LayerController:
    def __init__(self, composer, view):
        self.composer   = composer
        self.view       = view
        self._gdf_main  = None

    def handle_primary_selection(self):
        # 1) Auswahl ermitteln
        sel = [
            self.view.lst_layers.item(i).text()
            for i in range(self.view.lst_layers.count())
            if self.view.lst_layers.item(i).checkState() == Qt.Checked
        ]
        if not sel:
            # keine Auswahl → alle aktivieren
            sel = [
                self.view.lst_layers.item(i).text()
                for i in range(self.view.lst_layers.count())
            ]

        # 2) Composer updaten
        self.composer.set_primary_layers(sel)

        # 3) Haupt-GDF neu laden
        try:
            gdf = merge_hauptland_layers(
                self.composer.main_gpkg,
                sel,
                hide_cfg={"aktiv": False, "bereiche": {}},
                hl_cfg={"aktiv": False, "layer": "", "namen": []},
                crs=self.composer.crs,
            )
        except Exception as e:
            logging.error("Fehler beim Laden des Haupt-Layers: %s", e)
            return

        # nur __is_main-Features merken
        if "__is_main" in gdf.columns:
            self._gdf_main = gdf[gdf["__is_main"]]
        else:
            self._gdf_main = gdf.copy()

        # 4) Hide/Highlight-Listen befüllen
        unique_names = sorted(self._gdf_main["NAME_1"].unique())
        self.view.lst_hide.clear()
        self.view.lst_high.clear()
        for name in unique_names:
            # Hide
            item_h = QListWidgetItem(name)
            item_h.setFlags(item_h.flags() | Qt.ItemIsUserCheckable)
            item_h.setCheckState(Qt.Unchecked)
            self.view.lst_hide.addItem(item_h)
            # Highlight
            item_x = QListWidgetItem(name)
            item_x.setFlags(item_x.flags() | Qt.ItemIsUserCheckable)
            item_x.setCheckState(Qt.Unchecked)
            self.view.lst_high.addItem(item_x)

        # 5) Refresh
        self.view.map_canvas.refresh()

    def handle_hide_changed(self):
        # ausgeblendete Regionen
        hide_list = [
            self.view.lst_hide.item(i).text()
            for i in range(self.view.lst_hide.count())
            if self.view.lst_hide.item(i).checkState() == Qt.Checked
        ]
        layer = self.composer.primary_layers[0] if self.composer.primary_layers else ""
        hide_map: Dict[str, List[str]] = {layer: hide_list}
        self.composer.set_hide(hide_map)

        # Highlight-Liste neu generieren
        self.view.lst_high.clear()
        remaining = [
            name for name in self._gdf_main["NAME_1"].unique()
            if name not in hide_list
        ]
        for name in sorted(remaining):
            item = QListWidgetItem(name)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.view.lst_high.addItem(item)

        self.view.map_canvas.refresh()

    def handle_highlight_changed(self):
        hl = [
            self.view.lst_high.item(i).text()
            for i in range(self.view.lst_high.count())
            if self.view.lst_high.item(i).checkState() == Qt.Checked
        ]
        layer = self.composer.primary_layers[0] if self.composer.primary_layers else ""
        self.composer.set_highlight(layer, hl)
        self.view.map_canvas.refresh()