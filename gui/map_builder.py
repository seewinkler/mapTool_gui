import matplotlib.pyplot as plt
from typing import Optional, List, Dict, Any
from data_processing.layers import merge_hauptland_layers
from data_processing.crs import compute_bbox
from utils.scalebar import add_scalebar
import pandas as pd

def pixel_to_pt(px: float, dpi: float) -> float:
    """Konvertiert Pixel in Points (für Matplotlib-Linienbreiten)."""
    return px * 72.0 / dpi

class MapBuilder:
    """
    Baut eine Matplotlib-Figure aus Geodaten (Haupt- und Nebenländer),
    inklusive Hintergrund, Layerfarben, Hervorhebungen und Maßstabsleiste.
    """

    def __init__(
        self,
        cfg: Dict[str, Any],
        main_gpkg: Optional[str] = None,
        layers: Optional[List[str]] = None,
        crs: Optional[str] = None,
        hide_cfg: Optional[Dict[str, Any]] = None,
        hl_cfg: Optional[Dict[str, Any]] = None,
        gdf=None,
    ) -> None:
        self.cfg = cfg
        self.main_gpkg = main_gpkg
        self.layers = layers or []
        self.crs = crs
        self._gdf = gdf

        # Karten-Abmessungen
        karte = cfg.get("karte", {})
        self.width_px = karte.get("breite", 800)
        self.height_px = karte.get("hoehe", 600)

        # Layer- und Darstellungsoptionen
        self.hide_cfg = hide_cfg or cfg.get("ausblenden", {})
        self.hl_cfg = hl_cfg or cfg.get("hervorhebung", {})
        self.background = cfg.get("background", {})
        self.colors = cfg.get("farben", {})
        self.lines_cfg = cfg.get("linien", {})

        # Scalebar-Defaults sichern
        self._scalebar_defaults = cfg.get("scalebar", {}).copy()

    # ------------------------------------------------------------
    # Hauptmethode
    # ------------------------------------------------------------
    def build_figure(self, preview_mode: bool = False, preview_scale: float = 0.5) -> plt.Figure:
        """Erzeugt die Karte als Matplotlib-Figure."""
        gdf = self._get_geodataframe()
        if gdf is None or gdf.empty:
            return self._empty_figure()

        # --- Typbereinigung ---
        for col in ["__is_main", "__is_overlay", "highlight"]:
            if col in gdf.columns and gdf[col].dtype != bool:
                try:
                    gdf[col] = gdf[col].astype(bool)
                except Exception:
                    gdf[col] = False

        # --- Exklusive Aufteilung (fehlertolerant) ---
        if "__is_main" in gdf.columns:
            mask_main = gdf["__is_main"] == True
        else:
            mask_main = pd.Series(False, index=gdf.index)

        if "__is_overlay" in gdf.columns:
            mask_overlay = gdf["__is_overlay"] == True
        else:
            mask_overlay = pd.Series(False, index=gdf.index)

        main_gdf = gdf[mask_main]
        overlay_gdf = gdf[mask_overlay]
        sub_gdf = gdf[~mask_main & ~mask_overlay]

        # --- Kurze Übersicht ---
        print(f"[INFO] Hauptland: {len(main_gdf)}, Nebenländer: {len(sub_gdf)}, Overlay: {len(overlay_gdf)}")

        fig, ax, dpi = self._create_figure_and_axis()
        self._apply_background(ax)
        lw_grenze, lw_highlight = self._get_linewidths(dpi)

        # 1. Nebenländer
        self._plot_subcountries(ax, sub_gdf, lw_grenze)

        # 2. Bounding Box auf Hauptland setzen
        if not main_gdf.empty:
            self._set_bbox(ax, main_gdf)

        # 3. Hauptland
        self._plot_maincountry(ax, main_gdf, lw_grenze)

        # 4. Highlights
        self._plot_highlights(ax, main_gdf, lw_highlight)

        # 5. Overlay zuletzt – nur wenn vorhanden und nicht leer
        if not overlay_gdf.empty:
            style = self.cfg.get("overlay_style", {})
            lw = style.get("line_width", 1.0)
            overlay_gdf.plot(
                ax=ax,
                color=style.get("fill_color", "none"),
                edgecolor=style.get("line_color", "black")
                          if lw > 0 and style.get("show_lines", True)
                          else "none",
                linewidth=lw,
                zorder=5
            )

        # 6. Maßstabsleiste
        self._add_scalebar(ax, preview_mode=preview_mode, preview_scale=preview_scale)

        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        return fig

    # ------------------------------------------------------------
    # Datenquelle
    # ------------------------------------------------------------
    def _get_geodataframe(self):
        """Lädt oder verwendet vorhandenes GeoDataFrame."""
        if self._gdf is not None and not self._gdf.empty:
            return self._gdf

        return merge_hauptland_layers(
            self.main_gpkg,
            self.layers,
            hide_cfg=self.hide_cfg,
            hl_cfg=self.hl_cfg,
            crs=self.crs,
        )

    # ------------------------------------------------------------
    # Figure-Setup
    # ------------------------------------------------------------
    def _create_figure_and_axis(self):
        """Erstellt Figure und Achse mit korrekten Abmessungen."""
        dpi = self.cfg.get("export", {}).get("dpi", 300)
        fig_w = self.width_px / dpi
        fig_h = self.height_px / dpi
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        ax.set_axis_off()
        return fig, ax, dpi

    def _apply_background(self, ax):
        """Setzt Hintergrundfarbe, falls nicht transparent."""
        if not self.background.get("transparent", False):
            bg = self.background.get("color", "#ffffff")
            ax.figure.patch.set_facecolor(bg)
            ax.set_facecolor(bg)

    def _get_linewidths(self, dpi):
        """Berechnet Linienbreiten in Points."""
        lw_grenze = pixel_to_pt(self.lines_cfg.get("grenze_px", 1), dpi)
        lw_highlight = pixel_to_pt(self.lines_cfg.get("highlight_px", 1), dpi)
        return lw_grenze, lw_highlight

    # ------------------------------------------------------------
    # Plot-Methoden
    # ------------------------------------------------------------
    def _plot_subcountries(self, ax, sub_gdf, lw_grenze):
        """Zeichnet Nebenländer."""
        if not sub_gdf.empty:
            sub_gdf.plot(
                ax=ax,
                color=self.colors.get("nebenland", "lightgray"),
                edgecolor=self.colors.get("grenze", "gray"),
                linewidth=lw_grenze,
            )

    def _set_bbox(self, ax, main_gdf):
        """Setzt Bounding Box basierend auf Hauptland."""
        aspect = self.width_px / self.height_px
        bbox = compute_bbox(main_gdf, aspect)
        ax.set_xlim(bbox[0], bbox[1])
        ax.set_ylim(bbox[2], bbox[3])

    def _plot_maincountry(self, ax, main_gdf, lw_grenze):
        """Zeichnet Hauptland."""
        if not main_gdf.empty:
            main_gdf.plot(
                ax=ax,
                color=self.colors.get("hauptland", "white"),
                edgecolor=self.colors.get("grenze", "gray"),
                linewidth=lw_grenze,
            )

    def _plot_highlights(self, ax, main_gdf, lw_highlight):
        """Zeichnet Hervorhebungen."""
        if (
            self.hl_cfg.get("aktiv", False)
            and not main_gdf.empty
            and "highlight" in main_gdf.columns
            and main_gdf["highlight"].dtype == bool
        ):
            to_high = main_gdf[main_gdf["highlight"]]
            if not to_high.empty:
                to_high.plot(
                    ax=ax,
                    color=self.colors.get("highlight", "red"),
                    edgecolor=self.colors.get("grenze", "darkred"),
                    linewidth=lw_highlight,
                    zorder=3,
                )

    def _add_scalebar(self, ax, preview_mode: bool = False, preview_scale: float = 0.5):
        """Fügt Maßstabsleiste hinzu, falls aktiviert."""
        current = self.cfg.get("scalebar", {}) or {}
        scalebar_cfg = {**self._scalebar_defaults, **current}

        if scalebar_cfg.get("show", False):
            # Aktuelle Ausdehnung der Achse holen
            extent = [*ax.get_xlim(), *ax.get_ylim()]
            # Temporäre Config mit zusammengeführter Scalebar-Config
            tmp_cfg = {**self.cfg, "scalebar": scalebar_cfg}
            # Maßstabsleiste hinzufügen
            add_scalebar(
                ax,
                extent,
                self.crs,
                tmp_cfg,
                preview_mode=preview_mode,
                preview_scale=preview_scale
            )

    # ------------------------------------------------------------
    # Leere Figure
    # ------------------------------------------------------------
    def _empty_figure(self) -> plt.Figure:
        """Erstellt eine leere Figure (Platzhalter)."""
        fig, ax, _ = self._create_figure_and_axis()
        ax.text(
            0.5, 0.5,
            "Keine Daten",
            ha="center", va="center",
            fontsize=14,
            transform=ax.transAxes
        )
        return fig