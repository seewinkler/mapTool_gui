# gui/controllers/layer_controller.py

import logging
from typing import List, Dict

import geopandas as gpd
import pandas as pd

from PySide6.QtCore    import Qt
from PySide6.QtWidgets import QListWidgetItem

from utils.simplify_preview import simplify_for_preview
from data_processing.cache   import cached_merge


class LayerController:
    """
    Steuert die Auswahl der Haupt-Layer sowie
    das Ein-/Ausblenden und Hervorheben von Regionen.
    """

    def __init__(self, composer, view):
        self.composer  = composer
        self.view      = view
        self._gdf_main = None
        self._name_col = None

    def handle_primary_selection(self, item: QListWidgetItem) -> None:
        """
        Wird aufgerufen, wenn in lst_layers ein Layer
        angehakt oder abgehakt wird.
        """
        # 1) Aktuelle Layer-Selektion
        sel = [
            self.view.lst_layers.item(i).text()
            for i in range(self.view.lst_layers.count())
            if self.view.lst_layers.item(i).checkState() == Qt.Checked
        ]

        # Composer updaten
        self.composer.set_primary_layers(sel)

        # Falls keine Auswahl → Vorschau leeren
        if not sel:
            self.view.lst_hide.clear()
            self.view.lst_high.clear()
            self.view.map_canvas.refresh()
            return

        # 2) Layer-Merge (mit Caching)
        try:
            key = tuple(sorted(sel))
            gdf = cached_merge(
                self.composer.main_gpkg,
                key,
                self.composer.crs
            )
            print("Merge für:", key)
            print("Cachegröße:", cached_merge.cache_info())
        except Exception as e:
            logging.error("Fehler beim Laden des Haupt-Layers: %s", e)
            return

        # 3) Vorschau vereinfachen (Fallback, falls simplify_for_preview fehlschlägt)
        try:
            gdf = simplify_for_preview(gdf, {}, len(gdf), list(key))
        except Exception:
            logging.warning(
                "Vorschau-Vereinfachung fehlgeschlagen, rohes GeoDataFrame wird verwendet"
            )

        # 4) Series → DataFrame konvertieren, falls nötig
        if isinstance(gdf, (pd.Series, gpd.GeoSeries)):
            if isinstance(gdf, gpd.GeoSeries):
                gdf = gpd.GeoDataFrame({'geometry': gdf})
            else:
                gdf = gpd.GeoDataFrame(gdf.to_frame())

        # 5) Hauptregionen isolieren
        if "__is_main" in gdf.columns:
            self._gdf_main = gdf[gdf["__is_main"]]
        else:
            self._gdf_main = gdf.copy()

        # 6) NAME-Spalte bestimmen
        layer = sel[0]
        lvl   = layer.split("_")[-1]
        col   = f"NAME_{lvl}"
        if col not in self._gdf_main.columns:
            candidates = [c for c in self._gdf_main.columns if c.startswith("NAME_")]
            col = candidates[0] if candidates else None
        self._name_col = col

        # 7) Einträge extrahieren
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

        # 8) Listen füllen
        self.view.lst_hide.clear()
        self.view.lst_high.clear()
        for name in unique_names:
            h_item = QListWidgetItem(name)
            h_item.setFlags(h_item.flags() | Qt.ItemIsUserCheckable)
            h_item.setCheckState(Qt.Unchecked)
            self.view.lst_hide.addItem(h_item)

            x_item = QListWidgetItem(name)
            x_item.setFlags(x_item.flags() | Qt.ItemIsUserCheckable)
            x_item.setCheckState(Qt.Unchecked)
            self.view.lst_high.addItem(x_item)

        # 9) Karte aktualisieren
        self.view.map_canvas.refresh()

    def handle_hide_changed(self, item: QListWidgetItem) -> None:
        """
        Wenn eine Region in lst_hide (de)selektiert wurde.
        """
        # 1) Hide-Liste ermitteln
        hide_list = [
            self.view.lst_hide.item(i).text()
            for i in range(self.view.lst_hide.count())
            if self.view.lst_hide.item(i).checkState() == Qt.Checked
        ]

        # 2) Composer updaten
        layer = (
            self.composer.primary_layers[0]
            if self.composer.primary_layers else ""
        )
        self.composer.set_hide({layer: hide_list})

        # 3) Highlight-Liste neu befüllen
        self.view.lst_high.clear()
        if self._name_col:
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

        # 4) Karte aktualisieren
        self.view.map_canvas.refresh()

    def handle_highlight_changed(self, item: QListWidgetItem) -> None:
        """
        Wenn eine Region in lst_high (de)selektiert wurde.
        """
        hl = [
            self.view.lst_high.item(i).text()
            for i in range(self.view.lst_high.count())
            if self.view.lst_high.item(i).checkState() == Qt.Checked
        ]
        layer = (
            self.composer.primary_layers[0]
            if self.composer.primary_layers else ""
        )
        self.composer.set_highlight(layer, hl)
        self.view.map_canvas.refresh()