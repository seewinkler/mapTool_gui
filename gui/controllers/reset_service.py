import logging
from utils.config import config_manager

class ResetService:
    def __init__(self, composer, view):
        self.composer = composer
        self.view = view

    def reset(self):
        logging.info("Anwendung wird zurückgesetzt...")

        try:
            # Session-Config zurücksetzen
            config_manager.reset_session()
            session_cfg = config_manager.get_session()  # Neue Session-Config nach Reset

            # Composer-Zustand zurücksetzen
            if hasattr(self.composer, "main_gpkg"):
                self.composer.main_gpkg = None
            if hasattr(self.composer, "sub_gpkgs"):
                self.composer.sub_gpkgs = []

            # Dimensionen aus Session-Config
            karte_cfg = session_cfg.get("karte", {})
            w = karte_cfg.get("breite", getattr(self.composer, "width_px", 800))
            h = karte_cfg.get("hoehe", getattr(self.composer, "height_px", 600))
            if hasattr(self.composer, "set_dimensions"):
                self.composer.set_dimensions(w, h)

            # Hintergrund
            bg = session_cfg.get("background", {"color": "#ffffff", "transparent": False})
            if hasattr(self.composer, "set_background"):
                self.composer.set_background(color=bg.get("color"), transparent=bg.get("transparent"))

            # Scalebar
            sb = session_cfg.get("scalebar", {"show": False})
            if hasattr(self.composer, "set_scalebar"):
                self.composer.set_scalebar(sb)

            # Layer-/Filter-Configs
            if hasattr(self.composer, "set_primary_layers"):
                self.composer.set_primary_layers(session_cfg.get("primary_layers", []))
            if hasattr(self.composer, "set_hide"):
                self.composer.set_hide({})
            if hasattr(self.composer, "set_highlight"):
                self.composer.set_highlight(layer=None, names=[])

            # Dropzones leeren
            if hasattr(self.view, "drop_panel") and hasattr(self.view.drop_panel, "clear"):
                self.view.drop_panel.clear()

            # Listen leeren
            if hasattr(self.view, "lst_layers"):
                self.view.lst_layers.clear()
            if hasattr(self.view, "lst_hide"):
                self.view.lst_hide.clear()
            if hasattr(self.view, "lst_high"):
                self.view.lst_high.clear()

            # Dimensionen-Controls
            if hasattr(self.view, "sp_w"):
                self.view.sp_w.blockSignals(True)
                self.view.sp_w.setValue(w)
                self.view.sp_w.blockSignals(False)
            if hasattr(self.view, "sp_h"):
                self.view.sp_h.blockSignals(True)
                self.view.sp_h.setValue(h)
                self.view.sp_h.blockSignals(False)

            # Scalebar-Controls
            if hasattr(self.view, "cb_sb_show"):
                self.view.cb_sb_show.blockSignals(True)
                self.view.cb_sb_show.setChecked(bool(sb.get("show", False)))
                self.view.cb_sb_show.blockSignals(False)
            if hasattr(self.view, "cmb_sb_pos") and "position" in sb:
                self.view.cmb_sb_pos.blockSignals(True)
                self.view.cmb_sb_pos.setCurrentText(sb["position"])
                self.view.cmb_sb_pos.blockSignals(False)

            # Hintergrund-Controls
            if hasattr(self.view, "cb_transp"):
                self.view.cb_transp.blockSignals(True)
                self.view.cb_transp.setChecked(bool(bg.get("transparent", False)))
                self.view.cb_transp.blockSignals(False)

            # Leere Karte anzeigen
            if hasattr(self.view, "map_canvas"):
                try:
                    self.view.map_canvas.refresh(preview=True)
                except Exception as e:
                    logging.error("Fehler beim Leeren der Karte: %s", e)

            logging.info("Zurücksetzen abgeschlossen.")
            return True

        except Exception as e:
            logging.error("Fehler beim Zurücksetzen: %s", e)
            return False