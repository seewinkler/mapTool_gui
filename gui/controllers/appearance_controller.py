# gui/controllers/appearance_controller.py

import logging
from PySide6.QtWidgets import QColorDialog
from utils.config        import save_config

class AppearanceController:
    def __init__(self, composer, view, config, parent):
        self.composer = composer
        self.view     = view
        self.config   = config
        self.parent   = parent

    def choose_bg_color(self):
        col = QColorDialog.getColor(parent=self.parent)
        if not col.isValid():
            return

        # Composer updaten
        self.composer.set_background(color=col.name())
        # Canvas updaten
        self.view.map_canvas.set_background(color=col.name())
        # persistent speichern
        self.config["background"]["color"] = col.name()
        save_config(self.config)

        self.view.map_canvas.refresh()

    def background_changed(self, state: int):
        transparent = bool(state)

        # Composer updaten
        self.composer.set_background(transparent=transparent)
        # Canvas updaten
        self.view.map_canvas.set_background(transparent=transparent)
        # persistent speichern
        self.config["background"]["transparent"] = transparent
        save_config(self.config)

        self.view.map_canvas.refresh()