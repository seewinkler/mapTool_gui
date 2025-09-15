# gui/controllers/layer_controller.py

import logging
from typing import List, Dict

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QListWidgetItem

from data_processing.layers import merge_hauptland_layers


class LayerController:
    """
    Steuert die Auswahl der Haupt-Layer sowie
    das Ein-/Ausblenden und Hervorheben von Regionen.
    """

    def __init__(self, composer, view, main_ctrl=None):
        """
        :param composer: MapComposer-Instanz
        :param view: MainWindow-Instanz
        :param main_ctrl: Optionaler Verweis auf MainController
        """
        self.composer  = composer
        self.view      = view
        self.main_ctrl = main_ctrl
        self._gdf_main = None
        self._name_col = None

    def handle_primary_selection(self, item: QListWidgetItem) -> None:
        """Wird aufgerufen, wenn in lst_layers ein Layer angehakt oder abgehakt wird."""
        # 1) Alle aktuell angehakten Haupt-Layer
        sel = [
            self.view.lst_layers.item(i).text()
            for i in range(self.view.lst_layers.count())
            if self.view.lst_layers.item(i).checkState() == Qt.Checked
        ]

        # Composer updaten (auch bei leerer Selektion)
        self.composer.set_primary_layers(sel)

        # Wenn nichts angehakt, leere hide/high-Listen
        if not sel:
            self.view.lst_hide.clear()
            self.view.lst_high.clear()
            # Nur dirty markieren
            if self.main_ctrl:
                self.main_ctrl.mark_preview_dirty()
            return

        # 2) GDF der gewählten Haupt-Layer laden
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

        # nur die '__is_main' Features behalten
        if "__is_main" in gdf.columns:
            self._gdf_main = gdf[gdf["__is_main"]]
        else:
            self._gdf_main = gdf.copy()

        # 3) Dynamisch ermitteln, welche 'NAME_x'-Spalte genutzt wird
        layer = sel[0]
        lvl   = layer.split("_")[-1]
        col   = f"NAME_{lvl}"
        if col not in self._gdf_main.columns:
            # Fallback: erste Spalte, die mit 'NAME_' beginnt
            candidates = [c for c in self._gdf_main.columns if c.startswith("NAME_")]
            col = candidates[0] if candidates else None
        self._name_col = col

        # 4) Einträge extrahieren und in Listen packen
        if self._name_col:
            raw = (
                self._gdf_main[self._name_col]
                .dropna()
                .astype(str)
                .unique()
            )
            unique_names = sorted(raw)
        else:
            logging.warning("Kein NAME_-Feld gefunden für Layer '%s'", layer)
            unique_names = []

        # 5) Hide- und Highlight-Listen befüllen
        self.view.lst_hide.clear()
        self.view.lst_high.clear()
        for name in unique_names:
            # Ausblenden
            h_item = QListWidgetItem(name)
            h_item.setFlags(h_item.flags() | Qt.ItemIsUserCheckable)
            h_item.setCheckState(Qt.Unchecked)
            self.view.lst_hide.addItem(h_item)

            # Hervorheben
            x_item = QListWidgetItem(name)
            x_item.setFlags(x_item.flags() | Qt.ItemIsUserCheckable)
            x_item.setCheckState(Qt.Unchecked)
            self.view.lst_high.addItem(x_item)

        # 6) Nur dirty markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()

    def handle_hide_changed(self, item: QListWidgetItem) -> None:
        """Wird aufgerufen, wenn in lst_hide eine Region ange- oder abgehakt wird."""
        # 1) Ausgeblendete Regionen sammeln
        hide_list = [
            self.view.lst_hide.item(i).text()
            for i in range(self.view.lst_hide.count())
            if self.view.lst_hide.item(i).checkState() == Qt.Checked
        ]

        # 2) Composer informieren
        layer = (
            self.composer.primary_layers[0]
            if self.composer.primary_layers else ""
        )
        self.composer.set_hide({layer: hide_list} if layer else {})

        # 3) Highlight-Liste nur befüllen, wenn gültige Spalte vorhanden
        self.view.lst_high.clear()
        if (
            self._gdf_main is not None
            and self._name_col
            and self._name_col in self._gdf_main.columns
        ):
            raw = (
                self._gdf_main[self._name_col]
                .dropna()
                .astype(str)
                .unique()
            )
            remaining = [n for n in raw if n not in hide_list]
            for name in sorted(remaining):
                item = QListWidgetItem(name)
                item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
                item.setCheckState(Qt.Unchecked)
                self.view.lst_high.addItem(item)

        # 4) Nur dirty markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()


    def handle_highlight_changed(self, item: QListWidgetItem) -> None:
        """Wird aufgerufen, wenn in lst_high eine Region ange- oder abgehakt wird."""
        hl = [
            self.view.lst_high.item(i).text()
            for i in range(self.view.lst_high.count())
            if self.view.lst_high.item(i).checkState() == Qt.Checked
        ]
        layer = (
            self.composer.primary_layers[0]
            if self.composer.primary_layers else ""
        )

        # Nur setzen, wenn gültige Spalte vorhanden
        if (
            self._gdf_main is not None
            and self._name_col
            and self._name_col in self._gdf_main.columns
        ):
            self.composer.set_highlight(layer, hl)
        else:
            # Overlay oder kein gültiger Name-Col → Highlight deaktivieren
            self.composer.set_highlight("", [])

        # Nur dirty markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()


            # Nur dirty markieren
            if self.main_ctrl:
                self.main_ctrl.mark_preview_dirty()