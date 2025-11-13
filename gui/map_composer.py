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
        from utils.config import config_manager
        self.session_config = config_manager.get_session()
        self.crs = crs or self.session_config.get("crs", "EPSG:3857")

        # Dimensionen
        karte_cfg = self.session_config.get("karte", {})
        ui_cfg = self.session_config.get("ui", {})
        self.width_px = karte_cfg.get("breite", ui_cfg.get("default_width", 800))
        self.height_px = karte_cfg.get("hoehe", ui_cfg.get("default_height", 600))

        # Scalebar
        self.scalebar_cfg = self.session_config.get("scalebar", {"show": False})

        # Hintergrund
        bg_cfg = self.session_config.get("background", {})
        self.background_cfg = {
            "color": bg_cfg.get("color", "#ffffff"),
            "transparent": bg_cfg.get("transparent", False),
        }

        # Export-Formate – Fallback, falls leer
        self.export_formats = self.session_config.get("export", {}).get("formats") or ["png"]

        # Hide- und Highlight-Configs
        self.hide_cfg = self.session_config.get("hide_cfg", {}) or {"aktiv": False, "bereiche": {}}
        self.hl_cfg = self.session_config.get("highlight_cfg", {}) or {"aktiv": False, "layer": None, "namen": []}

        # Primäre Layer
        self.primary_layers = list(primary_layers)

        # GPKG-Dateien
        self.main_gpkg: Optional[str] = None
        self.sub_gpkgs: List[str] = []

        # Overlay-Datei
        self.overlay_file: Optional[str] = None

    # ------------------------------------------------------------
    # Setter-Methoden
    # ------------------------------------------------------------
    def set_files(self, main: str, subs: List[str]) -> None:
        self.main_gpkg = main
        self.sub_gpkgs = subs or []

    def set_primary_layers(self, layers: List[str]) -> None:
        self.primary_layers = list(layers)

    def set_hide(self, hide_map: Dict[str, List[str]]) -> None:
        aktiv = any(hide_map.values())
        self.hide_cfg = {"aktiv": aktiv, "bereiche": hide_map}
        self.session_config["hide_cfg"] = self.hide_cfg

    def set_highlight(self, layer: str, names: List[str]) -> None:
        aktiv = bool(names)
        self.hl_cfg = {"aktiv": aktiv, "layer": layer, "namen": names}
        self.session_config["highlight_cfg"] = self.hl_cfg

    def set_scalebar(self, cfg: Dict) -> None:
        from utils.config import SCALER
        SCALER.clear()
        SCALER.update(cfg)
        self.scalebar_cfg = dict(cfg)
        self.session_config["scalebar"] = self.scalebar_cfg

    def set_background(self, color: Optional[str] = None, transparent: Optional[bool] = None) -> None:
        if color is not None:
            self.background_cfg["color"] = color
        if transparent is not None:
            self.background_cfg["transparent"] = transparent
        self.session_config["background"] = self.background_cfg

    def set_dimensions(self, width: int, height: int) -> None:
        self.width_px = width
        self.height_px = height

    def set_export_formats(self, formats: List[str]) -> None:
        self.export_formats = formats or ["png"]
        self.session_config.setdefault("export", {})["formats"] = self.export_formats

    def set_overlay(self, overlay_path: Optional[str]) -> None:
        """Setzt oder entfernt den Overlay-Layer."""
        self.overlay_file = overlay_path

    # ------------------------------------------------------------
    # Datenaufbereitung
    # ------------------------------------------------------------
    def _get_combined_gdf(self) -> Optional[GeoDataFrame]:
        import os
        parts = []

        # --- Hauptland ---
        if self.main_gpkg:
            main_gdf = merge_hauptland_layers(
                self.main_gpkg,
                self.primary_layers,
                hide_cfg=self.hide_cfg,
                hl_cfg=self.hl_cfg,
                crs=self.crs
            )
            if main_gdf is not None and not main_gdf.empty:
                main_gdf["__is_main"] = True
                parts.append(main_gdf)

        # --- Nebenländer ---
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
            if sub_gdf is not None and not sub_gdf.empty:
                sub_gdf["__is_main"] = False
                parts.append(sub_gdf)

        # --- Overlay ---
        if self.overlay_file:
            try:
                ext = os.path.splitext(self.overlay_file)[1].lower()
                if ext == ".shp":
                    layers = None  # Shapefile → kein Layername
                else:
                    layers = get_simplest_layer(self.overlay_file) or [self.primary_layers[0]]

                overlay_gdf = merge_hauptland_layers(
                    self.overlay_file,
                    layers,
                    hide_cfg={"aktiv": False, "bereiche": {}},
                    hl_cfg={"aktiv": False, "layer": None, "namen": []},
                    crs=self.crs
                )
                if overlay_gdf is not None and not overlay_gdf.empty:
                    overlay_gdf["__is_overlay"] = True
                    parts.append(overlay_gdf)
            except Exception as e:
                print(f"Fehler beim Laden des Overlays: {e}")

        # --- Wenn nichts da ist, abbrechen ---
        if not parts:
            return None

        # --- Nur nicht-leere Frames zusammenführen ---
        non_empty = [p for p in parts if p is not None and not p.empty]
        if not non_empty:
            return None

        gdf = pd.concat(non_empty, ignore_index=True)

        # --- Sanfte Bereinigung ---

        if "geometry" in gdf.columns:
            gdf = gdf[gdf.geometry.notna() & ~gdf.geometry.is_empty]
            try:
                from shapely.validation import make_valid
                gdf["geometry"] = gdf["geometry"].apply(make_valid)
            except ImportError:
                try:
                    gdf["geometry"] = gdf["geometry"].buffer(0)
                except Exception:
                    pass

        for col in gdf.columns:
            if gdf[col].dtype == "object" or pd.api.types.is_categorical_dtype(gdf[col]):
                gdf[col] = gdf[col].fillna("")

        # --- Typbereinigung ---
        if "__is_main" in gdf.columns:
            try:
                gdf["__is_main"] = gdf["__is_main"].astype(bool)
            except Exception as e:
                print("WARN: __is_main cast failed:", e)
                gdf["__is_main"] = False

        if "highlight" in gdf.columns:
            try:
                gdf["highlight"] = gdf["highlight"].astype(bool)
            except Exception as e:
                print("WARN: highlight cast failed:", e)
                gdf["highlight"] = False

        return gdf

    # ------------------------------------------------------------
    # Figure-Erstellung
    # ------------------------------------------------------------
    def _create_empty_figure(self) -> plt.Figure:
        dpi = self.self.session_config.get("export", {}).get("dpi", 300)
        fig_w = self.width_px / dpi
        fig_h = self.height_px / dpi
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        ax.set_axis_off()

        if not self.background_cfg["transparent"]:
            fig.patch.set_facecolor(self.background_cfg["color"])
            ax.set_facecolor(self.background_cfg["color"])

        return fig

    def compose(self, preview_mode: bool = False, preview_scale: float = 0.5) -> plt.Figure:
        combined = self._get_combined_gdf()
        if combined is None or combined.empty:
            return self._create_empty_figure()

        builder = MapBuilder(
            cfg=self.session_config,
            main_gpkg=None,
            layers=self.primary_layers,
            crs=self.crs,
            hide_cfg=self.hide_cfg,
            hl_cfg=self.hl_cfg,
            gdf=combined
        )

        builder.width_px = self.width_px if not preview_mode else int(self.width_px * preview_scale)
        builder.height_px = self.height_px if not preview_mode else int(self.height_px * preview_scale)
        builder.background = self.background_cfg
        builder.scalebar_cfg = self.scalebar_cfg

        return builder.build_figure(preview_mode=preview_mode, preview_scale=preview_scale)

    # ------------------------------------------------------------
    # Export
    # ------------------------------------------------------------
    def compose_and_save(self, output: BytesIO) -> None:
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
    def render(self, preview_mode: bool = False) -> Image.Image:
        buffer = BytesIO()
        preview_scale = 0.5 if preview_mode else 1.0

        if preview_mode:
            combined = self._get_combined_gdf()
            if combined is not None and not combined.empty:
                combined = combined.copy()
                # Geometrien weiter vereinfachen für die schnelle Vorschau
                try:
                    combined["geometry"] = combined["geometry"].simplify(
                        tolerance=0.01, preserve_topology=True
                    )
                except Exception:
                    pass

                builder = MapBuilder(
                    cfg=self.session_config,
                    main_gpkg=None,
                    layers=self.primary_layers,
                    crs=self.crs,
                    hide_cfg=self.hide_cfg,
                    hl_cfg=self.hl_cfg,
                    gdf=combined
                )
                builder.width_px = int(self.width_px * preview_scale)
                builder.height_px = int(self.height_px * preview_scale)
                builder.background = self.background_cfg
                builder.scalebar_cfg = self.scalebar_cfg

                fig = builder.build_figure(preview_mode=True, preview_scale=preview_scale)
            else:
                fig = self._create_empty_figure()
        else:
            fig = self.compose(preview_mode=False)

        # Für die Vorschau immer PNG in den Speicher schreiben
        MapExporter.save(fig, buffer, ["png"], transparent=self.background_cfg["transparent"])
        buffer.seek(0)
        return Image.open(buffer)