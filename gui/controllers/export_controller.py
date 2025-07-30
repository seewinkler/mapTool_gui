# gui/controllers/export_controller.py

from pathlib import Path
from gui.map_composer import MapComposer

class ExportController:
    def __init__(self, composer: MapComposer, view, config: dict, parent):
        self.composer = composer
        self.view = view
        self.config = config
        self.parent = parent

    def render_clicked(self) -> None:
        # 1) Export-Formate sammeln
        formats = []
        if self.view.cb_png.isChecked():
            formats.append("png")
        if self.view.cb_svg.isChecked():
            formats.append("svg")
        self.composer.set_export_formats(formats)

        # 2) Abmessungen synchronisieren
        w = self.view.sp_w.value()
        h = self.view.sp_h.value()
        self.composer.set_dimensions(w, h)

        # 3) Speichern per Save-Dialog, öffnet danach den Ordner
        saved_path = self.composer.compose_and_save_dialog(
            parent=self.parent,
            initial_dir=self.config.get("output_dir", "output")
        )
        if saved_path:
            # Optional: zuletzt gewählten Ordner merken
            self.config["output_dir"] = str(saved_path.parent)

        # 4) Vorschau aktualisieren
        self.view.map_canvas.refresh()