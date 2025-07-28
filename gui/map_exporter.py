# gui/map_exporter.py

from pathlib import Path

class MapExporter:
    @staticmethod
    def save(fig, out, export_formats, transparent):
        """
        Speichert die Figur exakt in den vorgegebenen Pixelmaßen.

        out:
          - file-like Objekt → erstes Format aus export_formats
          - Pfad mit Extension → genau dieses Format
          - Pfad ohne Extension → alle export_formats
        """
        # export_formats kann ein Set oder andere Collection sein → in Liste wandeln
        fmt_list = list(export_formats)

        # 0) Achse auf volle Figure strecken
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        # 1) bbox_inches aus Achse berechnen (in Zoll)
        ax = fig.axes[0] if fig.axes else None
        bbox_inches = (
            ax.get_window_extent()
              .transformed(fig.dpi_scale_trans.inverted())
        ) if ax else None

        # 2) Helper-Funktion für savefig
        def _save(path, fmt):
            fig.savefig(
                path,
                format=fmt,
                transparent=transparent,
                dpi=fig.dpi,
                bbox_inches=bbox_inches,
                pad_inches=0
            )

        # 3) file-like?
        if hasattr(out, "write"):
            fmt = fmt_list[0]
            _save(out, fmt)
            return

        path = Path(out)

        # 4) Pfad mit Endung → genau dieses Format
        if path.suffix:
            path.parent.mkdir(parents=True, exist_ok=True)
            fmt = path.suffix.lstrip(".")
            _save(path, fmt)

        # 5) Pfad ohne Endung → alle Formate
        else:
            path.mkdir(parents=True, exist_ok=True)
            for fmt in fmt_list:
                fn = path / f"map.{fmt}"
                _save(fn, fmt)