# gui/controllers/settings_controller.py


class SettingsController:
    def __init__(self, composer, view, config, main_ctrl=None):
        """
        :param composer: MapComposer-Instanz
        :param view: MainWindow-Instanz
        :param config: Config-Dict
        :param main_ctrl: Optionaler Verweis auf MainController
        """
        self.composer = composer
        self.view     = view
        self.config   = config
        self.main_ctrl = main_ctrl

    def handle_dimensions_changed(self):
        w = self.view.sp_w.value()
        h = self.view.sp_h.value()
        self.composer.set_dimensions(w, h)

        # Kein sofortiger Refresh mehr – nur als 'dirty' markieren
        if self.main_ctrl and hasattr(self.main_ctrl, "mark_preview_dirty"):
            self.main_ctrl.mark_preview_dirty()

    def handle_scalebar_changed(self):
        show     = self.view.cb_sb_show.isChecked()
        position = self.view.cmb_sb_pos.currentText()

        sb_cfg = self.config.get("scalebar", {}).copy()
        sb_cfg.update({"show": show, "position": position})

        try:
            self.composer.set_scalebar(sb_cfg)
        except AttributeError:
            self.composer.cfg["scalebar"] = sb_cfg

        self.config["scalebar"] = sb_cfg

        # Kein sofortiger Refresh mehr – nur als 'dirty' markieren
        if self.main_ctrl and hasattr(self.main_ctrl, "mark_preview_dirty"):
            self.main_ctrl.mark_preview_dirty()