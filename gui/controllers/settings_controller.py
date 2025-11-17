# gui/controllers/settings_controller.py

from utils.config import config_manager

class SettingsController:
    def __init__(self, composer, view, main_ctrl=None):
        """
        :param composer: MapComposer-Instanz
        :param view: MainWindow-Instanz
        :param main_ctrl: Optionaler Verweis auf MainController
        """
        self.composer = composer
        self.view = view
        self.main_ctrl = main_ctrl
        self.session_config = config_manager.get_session()

    def handle_dimensions_changed(self):
        w = self.view.sp_w.value()
        h = self.view.sp_h.value()

        # Composer aktualisieren
        self.composer.set_dimensions(w, h)

        # Session-Config aktualisieren
        self.session_config.setdefault("karte", {})["breite"] = w
        self.session_config.setdefault("karte", {})["hoehe"] = h

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl and hasattr(self.main_ctrl, "mark_preview_dirty"):
            self.main_ctrl.mark_preview_dirty()

    def handle_scalebar_changed(self):
        show = self.view.cb_sb_show.isChecked()
        position = self.view.cmb_sb_pos.currentText()

        # Fallbacks aus Session-Config
        sb_cfg = self.session_config.get("scalebar", {}).copy()
        sb_cfg.update({"show": show, "position": position})

        # Composer synchronisieren
        try:
            self.composer.set_scalebar(sb_cfg)
        except AttributeError:
            # Falls Composer keine Methode hat, direkt in seine Config schreiben
            self.composer.cfg["scalebar"] = sb_cfg

        # Session-Config aktualisieren
        self.session_config["scalebar"] = sb_cfg

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl and hasattr(self.main_ctrl, "mark_preview_dirty"):
            self.main_ctrl.mark_preview_dirty()