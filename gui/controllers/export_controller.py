from io import BytesIO
from PySide6.QtWidgets import QFileDialog

class ExportController:
    def __init__(self, composer, view, config, parent):
        self.composer = composer
        self.view = view
        self.config = config
        self.parent = parent

    def render_clicked(self):
        # Formate setzen
        formats = []
        if self.view.cb_png.isChecked():
            formats.append("png")
        if self.view.cb_svg.isChecked():
            formats.append("svg")
        self.composer.set_export_formats(formats)

        # Aktuelle Dimensionen synchronisieren
        w = self.view.sp_w.value()
        h = self.view.sp_h.value()
        self.composer.set_dimensions(w, h)

        # Ausgabeordner wählen
        out_dir = QFileDialog.getExistingDirectory(
            self.parent,
            "Ausgabeordner wählen",
            self.config.get("output_dir", "output")
        )
        if not out_dir:
            return

        # Für jeden gewählten Format jeweils in eine Datei speichern
        for fmt in formats:
            filename = f"{out_dir}/karte.{fmt}"
            # MapExporter unterstützt Dateiobjekte; wir nutzen einen BytesIO-Umweg
            buffer = BytesIO()
            self.composer.compose_and_save(buffer)
            with open(filename, "wb") as f:
                f.write(buffer.getvalue())

        # Vorschau aktualisieren
        self.view.map_canvas.refresh()