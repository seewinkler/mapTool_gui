# plotting.py

import logging
from datetime import datetime
from pathlib import Path
from typing import Tuple, Dict, Set, Optional, List

import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from scalebar import add_scalebar

logger = logging.getLogger("mymaptool.plotting")


def pixel_to_pt(pixel: int, dpi: int) -> float:
    """
    Convert pixel units to points based on DPI.
    """
    return pixel * 72 / dpi


def plot_map(
    haupt_gdf,
    neben_gdfs: List,
    highlight_cfg: Dict[str, object],
    colors: Dict[str, str],
    bbox: Tuple[float, float, float, float],
    width_px: int,
    height_px: int,
    src_crs: str,
    label_text: Optional[str] = None,
    scalebar_cfg: Optional[Dict[str, object]] = None,
    background_cfg: Optional[Dict[str, object]] = None,
    linien_cfg: Optional[Dict[str, int]] = None
) -> Tuple[Figure, Axes]:
    """
    Render the map into a Matplotlib Figure and Axes.

    Returns:
        fig: the Matplotlib Figure object
        ax: the Matplotlib Axes object
    """
    dpi = 600
    figsize = (width_px / dpi, height_px / dpi)
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    
    # Background
    if background_cfg:
        bg_color = background_cfg.get("color", "#2896BA")
        bg_transp = background_cfg.get("transparent", False)
    else:
        bg_color = "none"
        bg_transp = True

    fig.patch.set_facecolor(bg_color)
    ax.set_facecolor(bg_color)
    fig.patch.set_alpha(0 if bg_transp else 1)
    ax.patch.set_alpha(0 if bg_transp else 1)

    # Line widths in points
    if linien_cfg:
        linewidth_grenze = pixel_to_pt(linien_cfg.get("grenze_px", 1), dpi)
        linewidth_highlight = pixel_to_pt(linien_cfg.get("highlight_px", 1), dpi)
    else:
        linewidth_grenze = pixel_to_pt(1, dpi)
        linewidth_highlight = pixel_to_pt(1, dpi)

    logger.debug(
        f"Linienstärken (pt): Grenze={linewidth_grenze:.2f}, "
        f"Highlight={linewidth_highlight:.2f}"
    )

    # Plot neighbouring countries
    for gdf in neben_gdfs:
        gdf.plot(
            ax=ax,
            color=colors["nebenland"],
            edgecolor=colors["grenze"],
            linewidth=linewidth_grenze
        )

    # Plot main country
    haupt_gdf.plot(
        ax=ax,
        color=colors["hauptland"],
        edgecolor=colors["grenze"],
        linewidth=linewidth_grenze
    )

    # Highlight regions
    if highlight_cfg.get("aktiv") and highlight_cfg.get("namen"):
        mask = haupt_gdf["NAME_1"].isin(highlight_cfg["namen"])
        haupt_gdf[mask].plot(
            ax=ax,
            color=colors["highlight"],
            edgecolor=colors["grenze"],
            linewidth=linewidth_highlight
        )

    # Set bounding box and remove axes
    xmin, xmax, ymin, ymax = bbox
    ax.set_xlim(xmin, xmax)
    ax.set_ylim(ymin, ymax)
    ax.axis("off")

    # Add scalebar if configured
    if scalebar_cfg and scalebar_cfg.get("show", False):
        extent = [*ax.get_xlim(), *ax.get_ylim()]
        add_scalebar(
            ax,
            extent,
            src_crs,
            label=label_text
        )
    else:
        logger.debug("Scalebar disabled or not configured.")

    return fig, ax


def save_map(
    fig: Figure,
    output_dir: Path,
    region: str,
    crs: str,
    width_px: int,
    height_px: int,
    export_formats: Set[str],
    background_cfg: Optional[Dict[str, object]] = None
) -> None:
    """
    Save the map figure to disk in specified formats.

    Dateiname: {region}_{crs}_{timestamp}.{ext}
    """
    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build filename base
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    base = f"{region}_{crs.replace(':', '_')}_{timestamp}"
    dpi = 600

    # Resize figure to match pixel dimensions
    fig.set_size_inches(width_px / dpi, height_px / dpi)
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    # Determine bbox_inches
    ax = fig.axes[0] if fig.axes else None
    if ax:
        bbox_inches = (
            ax.get_window_extent()
               .transformed(fig.dpi_scale_trans.inverted())
        )
    else:
        bbox_inches = None

    # Transparency setting
    transparent = True
    if background_cfg:
        transparent = background_cfg.get("transparent", False)

    # Save in requested formats
    for ext in export_formats:
        filepath = output_dir / f"{base}.{ext.lower()}"
        if ext.lower() == "png":
            fig.savefig(
                filepath,
                dpi=dpi,
                transparent=transparent,
                bbox_inches=bbox_inches,
                pad_inches=0
            )
        elif ext.lower() == "svg":
            fig.savefig(
                filepath,
                format="svg",
                bbox_inches=bbox_inches,
                pad_inches=0
            )
        else:
            logger.warning(f"Unbekanntes Format '{ext}' – übersprungen.")
            continue

        logger.info(f"Karte gespeichert: {filepath}")

    plt.close(fig)