# gui/map_exporter.py

import os
import sys
import subprocess
from pathlib import Path
from typing import Optional

from PySide6.QtWidgets import QFileDialog


class MapExporter:
    @staticmethod
    def save(fig, out, export_formats, transparent: bool):
        """
        Speichert eine Matplotlib-Figure exakt in den vorgegebenen Pixelmaßen.

        out:
          - file-like → erstes Format
          - Pfad mit Extension → genau dieses Format
          - Pfad ohne Extension → alle Formate
        """
        fmt_list = list(export_formats)

        # Figure-Rand entfernen
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # bbox_inches berechnen
        ax = fig.axes[0] if fig.axes else None
        bbox_inches = (
            ax.get_window_extent()
              .transformed(fig.dpi_scale_trans.inverted())
        ) if ax else None

        def _save(path, fmt):
            fig.savefig(
                path,
                format=fmt,
                transparent=transparent,
                dpi=fig.dpi,
                bbox_inches=bbox_inches,
                pad_inches=0
            )

        # file-like?
        if hasattr(out, "write"):
            _save(out, fmt_list[0])
            return

        path = Path(out)
        if path.suffix:
            # Einzeldatei
            path.parent.mkdir(parents=True, exist_ok=True)
            _save(path, path.suffix.lstrip("."))
        else:
            # Ordner + alle Formate
            path.mkdir(parents=True, exist_ok=True)
            for fmt in fmt_list:
                fn = path / f"map.{fmt}"
                _save(fn, fmt)

    @staticmethod
    def save_with_dialog(
        fig,
        export_formats,
        transparent: bool,
        parent=None,
        initial_dir: str = "output"
    ) -> Optional[Path]:
        """
        Öffnet Save-As-Dialog im initial_dir,
        speichert die Figure und öffnet den Ordner.
        Gibt den Pfad zur Datei oder None zurück.
        """
        out_dir = Path(initial_dir)
        out_dir.mkdir(parents=True, exist_ok=True)

        fmt_list = list(export_formats)
        pattern = " ".join(f"*.{fmt}" for fmt in fmt_list)
        filter_str = f"Map-Dateien ({pattern})"
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

        # Ordner im OS-Explorer öffnen
        folder = Path(filename).parent
        if sys.platform.startswith("darwin"):
            subprocess.call(["open", str(folder)])
        elif os.name == "nt":
            os.startfile(str(folder))
        else:
            subprocess.call(["xdg-open", str(folder)])

        return Path(filename)