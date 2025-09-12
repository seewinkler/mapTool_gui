# gui/map_composer.py

from io import BytesIO
from typing import List, Optional, Dict
from pathlib import Path

from PIL import Image
import matplotlib.pyplot as plt
import pandas as pd
from geopandas import GeoDataFrame

from data_processing.layers import merge_hauptland_layers
from gui.map_builder import MapBuilder
from gui.map_exporter import MapExporter
from utils.layer_selector import get_simplest_layer


class MapComposer:
    """
    Zentrale Klasse für den Kartenaufbau.
    Verwaltet Datenquellen, Layer-Konfiguration, Hintergrund, Dimensionen
    und steuert den Build- und Exportprozess.
    """

    def __init__(
        self,
        config: Dict,
        primary_layers: List[str],
        crs: Optional[str] = None
    ) -> None:
        self.config = config
        self.crs = crs or config.get("crs", "EPSG:3857")

        # Dimensionen
        karte_cfg = config.get("karte", {})
        ui_cfg = config.get("ui", {})
        self.width_px = karte_cfg.get("breite", ui_cfg.get("default_width", 800))
        self.height_px = karte_cfg.get("hoehe", ui_cfg.get("default_height", 600))

        # Scalebar
        self.scalebar_cfg = config.get("scalebar", {"show": False})

        # Hintergrund
        bg_cfg = config.get("background", {})
        self.background_cfg = {
            "color": bg_cfg.get("color", "#ffffff"),
            "transparent": bg_cfg.get("transparent", False),
        }

        # Export-Formate
        self.export_formats = config.get("export", {}).get("formats", ["png"])

        # Hide- und Highlight-Configs
        self.hide_cfg = config.get("hide_cfg", {}) or {"aktiv": False, "bereiche": {}}
        self.hl_cfg = config.get("highlight_cfg", {}) or {"aktiv": False, "layer": None, "namen": []}

        # Primäre Layer
        self.primary_layers = list(primary_layers)

        # GPKG-Dateien
        self.main_gpkg: Optional[str] = None
        self.sub_gpkgs: List[str] = []

    # ------------------------------------------------------------
    # Setter-Methoden
    # ------------------------------------------------------------
    def set_files(self, main: str, subs: List[str]) -> None:
        """Haupt- und Neben-Geopackages setzen."""
        self.main_gpkg = main
        self.sub_gpkgs = subs or []

    def set_primary_layers(self, layers: List[str]) -> None:
        """Reihenfolge oder Auswahl der primären Layer anpassen."""
        self.primary_layers = list(layers)

    def set_hide(self, hide_map: Dict[str, List[str]]) -> None:
        """Ausblendungen konfigurieren."""
        aktiv = any(hide_map.values())
        self.hide_cfg = {"aktiv": aktiv, "bereiche": hide_map}
        self.config["hide_cfg"] = self.hide_cfg

    def set_highlight(self, layer: str, names: List[str]) -> None:
        """Hervorzuhebenden Layer und Features definieren."""
        aktiv = bool(names)
        self.hl_cfg = {"aktiv": aktiv, "layer": layer, "namen": names}
        self.config["highlight_cfg"] = self.hl_cfg

    def set_scalebar(self, cfg: Dict) -> None:
        """Globale Scalebar-Settings aktualisieren und lokal speichern."""
        from utils.config import SCALER
        SCALER.clear()
        SCALER.update(cfg)
        self.scalebar_cfg = dict(cfg)

    def set_background(self, color: Optional[str] = None, transparent: Optional[bool] = None) -> None:
        """Hintergrundfarbe und -transparenz setzen."""
        if color is not None:
            self.background_cfg["color"] = color
        if transparent is not None:
            self.background_cfg["transparent"] = transparent

    def set_dimensions(self, width: int, height: int) -> None:
        """Breite und Höhe (in Pixeln) für Figure-/Canvas-Größe festlegen."""
        self.width_px = width
        self.height_px = height

    def set_export_formats(self, formats: List[str]) -> None:
        """Export-Formate (z.B. ['png','svg']) festlegen."""
        self.export_formats = list(formats)

    # ------------------------------------------------------------
    # Datenaufbereitung
    # ------------------------------------------------------------
    def _get_combined_gdf(self) -> Optional[GeoDataFrame]:
        """
        Lädt Haupt- und Neben-GPKGs, merged deren GeoDataFrames
        und liefert ein kombiniertes GeoDataFrame zurück.
        """
        if not self.main_gpkg:
            return None

        parts = []

        # Haupt-GPKG laden
        main_gdf = merge_hauptland_layers(
            self.main_gpkg,
            self.primary_layers,
            hide_cfg=self.hide_cfg,
            hl_cfg=self.hl_cfg,
            crs=self.crs
        )
        main_gdf["__is_main"] = True
        parts.append(main_gdf)

        # Neben-GPKGs laden
        for sub in self.sub_gpkgs:
            if not sub:
                continue
            layers = get_simplest_layer(sub) or [self.primary_layers[0]]
            sub_gdf = merge_hauptland_layers(
                sub,
                layers,
                hide_cfg=self.hide_cfg,
                hl_cfg=self.hl_cfg,
                crs=self.crs
            )
            sub_gdf["__is_main"] = False
            parts.append(sub_gdf)

        return pd.concat(parts, ignore_index=True)

    # ------------------------------------------------------------
    # Figure-Erstellung
    # ------------------------------------------------------------
    def _create_empty_figure(self) -> plt.Figure:
        """Leere Figure mit Hintergrund-Logik (ohne Geometrien)."""
        dpi = self.config.get("export", {}).get("dpi", 300)
        fig_w = self.width_px / dpi
        fig_h = self.height_px / dpi
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        ax.set_axis_off()

        if not self.background_cfg["transparent"]:
            fig.patch.set_facecolor(self.background_cfg["color"])
            ax.set_facecolor(self.background_cfg["color"])

        return fig

    def compose(self) -> plt.Figure:
        """
        Baut die aktuelle Karte als Matplotlib-Figure auf.
        Gibt bei fehlender main_gpkg oder keinem GDF eine leere Fläche zurück.
        """
        if not self.main_gpkg:
            return self._create_empty_figure()

        combined = self._get_combined_gdf()
        if combined is None or combined.empty:
            return self._create_empty_figure()

        builder = MapBuilder(
            cfg=self.config,
            main_gpkg=None,
            layers=self.primary_layers,
            crs=self.crs,
            hide_cfg=self.hide_cfg,
            hl_cfg=self.hl_cfg,
            gdf=combined
        )

        # UI-Overrides synchronisieren
        builder.width_px = self.width_px
        builder.height_px = self.height_px
        builder.background = self.background_cfg
        builder.scalebar_cfg = self.scalebar_cfg

        return builder.build_figure()

    # ------------------------------------------------------------
    # Export
    # ------------------------------------------------------------
    def compose_and_save(self, output: BytesIO) -> None:
        """Schreibt die aktuell erzeugte Figure in den BytesIO-Stream."""
        fig = self.compose()
        MapExporter.save(
            fig,
            output,
            self.export_formats,
            transparent=self.background_cfg["transparent"],
        )

    def compose_and_save_dialog(
        self,
        parent=None,
        initial_dir: str = "output"
    ) -> Optional[Path]:
        """Öffnet einen Save-Dialog und speichert die Figure."""
        fig = self.compose()
        return MapExporter.save_with_dialog(
            fig,
            self.export_formats,
            transparent=self.background_cfg["transparent"],
            parent=parent,
            initial_dir=initial_dir
        )

    # ------------------------------------------------------------
    # Vorschau
    # ------------------------------------------------------------
    def render(self) -> Image.Image:
        """Erstellt eine schnelle Vorschau als PIL.Image für die GUI-Anzeige."""
        buffer = BytesIO()
        self.compose_and_save(buffer)
        buffer.seek(0)
        return Image.open(buffer)