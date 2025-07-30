# scalebar.py

import numpy as np
from pyproj import CRS, Transformer

def pixel_to_pt(px: float, dpi: float) -> float:
    """
    Wandelt Pixel in Punkt (pt) um: 1 pt = 1/72 inch.
    """
    return px * 72.0 / dpi

def nice_number(x: float) -> float:
    """
    Rundet x auf eine „schöne“ Zahl (1, 2, 5 × 10^n).
    """
    if x <= 0:
        return 0
    exp = np.floor(np.log10(x))
    f   = x / 10**exp
    if f < 1.5:   nice_f = 1
    elif f < 3:   nice_f = 2
    elif f < 7:   nice_f = 5
    else:         nice_f = 10
    return nice_f * 10**exp

def add_scalebar(ax, extent, src_crs, config):
    """
    Zeichnet eine dynamisch skalierte Scalebar in Achsenkoordinaten.
    extent: [xmin, xmax, ymin, ymax] in Daten-Koordinaten
    src_crs: CRS-String oder EPSG-Code der Daten
    config: gesamtes Config-Dict (enthält scalebar- und karte-Sektion)
    """
    scalebar_cfg = config.get("scalebar", {})
    if not scalebar_cfg.get("show", False):
        return

    # 1) Kartenbreite in Meter berechnen
    crs_obj = CRS.from_user_input(src_crs)
    if crs_obj.is_geographic:
        transformer = Transformer.from_crs(crs_obj, "EPSG:3857", always_xy=True)
        xmin_m, ymin_m = transformer.transform(extent[0], extent[2])
        xmax_m, ymax_m = transformer.transform(extent[1], extent[3])
    else:
        xmin_m, xmax_m, ymin_m, ymax_m = extent
    map_width_m = xmax_m - xmin_m

    # 2) Achsenabmessungen in Pixel
    fig  = ax.figure
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    axes_w_px = bbox.width  * fig.dpi
    axes_h_px = bbox.height * fig.dpi

    # 3) Roh-Pixel-Länge & clamp zwischen min/max
    frac_cfg = scalebar_cfg.get("length_fraction", 0.07)
    raw_px   = frac_cfg * axes_w_px
    min_px   = scalebar_cfg.get("min_length_px", 50)
    max_px   = scalebar_cfg.get("max_length_px", 200)
    target_px = max(min(raw_px, max_px), min_px)

    # 4) Zurück in Meter + „schöne“ Länge finden
    target_m  = (target_px / axes_w_px) * map_width_m
    nice_len_m = nice_number(target_m)
    frac_nice  = nice_len_m / map_width_m

    # 5) Label (m oder km)
    if nice_len_m >= 1000:
        label = f"{int(nice_len_m/1000)} km"
    else:
        label = f"{int(nice_len_m)} m"

    # 6) Stift- und Schriftgrößen in pt
    dpi      = fig.dpi or scalebar_cfg.get("dpi", 72)
    lw_px    = scalebar_cfg.get("linewidth_px", 1.5)
    font_px  = scalebar_cfg.get("font_px", 16)
    lw_pt    = pixel_to_pt(lw_px, dpi)
    font_pt  = pixel_to_pt(font_px, dpi)
    color    = scalebar_cfg.get("color", "black")
    tick_frac = scalebar_cfg.get("tick_fraction", 0.05)
    pad_px   = scalebar_cfg.get("padding_px", 20)
    pad_x    = pad_px / axes_w_px
    pad_y    = pad_px / axes_h_px

    # 7) Position in Achsen-Koordinaten wählen
    pos_map = {
        "bottom-left":   (0.05, 0.05),
        "bottom-center": (0.50, 0.05),
        "bottom-right":  (0.95, 0.05),
        "top-left":      (0.05, 0.95),
        "top-center":    (0.50, 0.95),
        "top-right":     (0.95, 0.95),
    }
    x0, y0 = pos_map.get(scalebar_cfg.get("position", "bottom-right"),
                         (0.05, 0.05))

    # 8) Randabstand und Überlauf korrigieren
    if x0 + frac_nice > 1.0 - pad_x:
        x0 = 1.0 - frac_nice - pad_x
    if x0 < pad_x:
        x0 = pad_x
    if y0 < pad_y:
        y0 = pad_y
    if y0 > 1.0 - pad_y:
        y0 = 1.0 - pad_y

    # 9) Zeichnen: Linie
    ax.plot(
        [x0, x0 + frac_nice],
        [y0, y0],
        transform=ax.transAxes,
        color=color,
        linewidth=lw_pt,
        solid_capstyle="butt",
        zorder=5
    )

    # 10) End-Ticks
    tick_h = tick_frac * frac_nice
    for xx in (x0, x0 + frac_nice):
        ax.plot(
            [xx, xx],
            [y0, y0 + tick_h],
            transform=ax.transAxes,
            color=color,
            linewidth=lw_pt,
            zorder=5
        )

    # 11) Beschriftung
    ax.text(
        x0 + frac_nice / 2,
        y0 + tick_h * 1.5,
        label,
        transform=ax.transAxes,
        ha="center",
        va="bottom",
        fontsize=font_pt,
        color=color,
        zorder=5
    )