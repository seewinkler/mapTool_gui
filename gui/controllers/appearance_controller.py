# gui/controllers/appearance_controller.py

import logging
from PySide6.QtWidgets import QColorDialog
from utils.config import save_config

class AppearanceController:
    def __init__(self, composer, view, config, parent, main_ctrl=None):
        self.composer = composer
        self.view     = view
        self.config   = config
        self.parent   = parent
        self.main_ctrl = main_ctrl  # Referenz auf MainController (optional)

    def choose_bg_color(self):
        col = QColorDialog.getColor(parent=self.parent)
        if not col.isValid():
            return

        # Composer updaten
        self.composer.set_background(color=col.name())
        # Canvas-Hintergrund setzen (nur optisch, kein Render)
        self.view.map_canvas.set_background(color=col.name())
        # persistent speichern
        self.config["background"]["color"] = col.name()
        save_config(self.config)

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()

    def background_changed(self, state: int):
        transparent = bool(state)

        # Composer updaten
        self.composer.set_background(transparent=transparent)
        # Canvas-Hintergrund setzen (nur optisch, kein Render)
        self.view.map_canvas.set_background(transparent=transparent)
        # persistent speichern
        self.config["background"]["transparent"] = transparent
        save_config(self.config)

        # Vorschau nur als "dirty" markieren
        if self.main_ctrl:
            self.main_ctrl.mark_preview_dirty()
