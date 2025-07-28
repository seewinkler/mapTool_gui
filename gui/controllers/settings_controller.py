# gui/controllers/settings_controller.py

from utils.config import save_config

class SettingsController:
    def __init__(self, composer, view, config):
        self.composer = composer
        self.view     = view
        self.config   = config

    def handle_dimensions_changed(self):
        w = self.view.sp_w.value()
        h = self.view.sp_h.value()
        self.composer.set_dimensions(w, h)
        self.view.map_canvas.refresh()

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
        save_config(self.config)
        self.view.map_canvas.refresh()