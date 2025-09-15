# gui/map_exporter.py

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional, Union, List, IO

from PySide6.QtWidgets import QFileDialog


class MapExporter:
    """
    Verantwortlich für das Speichern von Matplotlib-Figures
    in verschiedenen Formaten und das Öffnen des Zielordners.
    """

    # ------------------------------------------------------------
    # Öffentliche Methoden
    # ------------------------------------------------------------
    @staticmethod
    def save(fig, out: Union[str, Path, IO], export_formats: List[str], transparent: bool) -> None:
        """
        Speichert eine Matplotlib-Figure exakt in den vorgegebenen Pixelmaßen.

        Parameter:
        - fig: Matplotlib-Figure
        - out: file-like Objekt, Pfad mit Extension oder Pfad ohne Extension
        - export_formats: Liste der Formate (z. B. ["png", "svg"])
        - transparent: Hintergrund transparent speichern
        """
        fmt_list = list(export_formats)

        # Figure-Rand entfernen
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # Bounding Box berechnen
        bbox_inches = MapExporter._get_bbox_inches(fig)

        # Speichern je nach Zieltyp
        if hasattr(out, "write"):
            MapExporter._save_single(fig, out, fmt_list[0], transparent, bbox_inches)
        else:
            MapExporter._save_to_path(fig, Path(out), fmt_list, transparent, bbox_inches)

    @staticmethod
    def save_with_dialog(
        fig,
        export_formats: List[str],
        transparent: bool,
        parent=None,
        initial_dir: str = "output"
    ) -> Optional[Path]:
        """
        Öffnet Save-As-Dialog im initial_dir, speichert die Figure und öffnet den Ordner.
        Gibt den Pfad zur Datei oder None zurück.
        """
        out_dir = Path(initial_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        fmt_list = list(export_formats)
        filter_str = MapExporter._build_file_filter(fmt_list)
        default_fp = out_dir / f"map.{fmt_list[0]}"

        filename, _ = QFileDialog.getSaveFileName(
            parent,
            "Karte speichern",
            str(default_fp),
            filter_str
        )
        if not filename:
            return None

        # Speichern
        MapExporter.save(fig, filename, export_formats, transparent)

        # Zielordner im OS-Explorer öffnen
        MapExporter._open_folder(Path(filename).parent)

        return Path(filename)

    # ------------------------------------------------------------
    # Private Hilfsmethoden
    # ------------------------------------------------------------
    @staticmethod
    def _get_bbox_inches(fig):
        """Berechnet die Bounding Box der Figure."""
        ax = fig.axes[0] if fig.axes else None
        if not ax:
            return None
        return ax.get_window_extent().transformed(fig.dpi_scale_trans.inverted())

    @staticmethod
    def _save_single(fig, target, fmt: str, transparent: bool, bbox_inches) -> None:
        """Speichert Figure in ein einzelnes Ziel (file-like oder Pfad)."""
        fig.savefig(
            target,
            format=fmt,
            transparent=transparent,
            dpi=fig.dpi,
            bbox_inches=bbox_inches,
            pad_inches=0
        )

    @staticmethod
    def _save_to_path(fig, path: Path, fmt_list: List[str], transparent: bool, bbox_inches) -> None:
        """Speichert Figure in eine Datei oder mehrere Formate in einem Ordner."""
        if path.suffix:
            # Einzeldatei
            path.parent.mkdir(parents=True, exist_ok=True)
            MapExporter._save_single(fig, path, path.suffix.lstrip("."), transparent, bbox_inches)
        else:
            # Ordner + alle Formate
            path.mkdir(parents=True, exist_ok=True)
            for fmt in fmt_list:
                fn = path / f"map.{fmt}"
                MapExporter._save_single(fig, fn, fmt, transparent, bbox_inches)

    @staticmethod
    def _build_file_filter(fmt_list: List[str]) -> str:
        """Erstellt den Filterstring für den QFileDialog."""
        pattern = " ".join(f"*.{fmt}" for fmt in fmt_list)
        return f"Map-Dateien ({pattern})"

    @staticmethod
    def _open_folder(folder: Path) -> None:
        """Öffnet einen Ordner im nativen Dateimanager."""
        if sys.platform.startswith("darwin"):
            subprocess.call(["open", str(folder)])
        elif os.name == "nt":
            os.startfile(str(folder))
        else:
            subprocess.call(["xdg-open", str(folder)])