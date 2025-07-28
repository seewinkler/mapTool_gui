import matplotlib.pyplot as plt
from typing import Optional, List, Dict, Any
from data_processing.layers import merge_hauptland_layers
from data_processing.crs import compute_bbox
from utils.scalebar import add_scalebar

def pixel_to_pt(px, dpi):
    return px * 72.0 / dpi

class MapBuilder:
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

        # 1) Karte-Grundparameter
        karte = cfg.get("karte", {})
        self.width_px  = karte.get("breite", 800)
        self.height_px = karte.get("hoehe", 600)

        # 2) Sonstige Sektionen
        self.hide_cfg  = hide_cfg or cfg.get("ausblenden", {})
        self.hl_cfg    = hl_cfg   or cfg.get("hervorhebung", {})
        self.background = cfg.get("background", {})
        self.colors     = cfg.get("farben", {})
        self.lines_cfg  = cfg.get("linien", {})

        # 3) ORIGINAL Scalebar-Defaults sichern
        #    (damit sie nicht verloren gehen, wenn GUI nur position setzt)
        self._scalebar_defaults = cfg.get("scalebar", {}).copy()

    def build_figure(self) -> plt.Figure:
        # Datenquelle
        if self._gdf is not None and not self._gdf.empty:
            gdf = self._gdf
        else:
            gdf = merge_hauptland_layers(
                self.main_gpkg,
                self.layers,
                hide_cfg=self.hide_cfg,
                hl_cfg=self.hl_cfg,
                crs=self.crs,
            )

        if gdf is None or gdf.empty:
            return self._empty_figure()

        main_gdf = gdf[gdf["__is_main"]]
        sub_gdf  = gdf[~gdf["__is_main"]]

        # Figure + Achse
        dpi   = self.cfg.get("export", {}).get("dpi", 300)
        fig_w = self.width_px  / dpi
        fig_h = self.height_px / dpi
        fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=dpi)
        ax.set_axis_off()

        # Hintergrund
        if not self.background.get("transparent", False):
            bg = self.background.get("color", "#ffffff")
            fig.patch.set_facecolor(bg)
            ax.set_facecolor(bg)

        # Linien-Breiten
        lw_grenze    = pixel_to_pt(self.lines_cfg.get("grenze_px", 1), dpi)
        lw_highlight = pixel_to_pt(self.lines_cfg.get("highlight_px", 1), dpi)

        # Nebenländer
        sub_gdf.plot(
            ax=ax,
            color=self.colors.get("nebenland", "lightgray"),
            edgecolor=self.colors.get("grenze",   "gray"),
            linewidth=lw_grenze,
        )

        # Bounding Box
        aspect = self.width_px / self.height_px
        bbox   = compute_bbox(main_gdf, aspect)
        ax.set_xlim(bbox[0], bbox[1])
        ax.set_ylim(bbox[2], bbox[3])

        # Hauptland
        main_gdf.plot(
            ax=ax,
            color=self.colors.get("hauptland", "white"),
            edgecolor=self.colors.get("grenze",    "gray"),
            linewidth=lw_grenze,
        )

        # Hervorhebungen
        if self.hl_cfg.get("aktiv", False) and "highlight" in main_gdf:
            to_high = main_gdf[main_gdf["highlight"]]
            if not to_high.empty:
                to_high.plot(
                    ax=ax,
                    color=self.colors.get("highlight",    "red"),
                    edgecolor=self.colors.get("grenze",   "darkred"),
                    linewidth=lw_highlight,
                    zorder=3,
                )

        # Scalebar: Defaults + aktueller GUI-State
        current = self.cfg.get("scalebar", {}) or {}
        # Mergen, current überschreibt nur spezifizierte Keys
        scalebar_cfg = {**self._scalebar_defaults, **current}

        # DEBUG-Ausgabe, damit du siehst, was tatsächlich gemergt wurde
        print("DEBUG Scalebar Config gemerged:", scalebar_cfg)

        if scalebar_cfg.get("show", False):
            extent = [*ax.get_xlim(), *ax.get_ylim()]
            # Wir geben scalebar_cfg jetzt als Teil von self.cfg weiter,
            # damit add_scalebar den gleichen Dict nutzt:
            tmp_cfg = {**self.cfg, "scalebar": scalebar_cfg}
            add_scalebar(ax, extent, self.crs, tmp_cfg)

        # Layout exakt wie save_map
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
        return fig

    def _empty_figure(self):
        fig = plt.figure(figsize=(self.width_px / 100, self.height_px / 100))
        fig.text(0.5, 0.5, "Keine Daten vorhanden", ha="center", va="center")
        return fig