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

def add_scalebar(ax, extent, src_crs, config,
                 preview_mode: bool = False, preview_scale: float = 0.5):
    """
    Zeichnet eine dynamisch skalierte Scalebar in Achsenkoordinaten.

    - extent: [xmin, xmax, ymin, ymax] in Daten-Koordinaten
    - src_crs: CRS-String oder EPSG-Code der Daten
    - config: gesamtes Config-Dict (enthält scalebar- und karte-Sektion)
    - preview_mode: True = Vorschau, False = finale Ausgabe
    - preview_scale: Verhältnis Vorschaugröße zu finaler Größe (z. B. 0.5 bei halber Pixelzahl)

    Ziel: Vorschau und finale Ausgabe sollen optisch identisch wirken.
    Daher werden Länge, Padding und Position gegen die Referenzgröße (final) berechnet.
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
    if map_width_m <= 0:
        return

    # 2) Achsenabmessungen in Pixel (aktuell gerenderte Größe)
    fig  = ax.figure
    bbox = ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
    axes_w_px_cur = max(1.0, bbox.width  * fig.dpi)
    axes_h_px_cur = max(1.0, bbox.height * fig.dpi)

    # 3) Referenzgröße (finale Ausgabe) ableiten
    # Im Preview ist die aktuelle Größe um preview_scale kleiner → normiere zurück.
    safe_scale = preview_scale if (preview_mode and preview_scale > 0) else 1.0
    axes_w_px_ref = axes_w_px_cur / safe_scale
    axes_h_px_ref = axes_h_px_cur / safe_scale

    # 4) Roh-Pixel-Länge (in Referenzpixeln) & clamp zwischen min/max
    frac_cfg = scalebar_cfg.get("length_fraction", 0.07)
    raw_px_ref = frac_cfg * axes_w_px_ref

    min_px   = scalebar_cfg.get("min_length_px", 50)
    max_px   = scalebar_cfg.get("max_length_px", 200)
    target_px_ref = max(min(raw_px_ref, max_px), min_px)

    # 5) Referenz-Pixel-Länge -> Meter -> „schöne“ Länge -> Fraktion der Kartenbreite
    # Wichtig: Division durch Referenzbreite, damit Preview und Final identisch wirken.
    target_m   = (target_px_ref / axes_w_px_ref) * map_width_m
    nice_len_m = nice_number(target_m)
    if nice_len_m <= 0:
        return
    frac_nice  = nice_len_m / map_width_m

    # 6) Label (m oder km)
    if nice_len_m >= 1000:
        label = f"{int(round(nice_len_m/1000))} km"
    else:
        label = f"{int(round(nice_len_m))} m"

    # 7) Stift- und Schriftgrößen in pt (physisch konsistent)
    dpi      = fig.dpi or scalebar_cfg.get("dpi", 72)
    lw_px    = scalebar_cfg.get("linewidth_px", 1.5)
    font_px  = scalebar_cfg.get("font_px", 16)
    lw_pt    = pixel_to_pt(lw_px, dpi)
    font_pt  = pixel_to_pt(font_px, dpi)
    color    = scalebar_cfg.get("color", "black")
    tick_frac = scalebar_cfg.get("tick_fraction", 0.05)

    # 8) Padding als Anteil der Referenzgröße, damit optischer Randabstand gleich bleibt
    pad_px   = scalebar_cfg.get("padding_px", 20)
    pad_x    = pad_px / axes_w_px_ref
    pad_y    = pad_px / axes_h_px_ref

    # 9) Position in Achsen-Koordinaten wählen
    pos_map = {
        "bottom-left":   (0.05, 0.05),
        "bottom-center": (0.50, 0.05),
        "bottom-right":  (0.95, 0.05),
        "top-left":      (0.05, 0.95),
        "top-center":    (0.50, 0.95),
        "top-right":     (0.95, 0.95),
    }
    x0, y0 = pos_map.get(scalebar_cfg.get("position", "bottom-right"), (0.05, 0.05))

    # 10) Randabstand und Überlauf korrigieren (auf Basis der Referenz-Padding-Anteile)
    if x0 + frac_nice > 1.0 - pad_x:
        x0 = 1.0 - frac_nice - pad_x
    if x0 < pad_x:
        x0 = pad_x
    if y0 < pad_y:
        y0 = pad_y
    if y0 > 1.0 - pad_y:
        y0 = 1.0 - pad_y

    # 11) Zeichnen
    ax.plot(
        [x0, x0 + frac_nice],
        [y0, y0],
        transform=ax.transAxes,
        color=color,
        linewidth=lw_pt,
        solid_capstyle="butt",
        zorder=5
    )

    # 12) End-Ticks
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

    # 13) Beschriftung
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