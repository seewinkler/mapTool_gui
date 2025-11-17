# gui/controllers/export_controller.py

from pathlib import Path
from gui.map_composer import MapComposer
from utils.config import config_manager

class ExportController:
    def __init__(self, composer: MapComposer, view, parent, main_ctrl=None):
        """
        :param composer: MapComposer-Instanz
        :param view: MainWindow-Instanz
        :param parent: Parent-Widget für Dialoge
        :param main_ctrl: Optionaler Verweis auf MainController
        """
        self.composer = composer
        self.view = view
        self.parent = parent
        self.main_ctrl = main_ctrl
        self.session_config = config_manager.get_session()

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
        initial_dir = self.session_config.get("output_dir", "output")
        saved_path = self.composer.compose_and_save_dialog(
            parent=self.parent,
            initial_dir=initial_dir
        )
        if saved_path:
            # Optional: zuletzt gewählten Ordner merken
            self.session_config["output_dir"] = str(saved_path.parent)

        # 4) Kein automatischer Vorschau-Refresh mehr
        #    Stattdessen Dirty-Flag zurücksetzen, da Export auf finalen Daten basiert
        if self.main_ctrl and hasattr(self.main_ctrl, "preview_dirty"):
            self.main_ctrl.preview_dirty = False
            if hasattr(self.main_ctrl.view, "set_preview_dirty_indicator"):
                try:
                    self.main_ctrl.view.set_preview_dirty_indicator(False)
                except Exception:
                    pass