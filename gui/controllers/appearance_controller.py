# gui/controllers/appearance_controller.py

import logging
from PySide6.QtWidgets import QColorDialog
from utils.config import config_manager



class AppearanceController:
    def __init__(self, composer, view, parent, main_ctrl=None):
        self.composer = composer
        self.view     = view
        self.parent   = parent
        self.main_ctrl = main_ctrl  # Referenz auf MainController (optional)
        self.session_config = config_manager.get_session()

    def choose_bg_color(self):
        col = QColorDialog.getColor(parent=self.parent)
        if not col.isValid():
            return

        # Composer updaten
        self.composer.set_background(color=col.name())
        # Canvas-Hintergrund setzen (nur optisch, kein Render)
        self.view.map_canvas.set_background(color=col.name())
        # Session-Config aktualisieren
        self.session_config.setdefault("background", {})["color"] = col.name()

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()

    def background_changed(self, state: int):
        transparent = bool(state)

        # Composer updaten
        self.composer.set_background(transparent=transparent)
        # Canvas-Hintergrund setzen (nur optisch, kein Render)
        self.view.map_canvas.set_background(transparent=transparent)
        # Session-Config aktualisieren
        self.session_config.setdefault("background", {})["transparent"] = transparent

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()
